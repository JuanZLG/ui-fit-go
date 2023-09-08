from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from sales.models import Clientes, Detalleventa, Ventas, Productos

def Home(request):
    ventas = Ventas.objects.all()
    return render(request, "salesHome.html", {"ventas": ventas})

# @csrf_exempt
# def crear_venta(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         documento = data.get('documento', '')
#         productos = data.get('productos', '')
        
#         # Buscar al cliente por su documento
#         cliente = Clientes.objects.filter(documento=documento).first()
        
#         if cliente:
#             # Crear una venta con el cliente encontrado
#             venta = Ventas.objects.create(id_cliente=cliente)
            
#             # Crear detalles de venta para cada producto
#             for producto_datos in productos:
#                 producto = Productos.objects.filter(nombre_producto=producto_datos['nombre']).first()
#                 if producto:
#                     detalle = Detalleventa.objects.create(
#                         id_producto=producto,
#                         id_venta=venta,
#                         cantidad=producto_datos['cantidad'],
#                         precio_uni=producto_datos['precioUnidad'],
#                         precio_tot=producto_datos['precioTotal']
#                     )
#                 else:
#                     # Manejar el caso donde el producto no existe
#                     # Puedes mostrar un mensaje de error o tomar otra acción apropiada.
#                     pass

#             response_data = {'success': True}
#         else:
#             # Manejar el caso donde el cliente no existe
#             # Puedes mostrar un mensaje de error o tomar otra acción apropiada.
#             response_data = {'success': False, 'message': 'Cliente no encontrado'}

#         return JsonResponse(response_data)

#     return render(request, 'createSales.html')


@csrf_exempt
def crear_venta(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        documento = data.get('documento', '')
        productos = data.get('productos', [])
        print(documento)
        cliente = Clientes.objects.filter(documento=documento).first()
        print(cliente)

        venta = Ventas.objects.create(id_cliente=cliente)
        for producto_datos in productos:
            producto = Productos.objects.filter(nombre_producto=producto_datos['nombre']).first()
            detalle = Detalleventa.objects.create(
                id_producto=producto,
                id_venta=venta,
                cantidad=producto_datos['cantidad'],
                precio_uni=producto_datos['precioUnidad'],
                precio_tot=producto_datos['precioTotal']
            )

        response_data = {'success': True}  
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
