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


locale.setlocale(locale.LC_TIME, 'es_CO.utf8')

def obtener_datos_ventas_y_compras(request):

    ventas = Ventas.objects.values('fechareg').annotate(total_ventas=Sum('totalVenta')).order_by('fechareg')
    compras = Compras.objects.values('fechareg').annotate(total_compras=Sum('totalCompra')).order_by('fechareg')

    data = {
        'labels': [], 
        'ventas': [],  
        'compras': [],  
    }

    
    totals_por_mes = {}


    for venta in ventas:
        fecha = venta['fechareg']
        mes_anio = fecha.strftime('%B %Y')
        
        if mes_anio not in totals_por_mes:
            totals_por_mes[mes_anio] = {
                'total_ventas': 0,
                'total_compras': 0,
            }
        
        totals_por_mes[mes_anio]['total_ventas'] += venta['total_ventas']

    for compra in compras:
        fecha = compra['fechareg']
        mes_anio = fecha.strftime('%B %Y')
        
        if mes_anio not in totals_por_mes:
            totals_por_mes[mes_anio] = {
                'total_ventas': 0,
                'total_compras': 0,
            }
        
        totals_por_mes[mes_anio]['total_compras'] += compra['total_compras']
    
    # Llenar los datos en el formato adecuado para Chart.js
    for mes_anio, totals in totals_por_mes.items():
        data['labels'].append(mes_anio.capitalize())  # Capitalizar el mes
        data['ventas'].append(totals['total_ventas'])
        data['compras'].append(totals['total_compras'])

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
