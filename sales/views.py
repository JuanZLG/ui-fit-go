from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
import json
from sales.models import Clientes, Detalleventa, Ventas, Productos

def Home(request):
    ventas = Ventas.objects.all()
    return render(request, "salesHome.html", {"ventas": ventas})

@csrf_exempt
def crear_venta(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        documento = data.get('documento', '')
        productos = data.get('productos', [])

        cliente = Clientes.objects.filter(documento=documento).first()
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


def detalles_venta(request, venta_id):
    detalles = Detalleventa.objects.filter(id_venta=venta_id)
    detalles_data = []

    for detalle in detalles:
        # Cambia detalle.id_producto por detalle.id_producto_id si es un ForeignKey
        producto = Productos.objects.get(id_producto=detalle.id_producto)
        detalle_data = {
            'producto': producto.nombre_producto,
            'cantidad': detalle.cantidad,
            'precio_uni': detalle.precio_uni,
            'precio_tot': detalle.precio_tot,
        }

        detalles_data.append(detalle_data)

    return JsonResponse({'detalleventa': detalles_data})


def cambiarEstado(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        venta_id = request.GET.get('venta_id')
        nuevo_estado = request.GET.get('nuevo_estado')
        
        try:
            venta = Ventas.objects.get(id_venta=venta_id)
            venta.estado = int(nuevo_estado)
            venta.save()
            
            return JsonResponse({'status': 'success'})
        except Clientes.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Registros de venta no encontrado'})
        
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})






