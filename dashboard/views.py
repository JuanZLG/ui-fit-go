from django.shortcuts import render
from tuiranfitgo.views import jwt_cookie_required
from django.http import JsonResponse
from .models import Compras, Ventas, Clientes, Proveedores, Productos
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import locale
from datetime import datetime, timedelta

@jwt_cookie_required
def Entrance(request):
    return render(request, 'tgoEntrance.html')

@jwt_cookie_required
def Home(request):
    return render(request, 'dashboard.html')

@jwt_cookie_required
def UserGuide(request):
    return render(request, 'manual.html')

def contar_clientes_activos(request):
    clientes_activos = Clientes.objects.filter(estado=1).count()
    clientes_inactivos = Clientes.objects.filter(estado=0).count()
    return JsonResponse({'clientes_activos': clientes_activos, 'clientes_inactivos': clientes_inactivos}) 

from django.db.models import Sum
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.utils import timezone

def calcular_total_compras_y_ventas(request):
    try:
        # Obtén el año actual
        current_year = timezone.now().year
        # Obtén el mes actual
        current_month = timezone.now().month

        # Filtra las compras del año actual y mes actual
        total_compras_por_mes = Compras.objects.filter(fechareg__year=current_year, fechareg__month=current_month) \
            .annotate(month=ExtractMonth('fechareg')) \
            .values('month') \
            .annotate(total_compras=Sum('totalCompra'))

        # Filtra las ventas del año actual y mes actual
        total_ventas_por_mes = Ventas.objects.filter(fechareg__year=current_year, fechareg__month=current_month) \
            .annotate(month=ExtractMonth('fechareg')) \
            .values('month') \
            .annotate(total_ventas=Sum('totalVenta'))

        return JsonResponse({
            'total_compras_por_mes': list(total_compras_por_mes),
            'total_ventas_por_mes': list(total_ventas_por_mes)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

locale.setlocale(locale.LC_TIME, 'es_CO.utf8')

def obtener_datos_ventas_y_compras(request):
    periodo = request.GET.get('periodo', 'semana')
    hoy = datetime.now().date()

    if periodo == 'semana':
        # Calcular el inicio de la última semana
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

    ventas = Ventas.objects.filter(fechareg__range=[fecha_inicio, fecha_fin])
    compras = Compras.objects.filter(fechareg__range=[fecha_inicio, fecha_fin])

    total_ventas = ventas.aggregate(Sum('totalVenta'))['totalVenta__sum'] or 0
    total_compras = compras.aggregate(Sum('totalCompra'))['totalCompra__sum'] or 0

    # Formatea los totales de ventas y compras
    total_ventas_formatted = "{:,.0f}".format(total_ventas)
    total_compras_formatted = "{:,.0f}".format(total_compras)

    # Convierte los valores en números enteros en lugar de números de punto flotante
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












def obtener_todos_los_productos(request):
    try:
        # Consulta para obtener todos los productos y sus cantidades.
        productos = Productos.objects.all()

        # Extrae los nombres de los productos y las cantidades en listas separadas.
        nombres_productos = [producto.nombre_producto for producto in productos]
        cantidades = [producto.cantidad for producto in productos]

        data = {
            'productos': nombres_productos,
            'cantidades': cantidades,
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})
