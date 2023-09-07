from django.http import JsonResponse
from django.shortcuts import render
from sales.models import Clientes, Detalleventa, Ventas, Productos


def Home(request):
    ventas = Ventas.objects.all()
    return render(request, "salesHome.html", {"ventas": ventas})


from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# def crear_venta(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         # Imprimir los datos en la consola del servidor
#         print(data)
        
#         # Ahora, 'data' contendrá el JSON enviado desde AJAX
#         # Puedes acceder a los datos como un diccionario de Python
#         # Por ejemplo, data['campo'] para acceder a un campo específico
#         return JsonResponse({'success': True})
    
#     # Manejar solicitudes GET u otros métodos HTTP según sea necesario
#     return render(request, "createSales.html")


def crear_venta(request):
    if request.method == 'POST':
        documento = request.POST.get('documento')
        producto = request.POST.get('producto')
        precioUnidad = request.POST.get('precioUnidad')
        cantidad = request.POST.get('cantidad')
        precioTotal = request.POST.get('precioTotal')

        # Imprime los datos en la consola del servidor
        print(f'Documento del Cliente: {documento}')
        print(f'Producto: {producto}')
        print(f'Precio Unitario: {precioUnidad}')
        print(f'Cantidad: {cantidad}')
        print(f'Total: {precioTotal}')

        # Retorna una respuesta JSON con un mensaje de éxito
        response_data = {
            'success': True,
            'message': 'Venta creada con éxito.',
            # Puedes agregar más datos procesados aquí si es necesario
        }
        return JsonResponse(response_data)

    return render(request, 'createSales.html')


def buscar_documentos(request):
    q = request.GET.get("q", "")
    documentos = Clientes.objects.filter(documento__contains=q).values_list(
        "documento", flat=True
    )

    nombre_cliente = ""
    if documentos:
        primer_documento = documentos[0]
        cliente = Clientes.objects.filter(documento=primer_documento).first()
        if cliente:
            nombre_cliente = f"{cliente.nombres} {cliente.apellidos}"

    return JsonResponse(
        {"documentos": list(documentos), "nombre_cliente": nombre_cliente}
    )


def buscar_productos(request):
    q = request.GET.get("q", "")
    productos = Productos.objects.filter(nombre_producto__icontains=q).values_list(
        "nombre_producto", flat=True
    )
    return JsonResponse({"productos": list(productos)})


def obtener_precio(request):
    nombre_producto = request.GET.get(
        "nombre_producto", None
    )  # Obtiene el valor de 'nombre_producto' de la solicitud GET
    if nombre_producto is not None:
        producto = Productos.objects.get(nombre_producto=nombre_producto)
        precio = producto.precio
        return JsonResponse({"precio": precio})
    else:
        return JsonResponse(
            {"error": 'Parámetro "nombre_producto" no proporcionado en la solicitud'},
            status=400,
        )


def obtener_nombre(request):
    nombre_producto = request.GET.get(
        "nombre_producto", None
    )  # Obtiene el valor de 'nombre_producto' de la solicitud GET
    if nombre_producto is not None:
        try:
            producto = Productos.objects.get(nombre_producto=nombre_producto)
            precio = producto.precio
            return JsonResponse({"precio": precio})
        except Productos.DoesNotExist:
            return JsonResponse({"error": "Producto no encontrado"}, status=404)
    else:
        return JsonResponse(
            {"error": 'Parámetro "nombre_producto" no proporcionado en la solicitud'},
            status=400,
        )


# def obtener_precio_producto(request, nombreProducto):
#     try:
#         producto = Productos.objects.get(nombre_producto=nombreProducto)
#         precio = producto.precio
#         return JsonResponse({'precio': precio})
#     except Productos.DoesNotExist:
#         return JsonResponse({'error': 'Producto no encontrado'}, status=404)
#     else:
#         return JsonResponse({'error': 'Parámetro "nombre_producto" no proporcionado en la solicitud'}, status=400)
