from django.http import JsonResponse
from django.shortcuts import render
from sales.models import Clientes, Detalleventa, Ventas, Productos

def Home(request):
    ventas = Ventas.objects.all()
    return render(request, 'salesHome.html', {"ventas":ventas})  



def crear_venta(request):
    # if request.method == 'POST':
    #     nombre = request.POST['nombre_proveedor']
    #     telefono = request.POST['telefono']
    #     correo = request.POST['correo']
    #     proveedor = Proveedores.objects.create(nombre_proveedor=nombre, telefono=telefono, correo=correo)
    #     return JsonResponse({'success': True})
    return render(request, 'createSales.html')



def buscar_documentos(request):
    q = request.GET.get('q', '')
    documentos = Clientes.objects.filter(documento__contains=q).values_list('documento', flat=True)
    return JsonResponse({'documentos': list(documentos)})


def buscar_productos(request):
    q = request.GET.get('q', '')
    productos = Productos.objects.filter(nombre_producto__icontains=q).values_list('nombre_producto', flat=True)
    return JsonResponse({'productos': list(productos)})


from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def obtener_precio_producto(request):
    nombre_producto = request.GET.get('nombre_producto', None)  # Obtiene el valor de 'nombre_producto' de la solicitud GET

    if nombre_producto is not None:
        try:
            producto = Productos.objects.get(nombre_producto=nombre_producto)
            precio = producto.precio  
            return JsonResponse({'precio': precio})
        except Productos.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'Parámetro "nombre_producto" no proporcionado en la solicitud'}, status=400)
