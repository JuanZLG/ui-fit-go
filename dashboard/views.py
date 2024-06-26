from django.shortcuts import render
from tuiranfitgo.views import jwt_cookie_required
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

def contar_clientes_activos(request):
    clientes_activos = Clientes.objects.filter(estado=1).count()
    return JsonResponse({'clientes_activos': clientes_activos}) 

def contar_pedidos_en_proceso(request):
    pedidos_en_proceso = Pedidos.objects.filter(estado='en proceso').count()
    data = {'pedidos_en_proceso': pedidos_en_proceso}
    return JsonResponse(data)

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

def obtener_datos_categorias_productos(request):
    try:
        datos_categorias = Productos.objects.values('categoria').annotate(
            total_cantidad=Sum('cantidad')
        )

        categorias = [dato['categoria'] for dato in datos_categorias]
        cantidades = [dato['total_cantidad'] for dato in datos_categorias]

        data = {
            'categorias': categorias,
            'cantidades': cantidades
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})

