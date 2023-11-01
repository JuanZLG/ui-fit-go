from django.shortcuts import render
from tuiranfitgo.views import jwt_cookie_required
from django.http import JsonResponse
from .models import Compras, Ventas, Clientes, Proveedores, Productos
from django.db.models import Sum
from django.db.models.functions import ExtractMonth

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

def calcular_total_compras(request, year):
    try:
       
        total_compras_por_mes = Compras.objects.filter(fechareg__year=year) \
            .annotate(month=ExtractMonth('fechareg')) \
            .values('month') \
            .annotate(total=Sum('totalCompra'))

        return JsonResponse({'total_compras_por_mes': list(total_compras_por_mes)})
    except Exception as e:
        return JsonResponse({'error': str(e)})


def calcular_total_ventas(request):
    total_ventas = Ventas.objects.aggregate(total_ventas=Sum('totalVenta'))['total_ventas'] 
    
    return JsonResponse({'total_ventas': total_ventas})


import locale
from django.db.models import Sum
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Ventas, Compras


locale.setlocale(locale.LC_TIME, 'es_CO.utf8')

def obtener_datos_ventas_y_compras(request):
    periodo = request.GET.get('periodo', 'semana')  # Obtén el periodo de la solicitud GET

    hoy = datetime.now().date()

    if periodo == 'semana':
        fecha_inicio = hoy - timedelta(days=hoy.weekday())
        fecha_fin = hoy
    elif periodo == 'mes':
        primer_dia_del_mes = hoy.replace(day=1)
        fecha_inicio = primer_dia_del_mes
        fecha_fin = hoy
    elif periodo == 'ano':
        primer_dia_del_ano = hoy.replace(month=1, day=1)
        fecha_inicio = primer_dia_del_ano
        fecha_fin = hoy

    ventas = Ventas.objects.filter(fechareg__range=[fecha_inicio, fecha_fin])
    compras = Compras.objects.filter(fechareg__range=[fecha_inicio, fecha_fin])

    total_ventas = ventas.aggregate(Sum('totalVenta'))['totalVenta__sum'] or 0
    total_compras = compras.aggregate(Sum('totalCompra'))['totalCompra__sum'] or 0

    data = {
        'total_ventas': total_ventas,
        'total_compras': total_compras,
    }
    print(data  )

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
