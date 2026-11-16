"""Auditoría, meta mensual de ventas y contacto por WhatsApp."""
import json
from datetime import date

import pytest
from django.test import Client
from django.urls import reverse

from authenticator.security import hashear
from control import auditoria
from control.models import MetaVentas, RegistroAuditoria
from customers.models import Clientes, Departamentos, Municipios
from dashboard import insights
from orders.models import DetallePedido, Pedidos
from orders.whatsapp import mensaje_pedido, normalizar_celular, url_whatsapp
from sales.models import Detalleventa, Ventas
from users.models import Roles, Usuarios

pytestmark = pytest.mark.django_db


@pytest.fixture
def cliente(db):
    depto = Departamentos.objects.create(nombre_departamento='Antioquia')
    muni = Municipios.objects.create(id_departamento=depto, nombre_municipio='Medellin')
    return Clientes.objects.create(id_municipio=muni, documento='900', nombres='Ana Maria', apellidos='Ruiz', celular='300 123 4567',
                                   barrio='Laureles', direccion='Calle 10 # 5-20', estado=True, correo='a@t.co')


def producto_post(p, **extra):
    datos = {'iNombre': p.nombre_producto, 'iDescripcion': 'd', 'iCantidad': str(p.cantidad), 'iFechaven': '2030-05-01', 'iSabor': 'x',
             'iServices': '1 lb', 'iPrice': '100', 'iPubPrice': '150', 'iCategoria': p.id_categoria_id, 'iMarca': p.id_marca_id}
    datos.update(extra)
    return datos


# ------------------------------------------------------------------ auditoría automática
def test_editar_producto_registra_quien_y_el_antes_y_despues(admin_client, catalogo):
    p = catalogo('Whey', cantidad=10)
    RegistroAuditoria.objects.all().delete()
    r = admin_client.post(reverse('editAProduct', args=[p.id_producto]), producto_post(p, iCantidad='7', iPubPrice='199'))
    assert r.status_code == 200
    reg = RegistroAuditoria.objects.get(accion='editar', modulo='productos')
    assert reg.usuario_nombre == 'Tester' and reg.usuario_correo == 'tester@tuiranfit.test'
    cambios = {c['campo']: (c['antes'], c['despues']) for c in reg.cambios_lista}
    assert cambios['Existencias'] == ('10', '7') and cambios['Precio al público'] == ('$150', '$199')
    assert 'Whey' in reg.descripcion


