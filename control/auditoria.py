"""Motor de auditoría.

Dos fuentes de registros:
  1. AUTOMÁTICA (señales): altas, ediciones (con antes/después campo por campo) y bajas de los datos
     maestros: productos, categorías, marcas, clientes, proveedores, usuarios, roles y permisos.
  2. EXPLÍCITA: ``registrar(...)`` para operaciones de negocio (ventas, compras, pedidos, inicios de
     sesión, informes...). Se llama después de que la operación tuvo éxito.

Auditar NUNCA debe romper la operación principal: todo error se captura y se registra en el log.
"""
import datetime
import json
import logging
from decimal import Decimal

from django.apps import apps
from django.db.models.signals import post_delete, post_save, pre_save
from django.utils import timezone

from . import contexto

logger = logging.getLogger(__name__)

# tabla -> (etiqueta del objeto, módulo, función que da su nombre legible)
TABLAS = {
    'productos': ('Producto', 'productos', lambda o: getattr(o, 'nombre_producto', '')),
    'categorias': ('Categoría', 'productos', lambda o: getattr(o, 'nombre_categoria', '')),
    'marcas': ('Marca', 'productos', lambda o: getattr(o, 'nombre_marca', '')),
    'clientes': ('Cliente', 'clientes', lambda o: f"{getattr(o, 'nombres', '')} {getattr(o, 'apellidos', '')}".strip()),
    'proveedores': ('Proveedor', 'proveedores', lambda o: getattr(o, 'nombre_proveedor', '')),
    'usuarios': ('Usuario', 'usuarios', lambda o: getattr(o, 'nombre_usuario', '')),
    'roles': ('Rol', 'usuarios', lambda o: getattr(o, 'nombre_rol', '')),
    'permisos': ('Permisos', 'usuarios', lambda o: f'#{o.pk}'),
}

CAMPOS = {
    'nombre_producto': 'Nombre', 'descripcion': 'Descripción', 'cantidad': 'Existencias', 'fechaven': 'Vencimiento',
    'sabor': 'Sabor', 'presentacion': 'Presentación', 'estado': 'Estado', 'precio': 'Precio de compra',
    'precio_pub': 'Precio al público', 'iProductImg': 'Imagen', 'iInfoImg': 'Imagen nutricional',
    'id_categoria_id': 'Categoría', 'id_marca_id': 'Marca', 'id_municipio_id': 'Municipio', 'id_rol_id': 'Rol',
    'nombre_categoria': 'Nombre', 'nombre_marca': 'Nombre', 'documento': 'Documento', 'nombres': 'Nombres',
    'apellidos': 'Apellidos', 'celular': 'Celular', 'barrio': 'Barrio', 'direccion': 'Dirección', 'correo': 'Correo',
    'nombre_proveedor': 'Nombre', 'telefono': 'Teléfono', 'informacion_adicional': 'Información adicional',
    'tipo_documento': 'Tipo de documento', 'numero_documento_nit': 'NIT / documento', 'nombre_usuario': 'Nombre de usuario',
    'nombre_rol': 'Nombre', 'clientes': 'Clientes', 'usuarios': 'Usuarios', 'proveedores': 'Proveedores',
    'productos': 'Productos', 'compras': 'Compras', 'ventas': 'Ventas',
}
IGNORAR = {'contrasena'}              # nunca se guarda una contraseña (ni su hash) en la auditoría
CAMPOS_DINERO = {'precio', 'precio_pub'}


# ---------------------------------------------------------------- valores legibles
def _nombre_relacionado(campo, valor):
    try:
        rel = campo.related_model._base_manager.filter(pk=valor).first()
    except Exception:
        rel = None
    if rel is None:
        return f'#{valor}'
    for f in rel._meta.concrete_fields:
        if f.name.startswith('nombre'):
            return str(getattr(rel, f.name))
    return str(rel)


def _formato(campo, nombre, valor):
    if valor is None or valor == '':
        return '—'
    if campo.is_relation:
        return _nombre_relacionado(campo, valor)
    if nombre == 'estado':
        return 'Activo' if valor in (1, True, '1') else 'Inactivo'
    if isinstance(valor, bool):
        return 'Sí' if valor else 'No'
    if nombre in CAMPOS_DINERO and isinstance(valor, (int, float, Decimal)):
        return '$' + f'{round(float(valor)):,}'.replace(',', '.')
    if isinstance(valor, (datetime.datetime, datetime.date)):
        return valor.strftime('%d/%m/%Y')
    if isinstance(valor, (bytes, bytearray, memoryview)):
        return bytes(valor).decode('utf-8', 'ignore')[:200]
    if hasattr(valor, 'name') and not isinstance(valor, str):
        return str(valor.name)
    return str(valor)[:200]


