import math
from django.http import JsonResponse
from django.shortcuts import render,  get_object_or_404
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
        totalVenta = data.get('totalVenta', '')
        productos = data.get('productos', [])

        cliente = Clientes.objects.filter(documento=documento).first()
        venta = Ventas.objects.create(id_cliente=cliente, totalVenta=totalVenta)
        for producto_datos in productos:
            nombre_producto = producto_datos['nombre']
            cantidad_vendida = producto_datos['cantidad']

            producto = Productos.objects.get(nombre_producto=nombre_producto)

            if producto:
                producto.cantidad -= cantidad_vendida
                producto.save()

            Detalleventa.objects.create(
                id_producto=producto,
                id_venta=venta,
                cantidad=cantidad_vendida,
                precio_uni=producto_datos['precioUnidad'],
                precio_tot=producto_datos['precioTotal']
            )
        response_data = {'success': True}  
        return JsonResponse(response_data)

    return render(request, 'createSales.html')

    
from django.db.models import Q

@csrf_exempt
def editar_venta(request, id_venta):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            documento = data.get('documento', '')
            totalVenta = data.get('totalVenta', 0)
            productos = data.get('productos', [])

            venta = Ventas.objects.get(id_venta=id_venta)

            if documento:
                cliente = Clientes.objects.get(documento=documento)
                venta.id_cliente = cliente
            venta.totalVenta = totalVenta
            venta.save()

            productos_nuevos = []
            productos_actualizar = []
            for producto in productos:
                if producto["idDetalle"] is None or producto["idDetalle"] == "":
                    productos_nuevos.append(producto)
                else:
                    productos_actualizar.append(producto)
                    
            detalles = Detalleventa.objects.filter(id_venta=venta)
            
            idDetalles_faltantes = [detalle.id_detalleventa for detalle in detalles if detalle.id_detalleventa not in [producto["idDetalle"] for producto in productos]]

            Detalleventa.objects.filter(id_detalleventa__in=idDetalles_faltantes).delete()

            for productoDatos in productos_actualizar:
                nombre_producto = productoDatos["nombre"]
                id_detalle = productoDatos["idDetalle"]
                detalle = Detalleventa.objects.get(id_detalleventa=id_detalle)
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
                    Detalleventa.objects.create(
                    id_producto=producto,
                    id_venta=venta,
                    cantidad=productoDatos["cantidad"],
                    precio_uni=productoDatos["precioUnidad"],
                    precio_tot=productoDatos["precioTotal"]
                )
                except Exception as e:
                    print(f"Error al guardar detalle: {str(e)}")



            response_data = {'success': True}
        except Exception as e:
            response_data = {'success': False, 'error_message': str(e)}
        return JsonResponse(response_data)

    venta = Ventas.objects.get(id_venta=id_venta)
    detalles = Detalleventa.objects.filter(id_venta=id_venta)
    return render(request, 'editSales.html', {"detalles": detalles, "venta": venta})


           
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


def validar_producto(request):
    nombre_producto = request.GET.get("nombre_producto", "")
    producto_existe = Productos.objects.filter(nombre_producto=nombre_producto).exists()
    return JsonResponse({"existe": producto_existe})


def validar_cliente(request):
    documentoDato = request.GET.get("documentoDato", "")
    cliente_existe = Clientes.objects.filter(documento=documentoDato).exists()
    return JsonResponse({"existe": cliente_existe})

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
