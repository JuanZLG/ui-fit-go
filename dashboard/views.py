from django.shortcuts import render

# Create your views here.

def Entrance(request):
    return render(request, 'tgoEntrance.html')

def Home(request):
    return render(request, 'dashboard.html')

def UserGuide(request):
    return render(request, 'manual.html')

from django.http import JsonResponse
from .models import Compras, Ventas, Clientes, Proveedores
from django.db.models import Sum


# En tu archivo views.py




from django.http import JsonResponse
from .models import Clientes

def contar_clientes_activos(request):
    total_clientes = Clientes.objects.count()
    print(total_clientes)
    return JsonResponse({'total_clientes': total_clientes})






def calcular_total_compras(request):
    total_compras = Compras.objects.aggregate(total=Sum('totalCompra'))['total']
    return JsonResponse({'total_compras': total_compras})

  # Ajusta esto para que coincida con tu modelo de ventas

def calcular_total_ventas(request):
    # Calcula el total de ventas desde tu modelo
    total_ventas = Ventas.objects.aggregate(total_ventas=Sum('totalVenta'))['total_ventas'] 
    
    # Devuelve el total de ventas en formato JSON
    return JsonResponse({'total_ventas': total_ventas})


import locale

# Define el idioma y la ubicación para Colombia (español)
locale.setlocale(locale.LC_TIME, 'es_CO.utf8')

def obtener_datos_ventas_y_compras(request):
    # Obtén los datos de ventas y compras
    ventas = Ventas.objects.values('fechareg').annotate(total_ventas=Sum('totalVenta')).order_by('fechareg')
    compras = Compras.objects.values('fechareg').annotate(total_compras=Sum('totalCompra')).order_by('fechareg')

    # Creamos un diccionario para almacenar los totales de ventas y compras por mes
    data = {
        'labels': [],  # Lista para almacenar los meses
        'ventas': [],  # Lista para almacenar las ventas
        'compras': [],  # Lista para almacenar las compras
    }

    # Diccionario para realizar un seguimiento de los totales por mes
    totals_por_mes = {}

    # Procesar ventas
    for venta in ventas:
        fecha = venta['fechareg']
        mes_anio = fecha.strftime('%B %Y')
        
        if mes_anio not in totals_por_mes:
            totals_por_mes[mes_anio] = {
                'total_ventas': 0,
                'total_compras': 0,
            }
        
        totals_por_mes[mes_anio]['total_ventas'] += venta['total_ventas']
    
    # Procesar compras
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

from django.http import JsonResponse
from .models import Ventas  # Asegúrate de importar tu modelo de Ventas

from django.http import JsonResponse
from .models import Productos  # Asegúrate de importar tu modelo de Productos

from django.http import JsonResponse
from .models import Productos

def obtener_top_productos(request):
    try:
        # Obtén los 3 productos más vendidos desde tu modelo Productos.
        productos = Productos.objects.order_by('-cantidad')[:3]

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


















