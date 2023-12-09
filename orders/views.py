from django.http import JsonResponse
from django.shortcuts import render
from orders.models import Pedidos, DetallePedido, Clientes, Detalleventa, Ventas, Productos
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



from django.shortcuts import render
from .models import Pedidos, DetallePedido, Productos
@jwt_cookie_required
@module_access_required('ventas')
def editarPedido(request, id_pedido):
    if request.method == 'POST':
        # Aquí iría la lógica para manejar la actualización del pedido
        pass

    # Obtener el pedido y sus detalles
    pedidos = Pedidos.objects.get(id_pedido=id_pedido)
    detalle = DetallePedido.objects.filter(id_pedido=pedidos)

    detalles = []

    for item in detalle:
        producto = Productos.objects.get(id_producto=item.id_producto.id_producto)
        imagen_data = producto.iProductImg.decode('utf-8') if producto.iProductImg else None
        sabores = producto.sabor.split(',') if producto.sabor else []
        # Suponiendo que el modelo Productos tiene un campo 'stock'
        stock = producto.cantidad
        detalles.append({
            'detalle': item,
            'imagen_data': imagen_data,
            'sabores': sabores,
            'stock': stock 
        })


    return render(request, 'editOrder.html', {
        "pedidos": pedidos,
        "detalles": detalles
    })





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
