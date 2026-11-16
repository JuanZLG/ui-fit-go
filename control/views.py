import csv
import json
from datetime import date, timedelta

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from dashboard import insights
from tuiranfitgo.views import jwt_cookie_required, module_access_required
from users.models import Roles

from . import auditoria as aud
from .models import MetaVentas, RegistroAuditoria

POR_PAGINA = 30


def _fecha(valor):
    try:
        return date.fromisoformat((valor or '').strip())
    except ValueError:
        return None


@jwt_cookie_required
@module_access_required('usuarios')
def auditoria(request):
    """Historial de actividad: quién hizo qué y cuándo, con filtros y exportación a CSV."""
    g = request.GET
    registros = RegistroAuditoria.objects.all()
    modulo, accion = g.get('modulo', ''), g.get('accion', '')
    desde, hasta = _fecha(g.get('desde')), _fecha(g.get('hasta'))
    q = (g.get('q') or '').strip()
    if modulo:
        registros = registros.filter(modulo=modulo)
    if accion:
        registros = registros.filter(accion=accion)
    if desde:
        registros = registros.filter(fecha__date__gte=desde)
    if hasta:
        registros = registros.filter(fecha__date__lte=hasta)
    if q:
        registros = registros.filter(Q(descripcion__icontains=q) | Q(usuario_nombre__icontains=q) | Q(usuario_correo__icontains=q)
                                     | Q(objeto_id__icontains=q))

    if g.get('formato') == 'csv':
        aud.registrar('exportar', 'usuarios', f'Exportó el registro de auditoría ({registros.count()} filas)')
        respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
        respuesta['Content-Disposition'] = f'attachment; filename="auditoria_{timezone.localdate()}.csv"'
        respuesta.write('\ufeff')
        escritor = csv.writer(respuesta, delimiter=';')
        escritor.writerow(['Fecha', 'Usuario', 'Correo', 'IP', 'Módulo', 'Acción', 'Objeto', 'ID', 'Descripción', 'Cambios'])
        for r in registros[:5000]:
            cambios = ' | '.join(f"{c['campo']}: {c['antes']} → {c['despues']}" for c in r.cambios_lista)
            escritor.writerow([timezone.localtime(r.fecha).strftime('%d/%m/%Y %H:%M:%S'), r.usuario_nombre, r.usuario_correo, r.ip,
                               r.modulo, r.accion, r.objeto, r.objeto_id, r.descripcion, cambios])
        return respuesta

    pagina = Paginator(registros, POR_PAGINA).get_page(g.get('pagina'))
    roles = {r.id_rol: r.nombre_rol for r in Roles.objects.all()}
    for r in pagina:
        r.rol_nombre = roles.get(r.rol_id, '')

    ahora = timezone.now()
    base = RegistroAuditoria.objects
    semana = base.filter(fecha__gte=ahora - timedelta(days=7))
    top = semana.values('modulo').annotate(n=Count('id')).order_by('-n').first()
    consulta = g.copy()
    consulta.pop('pagina', None)
    return render(request, 'auditoria.html', {
        'pagina': pagina, 'total': registros.count(),
        'resumen': {
            'hoy': base.filter(fecha__date=timezone.localdate()).count(), 'semana': semana.count(),
            'usuarios': semana.exclude(usuario_correo='').values('usuario_correo').distinct().count(),
            'modulo_top': top['modulo'] if top else '—',
        },
        'modulos': list(base.order_by().values_list('modulo', flat=True).distinct()),
        'acciones': list(base.order_by().values_list('accion', flat=True).distinct()),
        'filtros': {'modulo': modulo, 'accion': accion, 'desde': g.get('desde', ''), 'hasta': g.get('hasta', ''), 'q': q},
        'consulta': consulta.urlencode(),
    })


@jwt_cookie_required
@module_access_required('usuarios')
def actividad_reciente(request):
    """Últimos movimientos para el panel del dashboard."""
    filas = [{
        'fecha': timezone.localtime(r.fecha).strftime('%d/%m %H:%M'), 'iso': r.fecha.isoformat(), 'usuario': r.usuario_nombre or 'Sistema',
        'accion': r.accion, 'modulo': r.modulo, 'descripcion': r.descripcion,
    } for r in RegistroAuditoria.objects.all()[:8]]
    return JsonResponse({'registros': filas})


@jwt_cookie_required
def meta_actual(request):
    return JsonResponse(insights.progreso_meta())


@require_POST
@jwt_cookie_required
@module_access_required('ventas')
def guardar_meta(request):
    """Define (o cambia) la meta de ventas del mes en curso."""
    try:
        datos = json.loads(request.body or '{}')
        valor = int(float(str(datos.get('valor')).replace('.', '').replace(',', '.')) if isinstance(datos.get('valor'), str) else datos.get('valor'))
    except (ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Escribe un valor numérico.'}, status=400)
    if valor <= 0 or valor > 10 ** 12:
        return JsonResponse({'ok': False, 'error': 'La meta debe ser mayor que cero.'}, status=400)

    hoy = timezone.localdate()
    ctx = request.user if isinstance(request.user, dict) else {}
    meta = MetaVentas.objects.filter(anio=hoy.year, mes=hoy.month).first()
    previo = meta.valor if meta else None
    meta, _ = MetaVentas.objects.update_or_create(anio=hoy.year, mes=hoy.month,
                                                  defaults={'valor': valor, 'definida_por': ctx.get('nombre_usuario', '')})
    fmt = lambda v: '—' if v is None else '$' + f'{v:,}'.replace(',', '.')
    aud.registrar('editar' if previo else 'crear', 'ventas', f'{"Cambió" if previo else "Definió"} la meta de ventas de {insights.MESES[hoy.month]}: {fmt(valor)}',
                  'Meta de ventas', f'{hoy.year}-{hoy.month:02d}', [{'campo': 'Meta mensual', 'antes': fmt(previo), 'despues': fmt(valor)}])
    return JsonResponse({'ok': True, 'meta': insights.progreso_meta()})