def test_activar_y_desactivar_y_creacion_automatica(admin_client, catalogo):
    p = catalogo('Gorra')
    assert RegistroAuditoria.objects.filter(accion='crear', descripcion__contains='Gorra').exists()       # alta sin usuario: Sistema
    RegistroAuditoria.objects.all().delete()
    admin_client.get(reverse('cambiarEstadoDeProducto'), {'producto_id': p.id_producto, 'nuevo_estado': 0}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    reg = RegistroAuditoria.objects.get()
    assert reg.accion == 'desactivar' and reg.usuario_nombre == 'Tester' and reg.cambios_lista[0]['despues'] == 'Inactivo'


def test_guardar_sin_cambios_no_genera_registro(catalogo):
    p = catalogo('Quieto')
    RegistroAuditoria.objects.all().delete()
    p.save()
    assert RegistroAuditoria.objects.count() == 0


def test_la_contrasena_nunca_se_audita(db):
    rol = Roles.objects.create(nombre_rol='X')
    u = Usuarios.objects.create(id_rol=rol, correo='u@t.co', nombre_usuario='U', contrasena=hashear('Clave1234'), estado=1)
    RegistroAuditoria.objects.all().delete()
    u.contrasena = hashear('Otra12345'); u.save()
    assert RegistroAuditoria.objects.count() == 0                         # solo cambió la contraseña: no hay nada que mostrar
    u.nombre_usuario = 'Nuevo'; u.save()
    texto = json.dumps(list(RegistroAuditoria.objects.values()), default=str)
    assert 'Clave1234' not in texto and 'Otra12345' not in texto and 'bcrypt' not in texto.lower() and '$2b$' not in texto


# ------------------------------------------------------------------ auditoría de operaciones
def vender(client, producto, cantidad=2, documento='900'):
    total = 150 * cantidad
    data = {'documentoCliente': documento, 'totalVenta': total, 'margenGananciaVenta': 50, 'descuentoVenta': 'No aplica',
            'totalVentaDescuento': 'No aplica', 'productos': {str(producto.id_producto): {
                'idPedido': 'no pedido', 'cantidad': cantidad, 'precioCompra': 100, 'precioVenta': 150, 'descuentoProducto': 'No aplica',
                'margenGananciaProducto': 50, 'totalProducto': total, 'totalProductoDescuento': 'No aplica'}}}
    return client.post(reverse('crear_venta'), json.dumps(data), content_type='application/json')


def test_venta_y_anulacion_quedan_registradas_una_sola_vez(admin_client, catalogo, cliente):
    p = catalogo('Whey', cantidad=10)
    RegistroAuditoria.objects.all().delete()
    assert vender(admin_client, p).status_code == 200
    venta = Ventas.objects.get()
    reg = RegistroAuditoria.objects.get(accion='crear', modulo='ventas')
    assert f'#{venta.id_venta:06d}' in reg.descripcion and 'Ana Maria' in reg.descripcion and '2× Whey' in reg.cambios_lista[0]['despues']
    url = reverse('cambiarEstadoVentas')
    args = {'venta_id': venta.id_venta, 'nuevo_estado': 0}
    admin_client.get(url, args, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    admin_client.get(url, args, HTTP_X_REQUESTED_WITH='XMLHttpRequest')               # repetir no cambia nada
    assert RegistroAuditoria.objects.filter(accion='anular').count() == 1


def test_una_venta_rechazada_no_deja_registro(admin_client, catalogo, cliente):
    p = catalogo('Poco', cantidad=1)
    RegistroAuditoria.objects.all().delete()
    assert vender(admin_client, p, cantidad=5).status_code == 400
    assert not RegistroAuditoria.objects.filter(accion='crear', modulo='ventas').exists()


def test_si_la_auditoria_falla_la_operacion_sigue(admin_client, catalogo, cliente, monkeypatch):
    p = catalogo('Whey', cantidad=10)
    def explota(*a, **k): raise RuntimeError('tabla de auditoría caída')
    monkeypatch.setattr(RegistroAuditoria.objects, 'create', explota)
    assert vender(admin_client, p).status_code == 200
    p.refresh_from_db(); assert p.cantidad == 8


def test_inicios_de_sesion_exitosos_y_fallidos(anonimo, db):
    rol = Roles.objects.create(nombre_rol='Admin')
    Usuarios.objects.create(id_rol=rol, correo='u@t.co', nombre_usuario='Uri', contrasena=hashear('Clave1234'), estado=1)
    post = lambda correo, clave: anonimo.post(reverse('login_view'), json.dumps({'correo': correo, 'contra': clave}), content_type='application/json')
    assert post('u@t.co', 'Clave1234').status_code == 200
    assert post('u@t.co', 'zz-clave-secreta-777').status_code == 401
    assert post('nadie@t.co', 'x').status_code == 401
    acciones = list(RegistroAuditoria.objects.filter(modulo='seguridad').values_list('accion', flat=True))
    assert sorted(acciones) == ['login', 'login_fallido', 'login_fallido']
    assert 'zz-clave-secreta-777' not in json.dumps(list(RegistroAuditoria.objects.values()), default=str)      # nunca se guarda la clave intentada


# ------------------------------------------------------------------ pantalla de auditoría
def test_pantalla_de_auditoria_filtros_y_csv(admin_client, catalogo):
    catalogo('Whey Gold')
    auditoria.registrar('anular', 'ventas', 'Anuló la venta #000001')
    url = reverse('auditoria')
    html = admin_client.get(url).content.decode()
    assert 'Anuló la venta' in html and 'Whey Gold' in html
    solo_ventas = admin_client.get(url, {'modulo': 'ventas'}).content.decode()
    assert 'Anuló la venta' in solo_ventas and 'Whey Gold' not in solo_ventas
    assert 'Anuló la venta' in admin_client.get(url, {'q': 'venta #000001'}).content.decode()
    csv = admin_client.get(url, {'formato': 'csv'})
    assert csv['Content-Type'].startswith('text/csv') and csv.content.decode('utf-8-sig').startswith('Fecha;Usuario')
    assert 'Anuló la venta' in csv.content.decode('utf-8-sig')


def test_auditoria_exige_sesion_y_permiso(anonimo, cliente_sin_permisos):
    for nombre in ('auditoria', 'auditoria_reciente'):
        assert anonimo.get(reverse(nombre)).status_code == 302
        assert cliente_sin_permisos.get(reverse(nombre)).status_code == 302


def test_actividad_reciente_devuelve_los_ultimos(admin_client):
    for i in range(10):
        auditoria.registrar('editar', 'productos', f'Cambio {i}')
    filas = admin_client.get(reverse('auditoria_reciente')).json()['registros']
    assert len(filas) == 8 and filas[0]['descripcion'] == 'Cambio 9'


# ------------------------------------------------------------------ meta mensual
def venta_del(cliente, dia, total, mes=11):
    return Ventas.objects.create(id_cliente_id=cliente.id_cliente, fechareg=date(2026, mes, dia), totalVenta=total, margenGanancia=0,
                                 descuentoVenta='', totalVentaDescuento='', estado=1)


def test_progreso_sin_meta_sugiere_una(cliente):
    venta_del(cliente, 5, 3_000_000, mes=8); venta_del(cliente, 5, 3_000_000, mes=9); venta_del(cliente, 5, 3_000_000, mes=10)
    r = insights.progreso_meta(hoy=date(2026, 11, 16))
    assert r['estado'] == 'sin_meta' and r['meta'] is None and r['sugerida'] == 3_300_000


@pytest.mark.parametrize('vendido,estado', [(800, 'adelantada'), (540, 'al_ritmo'), (200, 'atrasada'), (1200, 'cumplida')])
def test_estado_de_la_meta_segun_el_ritmo(cliente, vendido, estado):
    MetaVentas.objects.create(anio=2026, mes=11, valor=1000)
    venta_del(cliente, 10, vendido)
    r = insights.progreso_meta(hoy=date(2026, 11, 16))          # dia 16 de 30: lo esperado es 533
    assert r['estado'] == estado and r['esperado'] == 533
    if estado != 'cumplida':
        assert r['diario_necesario'] == round((1000 - vendido) / 15)
    else:
        assert r['faltante'] == 0 and r['diario_necesario'] == 0


def test_guardar_meta_valida_audita_y_exige_csrf(admin_client, cliente_sin_permisos):
    url = reverse('guardar_meta')
    post = lambda c, v: c.post(url, json.dumps({'valor': v}), content_type='application/json')
    assert post(admin_client, 0).status_code == 400 and post(admin_client, 'abc').status_code == 400
    ok = post(admin_client, 4_500_000)
    assert ok.status_code == 200 and ok.json()['meta']['meta'] == 4_500_000
    assert MetaVentas.objects.get().definida_por == 'Tester'
    assert post(admin_client, 5_000_000).status_code == 200 and MetaVentas.objects.count() == 1            # actualiza, no duplica
    reg = RegistroAuditoria.objects.filter(objeto='Meta de ventas').order_by('id').last()
    assert reg.accion == 'editar' and reg.cambios_lista[0] == {'campo': 'Meta mensual', 'antes': '$4.500.000', 'despues': '$5.000.000'}
    assert post(cliente_sin_permisos, 1000).status_code == 302
    estricto = Client(enforce_csrf_checks=True); estricto.cookies = admin_client.cookies
    assert post(estricto, 1000).status_code == 403
    assert admin_client.get(url).status_code == 405


# ------------------------------------------------------------------ WhatsApp
@pytest.mark.parametrize('entrada,esperado', [('300 123 4567', '573001234567'), ('3001234567', '573001234567'), ('+57 (300) 123-4567', '573001234567'),
                                              ('573001234567', '573001234567'), ('6041234567', ''), ('', ''), (None, ''), ('abc', '')])
def test_normalizar_celular(entrada, esperado):
    assert normalizar_celular(entrada) == esperado


def test_mensajes_segun_el_estado_del_pedido(cliente, catalogo):
    p = catalogo('Whey Gold')
    ped = Pedidos.objects.create(id_venta=None, id_cliente_id=cliente.id_cliente, total_pedido=478000, estado='en proceso')
    det = [DetallePedido.objects.create(id_pedido=ped, id_producto_id=p.id_producto, sabor='x', cantidad=2, precio_uni=239000, precio_tot=478000)]
    en_proceso = mensaje_pedido(ped, cliente, det)
    assert 'Hola Ana' in en_proceso and '#%d' % ped.id_pedido in en_proceso and '2× Whey Gold' in en_proceso and '$478.000' in en_proceso and 'Calle 10 # 5-20' in en_proceso
    ped.estado = 'confirmado'; assert 'ya fue confirmado' in mensaje_pedido(ped, cliente, det)
    ped.estado = 'cancelado'; assert 'fue cancelado' in mensaje_pedido(ped, cliente, det)
    url = url_whatsapp('300 123 4567', 'Hola ñandú & más')
    assert url.startswith('https://wa.me/573001234567?text=Hola%20%C3%B1and%C3%BA%20%26%20m%C3%A1s')
    assert url_whatsapp('123', 'x') == ''


def test_la_lista_de_pedidos_trae_el_boton_de_whatsapp(admin_client, cliente, catalogo):
    p = catalogo('Whey')
    ped = Pedidos.objects.create(id_venta=None, id_cliente_id=cliente.id_cliente, total_pedido=1, estado='en proceso')
    DetallePedido.objects.create(id_pedido=ped, id_producto_id=p.id_producto, sabor='x', cantidad=1, precio_uni=1, precio_tot=1)
    html = admin_client.get(reverse('pedidos')).content.decode()
    assert 'https://wa.me/573001234567?text=' in html and 'btn-whatsapp' in html
    cliente.celular = 'sin numero'; cliente.save()
    assert 'https://wa.me/' not in admin_client.get(reverse('pedidos')).content.decode()


def test_los_informes_vacios_y_con_datos_siguen_distintos_y_quedan_auditados(admin_client, catalogo, cliente):
    """Regresión: un return mal indentado hacía que todo informe saliera vacío."""
    p = catalogo('Whey', cantidad=10)
    vender(admin_client, p)
    hoy = str(Ventas.objects.get().fechareg)
    con = admin_client.post(reverse('generar_informe_pdf_ventas'), {'fecha_inicio': hoy, 'fecha_fin': hoy}).content
    sin = admin_client.post(reverse('generar_informe_pdf_ventas'), {'fecha_inicio': '2000-01-01', 'fecha_fin': '2000-01-02'}).content
    assert len(con) > len(sin) + 500
    assert RegistroAuditoria.objects.filter(accion='exportar', modulo='ventas', descripcion__contains='informe de ventas').count() == 1   # solo el que tuvo datos
