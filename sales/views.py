from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from sales.models import Clientes, Detalleventa, Ventas, Productos
from django.db.models import Q


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
    
    clientes = Clientes.objects.all()
    return render(request, 'createSales.html', {'clientes': clientes})


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

            detalles = Detalleventa.objects.filter(id_venta=venta)

            stock_actual = {}

            for detalle in detalles:
                producto = detalle.id_producto
                stock_actual.setdefault(producto.nombre_producto, producto.cantidad)

                for productoDatos in productos:
                    if productoDatos["idDetalle"] == detalle.id_detalleventa:
                        nueva_cantidad = productoDatos["cantidad"]
                        diferencia = nueva_cantidad - detalle.cantidad
                        detalle.cantidad = nueva_cantidad
                        detalle.save()

                        if detalle.estado != productoDatos["estado"]:                      
                            if detalle.estado == 1 and productoDatos["estado"] == 0:
                                producto.cantidad += nueva_cantidad
                            elif detalle.estado == 0 and productoDatos["estado"] == 1:
                                producto.cantidad -= nueva_cantidad

                        else:
                            producto.cantidad = stock_actual[producto.nombre_producto] - diferencia
                        
                        detalle.estado = productoDatos["estado"]
                        detalle.save()
                        producto.save()
                        break

            for productoDatos in productos:
                id_detalle = productoDatos["idDetalle"]
                if not Detalleventa.objects.filter(id_detalleventa=id_detalle).exists():
                    nombre_producto = productoDatos["nombre"]
                    nueva_cantidad = productoDatos["cantidad"]

                    producto = Productos.objects.get(nombre_producto=nombre_producto)

                    if producto:
                        producto.cantidad -= nueva_cantidad
                        producto.save()

                    detalle = Detalleventa.objects.create(
                        id_venta=venta,
                        id_producto=producto,
                        cantidad=nueva_cantidad,
                        precio_uni=productoDatos["precioUnidad"],
                        precio_tot=productoDatos["precioTotal"],
                    )


            response_data = {'success': True}
        except Exception as e:
            response_data = {'success': False, 'error_message': str(e)}

        return JsonResponse(response_data)

    venta = Ventas.objects.get(id_venta=id_venta)
    detalles = Detalleventa.objects.filter(id_venta=id_venta)
    return render(request, 'editSales.html', {"detalles": detalles, "venta": venta})

    

def buscar_cliente(request):
    nombre_cliente = request.GET.get("q", "")

    palabras_clave = nombre_cliente.split()
    clientes_encontrados = Clientes.objects.all()

    for palabra_clave in palabras_clave:
        clientes_encontrados = clientes_encontrados.filter(
            Q(nombres__icontains=palabra_clave) | Q(apellidos__icontains=palabra_clave)
        )

    resultados = [
        {
            "documento": cliente.documento,
            "nombre_cliente": f"{cliente.nombres} {cliente.apellidos}",
            "estado": cliente.estado,
        }
        for cliente in clientes_encontrados
    ]

    return JsonResponse({"resultados": resultados})



def buscar_productos(request):
    q = request.GET.get("q", "")
    productos = Productos.objects.filter(nombre_producto__icontains=q).values_list(
        "nombre_producto", flat=True
    )
    return JsonResponse({"productos": list(productos)})


def validar_cantidad(request):
    cantidad = request.GET.get("cantidad", "")
    nombre = request.GET.get("nombre", "")
    producto = Productos.objects.get(nombre_producto__iexact=nombre)
    if int(cantidad) > producto.cantidad:
        return JsonResponse({"suficiente": False})
    return JsonResponse({"suficiente": True})


           
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



def validar_producto(request):
    nombre_producto = request.GET.get("nombre_producto", "")
    producto_existe = Productos.objects.filter(nombre_producto=nombre_producto).exists()
    return JsonResponse({"existe": producto_existe})

def existencia_producto(request):
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


def cambiarEstado(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        venta_id = request.GET.get('venta_id')
        nuevo_estado = request.GET.get('nuevo_estado')
        
        venta = Ventas.objects.get(id_venta=venta_id)
        venta.estado = int(nuevo_estado)
        venta.save()

        detalles = Detalleventa.objects.filter(id_venta=venta_id)
        for detalle in detalles:
            producto = detalle.id_producto

            if venta.estado == 1: 
                detalle.estado = 1  
                producto.cantidad -= detalle.cantidad  
                producto.save()  

            else:  
                detalle.estado = 0  
                producto.cantidad += detalle.cantidad 
                producto.save()  

            detalle.save() 
        
        return JsonResponse({'status': 'success'})


def detalles_venta(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_venta = request.GET.get('venta_id')
        if id_venta:
            try:
                venta = Ventas.objects.get(id_venta=id_venta)
                detalles = Detalleventa.objects.filter(id_venta=id_venta)
                detalles_data = []

                for detalle in detalles:
                    producto = Productos.objects.get(id_producto=detalle.id_producto.id_producto)
                    detalle_data = {
                        'producto': producto.nombre_producto,
                        'cantidad': detalle.cantidad,
                        'precio_uni': detalle.precio_uni,
                        'precio_tot': detalle.precio_tot,
                    }
                    detalles_data.append(detalle_data)

                data = {
                    'fechareg': venta.fechareg,
                    'cliente': venta.id_cliente.nombres + ' ' + venta.id_cliente.apellidos,
                    'estado': venta.estado,
                    'documento': venta.id_cliente.documento,
                    'totalVenta': venta.totalVenta,
                    'detalles': detalles_data
                }
                return JsonResponse({'success': data})
            except Ventas.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Venta no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de Venta no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})
