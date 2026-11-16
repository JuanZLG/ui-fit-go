from django.shortcuts import render
from tuiranfitgo.views import jwt_cookie_required, module_access_required
from django.http import JsonResponse
from .models import Compras, Ventas, Clientes, Proveedores, Productos
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import locale
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Pedidos

@jwt_cookie_required
def Entrance(request):
    return render(request, 'tgoEntrance.html')

@jwt_cookie_required
def Home(request):
    return render(request, 'dashboard.html')

@jwt_cookie_required
def UserGuide(request):
    return render(request, 'manual.html')

@jwt_cookie_required
def contar_clientes_activos(request):
    clientes_activos = Clientes.objects.filter(estado=1).count()
    return JsonResponse({'clientes_activos': clientes_activos}) 

@jwt_cookie_required
def contar_pedidos_en_proceso(request):
    pedidos_en_proceso = Pedidos.objects.filter(estado='en proceso').count()
    data = {'pedidos_en_proceso': pedidos_en_proceso}
    return JsonResponse(data)

@jwt_cookie_required
def calcular_total_compras_y_ventas(request):
    try:
        current_year = timezone.now().year
        current_month = timezone.now().month

        total_compras_por_mes = Compras.objects.filter(
            fechareg__year=current_year,
            fechareg__month=current_month,
            estado=1 
        ).annotate(month=ExtractMonth('fechareg')) \
            .values('month') \
            .annotate(total_compras=Sum('totalCompra'))

        total_ventas_por_mes = Ventas.objects.filter(
            fechareg__year=current_year,
            fechareg__month=current_month,
            estado=1 
        ).annotate(month=ExtractMonth('fechareg')) \
            .values('month') \
            .annotate(total_ventas=Sum('totalVenta'))

        return JsonResponse({
            'total_compras_por_mes': list(total_compras_por_mes),
            'total_ventas_por_mes': list(total_ventas_por_mes)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

locale.setlocale(locale.LC_TIME, 'es_CO.utf8')
@jwt_cookie_required
def obtener_datos_ventas_y_compras(request):
    periodo = request.GET.get('periodo', 'semana')
    hoy = datetime.now().date()

    if periodo == 'semana':
        ultimo_dia_semana_pasada = hoy - timedelta(days=(hoy.weekday() + 1) % 7)
        fecha_inicio = ultimo_dia_semana_pasada - timedelta(days=6)
        fecha_fin = ultimo_dia_semana_pasada
        etiqueta_semana = f'Última semana del {fecha_inicio.strftime("%d/%m/%Y")} al {fecha_fin.strftime("%d/%m/%Y")}'
    elif periodo == 'mes':
        primer_dia_del_mes = hoy.replace(day=1)
        fecha_inicio = primer_dia_del_mes
        fecha_fin = hoy
        etiqueta_semana = fecha_inicio.strftime('%b %Y')
    elif periodo == 'ano':
        primer_dia_del_ano = hoy.replace(month=1, day=1)
        fecha_inicio = primer_dia_del_ano
        fecha_fin = hoy
        etiqueta_semana = fecha_inicio.strftime('%Y')

    ventas = Ventas.objects.filter(fechareg__range=[fecha_inicio, fecha_fin], estado=1)
    compras = Compras.objects.filter(fechareg__range=[fecha_inicio, fecha_fin], estado=1)

    total_ventas = ventas.aggregate(Sum('totalVenta'))['totalVenta__sum'] or 0
    total_compras = compras.aggregate(Sum('totalCompra'))['totalCompra__sum'] or 0

    total_ventas_formatted = "{:,.0f}".format(total_ventas)
    total_compras_formatted = "{:,.0f}".format(total_compras)

    total_ventas = int(total_ventas)
    total_compras = int(total_compras)

    data = {
        'total_ventas': total_ventas_formatted,
        'total_compras': total_compras_formatted,
        'labels': [etiqueta_semana],
        'ventas': [total_ventas],
        'compras': [total_compras],
    }

    return JsonResponse(data)

from django.http import JsonResponse
from .models import Productos

@jwt_cookie_required
def obtener_todos_los_productos(request):
    try:
        productos = Productos.objects.filter(estado=1)

        nombres_productos = [producto.nombre_producto for producto in productos]
        cantidades = [producto.cantidad for producto in productos]

        data = {
            'productos': nombres_productos,
            'cantidades': cantidades,
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
@jwt_cookie_required
def obtener_margen_ganancia(request):
    try:
        current_year = timezone.now().year
        current_month = timezone.now().month

        margen_ganancia = Ventas.objects.filter(
            fechareg__year=current_year,
            fechareg__month=current_month,
            estado=1  
        ).aggregate(margen_ganancia_total=Sum('margenGanancia'))

        return JsonResponse({'margen_ganancia_total': margen_ganancia['margen_ganancia_total']})
    except Exception as e:
        return JsonResponse({'error': str(e)})
    

from django.http import JsonResponse
from django.db.models import Sum

@jwt_cookie_required
def obtener_datos_categorias_productos(request):
    try:
        datos_categorias = (
            Productos.objects.filter(estado=1)
            .values('id_categoria__nombre_categoria')
            .annotate(total_cantidad=Sum('cantidad'))
            .order_by('id_categoria__nombre_categoria')
        )

        categorias = [dato['id_categoria__nombre_categoria'] or 'Sin categoría' for dato in datos_categorias]
        cantidades = [dato['total_cantidad'] for dato in datos_categorias]

        data = {
            'categorias': categorias,
            'cantidades': cantidades
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})



# ======================================================================================
# Inteligencia de negocio (marcador comparativo, inventario inteligente, búsqueda global)
# ======================================================================================
from django.db.models import Q
from django.urls import reverse
from . import insights


@jwt_cookie_required
def obtener_resumen(request):
    """Marcador: mes actual frente al mismo tramo del mes anterior + serie de 14 días."""
    return JsonResponse(insights.resumen_marcador())


@jwt_cookie_required
def inteligencia_inventario(request):
    """Reposición sugerida, productos por vencer, sin rotación y capital en inventario."""
    return JsonResponse(insights.inventario_inteligente())


@jwt_cookie_required
@module_access_required('compras')
def orden_compra_sugerida_pdf(request):
    """PDF con lo que conviene comprar hoy para cubrir los próximos días de venta."""
    from tuiranfitgo.reports import Informe, cop, E_PEQ
    datos = insights.inventario_inteligente()
    pedido = [r for r in datos['reposicion'] if r['sugerido'] > 0]
    informe = Informe('Orden de compra sugerida', timezone.localdate().strftime('%d/%m/%Y'),
                      f'Cobertura a {insights.DIAS_COBERTURA} días')
    nombre = f'orden_compra_sugerida_{timezone.localdate()}.pdf'
    if not pedido:
        informe.aviso('Por ahora no hay productos que necesiten reposición.')
        return informe.respuesta(nombre)

    informe.espacio(2)
    informe.tarjetas([('Productos a reponer', str(len(pedido))), ('Unidades sugeridas', str(sum(r['sugerido'] for r in pedido))),
                      ('Inversión estimada', cop(datos['inversion_sugerida'])),
                      ('Críticos', str(sum(1 for r in pedido if r['nivel'] == 'critico')))])
    informe.seccion('Productos a comprar')
    filas = [[r['producto'], r['stock'],
              f"{r['ventas_por_dia']:g}", '—' if r['dias_restantes'] is None else f"{r['dias_restantes']:g}",
              'CRÍTICO' if r['nivel'] == 'critico' else 'ATENCIÓN', r['sugerido'], cop(r['costo_estimado'])] for r in pedido]
    informe.tabla(['Producto', 'Stock', 'Ventas/día', 'Días', 'Nivel', 'Comprar', 'Costo est.'], filas,
                  [182, 44, 56, 40, 60, 54, 96], 'LCCCCCR', total=['', '', '', '', '', 'TOTAL', cop(datos['inversion_sugerida'])])
    informe.espacio(14)
    informe.parrafo(f'Calculado con el ritmo de ventas de los últimos {insights.DIAS_VENTANA} días. '
                    'Es una sugerencia: ajústala según tus promociones, temporadas y plazos de entrega del proveedor.',
                    E_PEQ)
    from control import auditoria as aud
    aud.registrar('exportar', 'compras', f'Generó la orden de compra sugerida ({len(pedido)} productos)')
    return informe.respuesta(nombre)


def _modulos_permitidos(request):
    from users.models import Rolespermisos
    rol = (getattr(request, 'user', None) or {}).get('id_rol')
    permitidos = set()
    for modulo in ('clientes', 'productos', 'proveedores', 'ventas', 'compras', 'usuarios'):
        if Rolespermisos.objects.filter(id_rol=rol, **{f'id_permiso__{modulo}': 1}).exists():
            permitidos.add(modulo)
    return permitidos


@jwt_cookie_required
def buscar_global(request):
    """Búsqueda para la paleta de comandos: productos, clientes, proveedores, ventas y pedidos."""
    from customers.models import Clientes as ClientesApp
    from eproviders.models import Proveedores as ProveedoresApp
    from orders.models import Pedidos as PedidosApp
    from products.models import Productos as ProductosApp
    from sales.models import Ventas as VentasApp

    q = (request.GET.get('q') or '').strip()
    if len(q) < 2:
        return JsonResponse({'grupos': []})
    permitidos = _modulos_permitidos(request)
    grupos = []

    def agregar(titulo, icono, items):
        if items:
            grupos.append({'grupo': titulo, 'icono': icono, 'items': items})

    if 'productos' in permitidos:
        agregar('Productos', 'fa-box', [
            {'label': p.nombre_producto, 'meta': f'Stock {p.cantidad} · ${p.precio_pub:,.0f}'.replace(',', '.'),
             'url': reverse('editAProduct', args=[p.id_producto])}
            for p in ProductosApp.objects.filter(nombre_producto__icontains=q).order_by('nombre_producto')[:5]])
    if 'clientes' in permitidos:
        agregar('Clientes', 'fa-user', [
            {'label': f'{c.nombres} {c.apellidos}', 'meta': f'{c.documento} · {c.celular}',
             'url': reverse('editarCliente', args=[c.id_cliente])}
            for c in ClientesApp.objects.filter(Q(nombres__icontains=q) | Q(apellidos__icontains=q) | Q(documento__icontains=q))[:5]])
    if 'proveedores' in permitidos:
        agregar('Proveedores', 'fa-truck-field', [
            {'label': p.nombre_proveedor, 'meta': f'{p.numero_documento_nit} · {p.telefono}',
             'url': reverse('editarProveedor', args=[p.id_proveedor])}
            for p in ProveedoresApp.objects.filter(Q(nombre_proveedor__icontains=q) | Q(numero_documento_nit__icontains=q))[:5]])
    if 'ventas' in permitidos:
        filtro = Q(id_cliente__nombres__icontains=q) | Q(id_cliente__apellidos__icontains=q) | Q(id_cliente__documento__icontains=q)
        if q.isdigit():
            filtro |= Q(id_venta=int(q))
        agregar('Ventas', 'fa-receipt', [
            {'label': f'Venta #{v.id_venta:06d} · {v.id_cliente.nombres} {v.id_cliente.apellidos}',
             'meta': f'{v.fechareg:%d/%m/%Y} · ${v.totalVenta:,.0f}'.replace(',', '.'),
             'url': reverse('generar_factura_pdf_venta', args=[v.id_venta]), 'nueva_pestana': True}
            for v in VentasApp.objects.filter(filtro).select_related('id_cliente').order_by('-id_venta')[:5]])
        agregar('Pedidos', 'fa-truck', [
            {'label': f'Pedido #{p.id_pedido} · {p.id_cliente.nombres} {p.id_cliente.apellidos}',
             'meta': f'{p.estado} · ${p.total_pedido:,.0f}'.replace(',', '.'),
             'url': reverse('editarPedidoHome', args=[p.id_pedido])}
            for p in PedidosApp.objects.filter(Q(id_cliente__nombres__icontains=q) | Q(id_cliente__apellidos__icontains=q)
                                               | Q(id_cliente__documento__icontains=q)).select_related('id_cliente').order_by('-id_pedido')[:4]])
    return JsonResponse({'grupos': grupos})
