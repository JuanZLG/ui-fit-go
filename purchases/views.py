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
            logger.debug("Datos JSON recibidos: %s", data)

            proveedor_nombre = data.get('proveedor', '')
            totalCompra = data.get('totalCompra', '')

            productos = data.get('productos', [])

            if not proveedor_nombre:
                return JsonResponse({'error': 'El nombre del proveedor es obligatorio.'}, status=400)

            if not productos:
                return JsonResponse({'error': 'Debe agregar al menos un producto a la compra.'}, status=400)

            proveedor = Proveedores.objects.filter(nombre_proveedor=proveedor_nombre).first()

            if not proveedor:
                return JsonResponse({'error': 'Proveedor no encontrado en la base de datos.'}, status=400)

            compra = Compras.objects.create(id_proveedor=proveedor, totalCompra=totalCompra)

            for producto_datos in productos:
                producto = Productos.objects.filter(nombre_producto=producto_datos['nombre']).first()

                if not producto:
                    return JsonResponse({'error': f'Producto "{producto_datos["nombre"]}" no encontrado en la base de datos.'}, status=400)

                detalle = Detallecompra.objects.create(
                    id_producto=producto,
                    id_compra=compra,
                    cantidad=producto_datos['cantidad'],
                    precio_uni=producto_datos['precioUnidad'],
                    precio_tot=producto_datos['precioTotal']
                )

                # Incrementar la cantidad en stock del producto
                producto.cantidad += producto_datos['cantidad']
                producto.save()

            response_data = {'success': True}
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            logger.error("Error al decodificar datos JSON: %s", request.body)
            return JsonResponse({'error': 'Datos JSON no válidos.'}, status=400)

        except Exception as e:
            logger.error("Error al crear la compra: %s", str(e))
            return JsonResponse({'error': 'Error al crear la compra. Intente nuevamente más tarde.'}, status=500)

    return render(request, 'createPurchases.html')




def buscar_proveedores(request):
    q = request.GET.get("q", "")
    proveedores = Proveedores.objects.filter(nombre_proveedor__icontains=q).values_list(
        "nombre_proveedor", flat=True
    )
    return JsonResponse({"proveedores": list(proveedores)})


def buscar_productos(request):
    q = request.GET.get("q", "")
    productos = Productos.objects.filter(nombre_producto__icontains=q).values_list(
        "nombre_producto", flat=True
    )
    return JsonResponse({"productos": list(productos)})
def validar_producto(request):
    nombre_producto = request.GET.get("nombre_producto", "")
    producto_existe = Productos.objects.filter(nombre_producto=nombre_producto).exists()
    return JsonResponse({"existe": producto_existe})





def validar_proveedor(request):
    nombre_proveedor = request.GET.get("nombreProveedor", "")
    
    if nombre_proveedor:  # Verifica si nombreProveedor no está vacío
        proveedor_existe = Proveedores.objects.filter(nombre_proveedor__iexact=nombre_proveedor).exists()
        return JsonResponse({"existe": proveedor_existe})
    else:
        return JsonResponse({"existe": False})





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


def obtener_detalles_compra(request, compra_id):
    detalles_compra = Detallecompra.objects.filter(id_compra=compra_id)

    detalles = [
        {
            'producto': detalle.id_producto.nombre_producto,
            'precioUnitario': str(detalle.precio_uni),
            'totalProducto': str(detalle.precio_tot),
            'cantidad': detalle.cantidad
            
        }
        for detalle in detalles_compra
    ]

    compra = detalles_compra.first().id_compra 
    datos_generales = {
        'proveedor': compra.id_proveedor.nombre_proveedor,
        'fechaRegistro': compra.fechareg,
        'estado': 'Activo' if compra.estado == 1 else 'Inactivo',
    }

    respuesta = {
        'proveedor': datos_generales['proveedor'],
        'fechaRegistro': str(datos_generales['fechaRegistro']),
        'estado': datos_generales['estado'],
        'detalles': detalles,
    }

    return JsonResponse(respuesta)


@csrf_exempt
def editar_compra(request, id_compra):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Datos recibidos en la solicitud POST:", data)

            proveedor_nombre = data.get('proveedor', '')
            totalCompra = data.get('totalCompra', 0)
            productos = data.get('productos', [])

            compra = Compras.objects.get(id_compra=id_compra)

            if proveedor_nombre:
                proveedor = Proveedores.objects.get(nombre_proveedor=proveedor_nombre)
                compra.id_proveedor = proveedor
            compra.totalCompra = totalCompra
            compra.save()

            productos_nuevos = []
            productos_actualizar = []
            for producto in productos:
                if producto["idDetalle"] is None or producto["idDetalle"] == "":
                    productos_nuevos.append(producto)
                else:
                    productos_actualizar.append(producto)
                    
            detalles = Detallecompra.objects.filter(id_compra=compra)
            
            idDetalles_faltantes = [detalle.id_detallecompra for detalle in detalles if detalle.id_detallecompra not in [producto["idDetalle"] for producto in productos]]

            Detallecompra.objects.filter(id_detallecompra__in=idDetalles_faltantes).delete()

            for productoDatos in productos_actualizar:
                nombre_producto = productoDatos["nombre"]
                id_detalle = productoDatos["idDetalle"]
                detalle = Detallecompra.objects.get(id_detallecompra=id_detalle)
                producto = Productos.objects.get(nombre_producto=nombre_producto)
                try:
                    detalle.id_producto = producto
                    detalle.cantidad = productoDatos["cantidad"]
                    detalle.precio_uni = productoDatos["precioUnidad"]
                    detalle.precio_tot = productoDatos["precioTotal"]
                    detalle.save()
                except Exception as e:
                    print(f"Error al guardar detalle: {str(e)}")

            for productoDatos in productos_nuevos:
                nombre_producto = productoDatos["nombre"]
                producto = Productos.objects.get(nombre_producto=nombre_producto)
                try:
                    Detallecompra.objects.create(
                    id_producto=producto,
                    id_compra=compra,
                    cantidad=productoDatos["cantidad"],
                    precio_uni=productoDatos["precioUnidad"],
                    precio_tot=productoDatos["precioTotal"]
                )
                except Exception as e:
                    print(f"Error al guardar detalle: {str(e)}")



            response_data = {'success': True}
        except Exception as e:
            response_data = {'success': False, 'error_message': str(e)}
            print("Error en la vista editar_compra:", str(e))  # Imprimir cualquier error que ocurra

        return JsonResponse(response_data)

    compra = Compras.objects.get(id_compra=id_compra)
    detalles = Detallecompra.objects.filter(id_compra=id_compra)
    return render(request, 'editPurchases.html', {"detalles": detalles, "compra": compra})