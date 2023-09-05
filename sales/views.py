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



# def buscar_documentos(request):
#     q = request.GET.get('q', '')
#     documentos = Clientes.objects.filter(documento__contains=q).values_list('documento', flat=True)
#     return JsonResponse({'documentos': list(documentos)})



def buscar_documentos(request):
    q = request.GET.get('q', '')
    documentos = Clientes.objects.filter(documento__contains=q).values_list('documento', flat=True)
    
    nombre_cliente = ""
    if documentos:
        primer_documento = documentos[0]
        cliente = Clientes.objects.filter(documento=primer_documento).first()
        if cliente:
            nombre_cliente = f"{cliente.nombres} {cliente.apellidos}" 
    
    return JsonResponse({'documentos': list(documentos), 'nombre_cliente': nombre_cliente})


def buscar_productos(request):
    q = request.GET.get('q', '')
    productos = Productos.objects.filter(nombre_producto__icontains=q).values_list('nombre_producto', flat=True)
    return JsonResponse({'productos': list(productos)})




def obtener_precio(request):
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


def obtener_nombre(request):
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



# def obtener_precio_producto(request, nombreProducto):
#     try:
#         producto = Productos.objects.get(nombre_producto=nombreProducto)
#         precio = producto.precio  
#         return JsonResponse({'precio': precio})
#     except Productos.DoesNotExist:
#         return JsonResponse({'error': 'Producto no encontrado'}, status=404)
#     else:
#         return JsonResponse({'error': 'Parámetro "nombre_producto" no proporcionado en la solicitud'}, status=400)

