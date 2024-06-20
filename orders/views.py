import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from orders.models import Pedidos, DetallePedido, Productos
from tuiranfitgo.views import jwt_cookie_required, module_access_required

@jwt_cookie_required
@module_access_required('ventas')
def Home(request):
    pedidos = Pedidos.objects.all()
    return render(request, "ordersHome.html", {"pedidos": pedidos})

def cambiarEstadoPedido(request):
    if request.method == "GET":
        id_pedido = request.GET.get('pedido_id')
        pedido = Pedidos.objects.get(id_pedido=id_pedido)
        pedido.estado = "cancelado"
        pedido.save()
        return JsonResponse({'status': 'success'})

@jwt_cookie_required
@module_access_required('ventas')
def editarPedidoHome(request, id_pedido):
    pedido = Pedidos.objects.get(id_pedido=id_pedido)
    detalle = DetallePedido.objects.filter(id_pedido=pedido)
    detalles = []

    for item in detalle:
        producto = Productos.objects.get(id_producto=item.id_producto.id_producto)
        imagen_data = producto.iProductImg.decode('utf-8') if producto.iProductImg else None
        sabores = producto.sabor.split(',') if producto.sabor else []
        stock = producto.cantidad
        detalles.append({
            'detalle': item,
            'imagen_data': imagen_data,
            'sabores': sabores,
            'stock': stock,
        })

    return render(request, 'editOrder.html', {
        "pedido": pedido,
        "detalles": detalles
    })

@csrf_exempt
def editarPedido(request):
    if request.method == 'POST':
        try:
            datos_pedido = json.loads(request.body)
            detalles_pedido = datos_pedido.get('detalles')
            id_pedido = datos_pedido.get('dataIdPedido')
            total_pedido = datos_pedido.get('total_pedido')

            pedido = Pedidos.objects.get(id_pedido=id_pedido)
            pedido.total_pedido = total_pedido
            pedido.save()

            ids_detalles_actuales = [detalle['id_detalle'] for detalle in detalles_pedido]

            DetallePedido.objects.filter(id_pedido=pedido).exclude(id_detallepedido__in=ids_detalles_actuales).delete()

            for detalle in detalles_pedido:
                detalle_pedido = DetallePedido.objects.get(id_detallepedido=detalle['id_detalle'])
                detalle_pedido.sabor = detalle['sabor']
                detalle_pedido.cantidad = detalle['cantidad']
                detalle_pedido.precio_tot = detalle['total_producto']
                detalle_pedido.save()

            response_data = {'success': True}
            return JsonResponse(response_data)
        except Exception as e:
            response_data = {'success': False, 'error_message': str(e)}
            return JsonResponse(response_data, status=500)

def detalles_pedido(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_pedido = request.GET.get('pedido_id')
        if id_pedido:
            try:
                pedido = Pedidos.objects.get(id_pedido=id_pedido)
                detalles_pedido = DetallePedido.objects.filter(id_pedido=id_pedido)
                detalles_data = []

                for detalle in detalles_pedido:
                    detalle_data = {
                        'producto': detalle.id_producto.nombre_producto,
                        'cantidad': detalle.cantidad,
                        'sabor': detalle.sabor,
                        'precio_uni': detalle.precio_uni,
                        'precio_tot': detalle.precio_tot,
                    }
                    detalles_data.append(detalle_data)

                data = {
                    'fecha_pedido': pedido.fecha_pedido,
                    'cliente': pedido.id_cliente.nombres + ' ' + pedido.id_cliente.apellidos,
                    'estado': pedido.estado,
                    'documento': pedido.id_cliente.documento,
                    'total_pedido': pedido.total_pedido,
                    'detalles': detalles_data
                }
                return JsonResponse({'success': data})
            except Pedidos.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': f'Pedido con ID {id_pedido} no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de Pedido no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})