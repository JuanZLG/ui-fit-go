from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
import json
import logging  # Importa el módulo de registro
logger = logging.getLogger(__name__)

from .models import Compras, Detallecompra, Proveedores, Productos

def Home(request):
    compras = Compras.objects.all()
    return render(request, "purchasesHome.html", {"compras": compras})

@csrf_exempt
def crear_compra(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug("Datos JSON recibidos: %s", data)  # Registra los datos JSON recibidos
            proveedor_id = data.get('proveedor_id', '')
            productos = data.get('productos', [])

            # Validar los datos aquí según tus requisitos
            if not proveedor_id or not productos:
                return JsonResponse({'error': 'Datos no válidos'}, status=400)

            proveedor = Proveedores.objects.filter(id_proveedor=proveedor_id).first()
            compra = Compras.objects.create(id_proveedor=proveedor)
            
            for producto_datos in productos:
                producto = Productos.objects.filter(nombre_producto=producto_datos['nombre']).first()
                detalle = Detallecompra.objects.create(
                    id_producto=producto,
                    id_compra=compra,
                    cantidad=producto_datos['cantidad'],
                    precio_uni=producto_datos['precioUnidad'],
                    precio_tot=producto_datos['precioTotal']
                )

            response_data = {'success': True}
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            logger.error("Error al decodificar datos JSON: %s", request.body)  # Registra el error de datos JSON no válidos
            return JsonResponse({f'error': 'Datos JSON no válidos {request.body}'}, status=400 )

    return render(request, 'createPurchases.html')


def buscar_proveedores(request):
    q = request.GET.get("q", "")
    proveedores = Proveedores.objects.filter(nombre_proveedor__icontains=q).values_list(
        "nombre_proveedor", flat=True
    )
    return JsonResponse({"proveedores": list(proveedores)})

def validar_producto(request):
    nombre_producto = request.GET.get("nombre_producto", "")
    producto_existe = Productos.objects.filter(nombre_producto=nombre_producto).exists()
    return JsonResponse({"existe": producto_existe})
def validar_proveedor(request):
    proveedor_id = request.GET.get("proveedor_id", "")
    proveedor_existe = Proveedores.objects.filter(id_proveedor=proveedor_id).exists()
    return JsonResponse({"existe": proveedor_existe})

def obtener_precio(request):
    nombre_producto = request.GET.get(
        "nombre_producto", None
    )
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
    )
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

def detalles_compra(request, compra_id):
    detalles = Detallecompra.objects.filter(id_compra=compra_id)
    detalles_data = []

    for detalle in detalles:
        producto = Productos.objects.get(id_producto=detalle.id_producto)
        detalle_data = {
            'producto': producto.nombre_producto,
            'cantidad': detalle.cantidad,
            'precio_uni': detalle.precio_uni,
            'precio_tot': detalle.precio_tot,
        }

        detalles_data.append(detalle_data)

    return JsonResponse({'detallecompra': detalles_data})

def cambiarEstado(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        compra_id = request.GET.get('compra_id')
        nuevo_estado = request.GET.get('nuevo_estado')
        
        try:
            compra = Compras.objects.get(id_compra=compra_id)
            compra.estado = int(nuevo_estado)
            compra.save()
            
            return JsonResponse({'status': 'success'})
        except Compras.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Registro de compra no encontrado'})
        
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})