def _como_comparable(valor):
    if isinstance(valor, datetime.datetime):
        # naive (p. ej. texto sin zona) y aware se comparan en UTC para no inventar cambios
        if timezone.is_naive(valor):
            valor = timezone.make_aware(valor)
        return valor.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat()
    if isinstance(valor, (bytes, bytearray, memoryview)):
        return bytes(valor).decode('utf-8', 'ignore')
    if hasattr(valor, 'name') and not isinstance(valor, (str, int, float)):
        return str(valor.name or '')
    if valor is None:
        return ''
    if isinstance(valor, bool):
        return int(valor)
    if isinstance(valor, float):
        return round(valor, 4)
    return valor


# ---------------------------------------------------------------- registro explícito
def registrar(accion, modulo, descripcion, objeto='', objeto_id='', cambios=None, actor=None):
    """Guarda un registro de auditoría. ``actor`` = {'nombre', 'correo', 'rol_id'} para sobrescribir al usuario actual."""
    try:
        from .models import RegistroAuditoria
        ctx = contexto.obtener()
        if ctx.get('silencio'):
            return
        actor = actor or {}
        RegistroAuditoria.objects.create(
            usuario_nombre=(actor.get('nombre') or ctx.get('usuario_nombre') or 'Sistema')[:80],
            usuario_correo=(actor.get('correo') or ctx.get('usuario_correo') or '')[:120],
            rol_id=actor.get('rol_id', ctx.get('rol_id')),
            ip=(actor.get('ip') or ctx.get('ip') or '')[:45],
            accion=accion[:30], modulo=modulo[:30], objeto=str(objeto)[:60], objeto_id=str(objeto_id)[:40],
            descripcion=str(descripcion)[:300],
            cambios=json.dumps(cambios, ensure_ascii=False) if cambios else '',
        )
    except Exception:
        logger.exception('No se pudo registrar la auditoría (%s %s)', accion, modulo)


# ---------------------------------------------------------------- señales (datos maestros)
def _campos_auditables(modelo):
    return [f for f in modelo._meta.concrete_fields if not f.primary_key and f.attname not in IGNORAR and f.name not in IGNORAR]


def _antes(sender, instance, raw=False, **kwargs):
    instance._audit_antes = None
    if raw or not instance.pk:
        return
    try:
        instance._audit_antes = sender._base_manager.filter(pk=instance.pk).values().first()
    except Exception:
        instance._audit_antes = None


def _despues(sender, instance, created=False, raw=False, **kwargs):
    if raw:
        return
    try:
        etiqueta, modulo, nombre_fn = TABLAS[sender._meta.db_table]
        nombre = nombre_fn(instance) or f'#{instance.pk}'
        if created:
            registrar('crear', modulo, f'Creó {etiqueta.lower()} «{nombre}»', etiqueta, instance.pk)
            return
        antes = getattr(instance, '_audit_antes', None)
        if not antes:
            return
        cambios = []
        for f in _campos_auditables(sender):
            nuevo, viejo = getattr(instance, f.attname, None), antes.get(f.attname)
            try:
                nuevo = f.to_python(nuevo)          # '2030-01-01' (texto) y datetime son el mismo valor
            except Exception:
                pass
            if _como_comparable(nuevo) != _como_comparable(viejo):
                cambios.append({'campo': CAMPOS.get(f.attname, CAMPOS.get(f.name, f.verbose_name)),
                                'antes': _formato(f, f.name, viejo), 'despues': _formato(f, f.name, nuevo), '_n': f.name})
        if not cambios:
            return
        estado = [c for c in cambios if c['_n'] == 'estado']
        if estado and len(cambios) == 1:
            accion = 'activar' if estado[0]['despues'] == 'Activo' else 'desactivar'
            texto = f'{"Activó" if accion == "activar" else "Desactivó"} {etiqueta.lower()} «{nombre}»'
        else:
            accion = 'editar'
            texto = f'Editó {etiqueta.lower()} «{nombre}»: ' + ', '.join(c['campo'] for c in cambios[:4]) + ('…' if len(cambios) > 4 else '')
        for c in cambios:
            c.pop('_n', None)
        registrar(accion, modulo, texto, etiqueta, instance.pk, cambios)
    except Exception:
        logger.exception('Error auditando %s', sender)


def _borrado(sender, instance, **kwargs):
    try:
        etiqueta, modulo, nombre_fn = TABLAS[sender._meta.db_table]
        registrar('eliminar', modulo, f'Eliminó {etiqueta.lower()} «{nombre_fn(instance) or "#" + str(instance.pk)}»', etiqueta, instance.pk)
    except Exception:
        logger.exception('Error auditando el borrado de %s', sender)


def conectar_senales():
    for modelo in apps.get_models():
        if modelo._meta.db_table in TABLAS and not modelo._meta.managed is True:
            uid = f'auditoria-{modelo._meta.label}'
            pre_save.connect(_antes, sender=modelo, dispatch_uid=uid + '-pre')
            post_save.connect(_despues, sender=modelo, dispatch_uid=uid + '-post')
            post_delete.connect(_borrado, sender=modelo, dispatch_uid=uid + '-del')
