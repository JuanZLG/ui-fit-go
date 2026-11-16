import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from orders.models import Pedidos, DetallePedido, Clientes, Detalleventa, Ventas, Productos
from tuiranfitgo.views import jwt_cookie_required, module_access_required
from django.db import transaction
from tuiranfitgo.inventory import StockError, DatosInvalidos, entero_positivo, nombre_imagen

@jwt_cookie_required
@module_access_required('ventas')
def Home(request):
    pedidos = Pedidos.objects.all()
    return render(request, "ordersHome.html", {"pedidos": pedidos})



@jwt_cookie_required
@module_access_required('ventas')
def cambiarEstadoPedido(request):
    if request.method != "GET":
        return JsonResponse({'status': 'error', 'message': 'Solicitud no válida.'}, status=405)
    pedido = Pedidos.objects.filter(pk=request.GET.get('pedido_id') or 0).first()
    if pedido is None:
        return JsonResponse({'status': 'error', 'message': 'Pedido no encontrado.'}, status=404)
    if pedido.estado == 'confirmado':
        return JsonResponse({'status': 'error',
                             'message': 'El pedido ya fue confirmado en una venta. Anula la venta para cancelarlo.'})
    pedido.estado = "cancelado"
    pedido.save(update_fields=['estado'])
    return JsonResponse({'status': 'success'})



@jwt_cookie_required
@module_access_required('ventas')
def editarPedidoHome(request, id_pedido):
    pedido = Pedidos.objects.get(id_pedido=id_pedido)
    detalle = DetallePedido.objects.filter(id_pedido=pedido)
    detalles = []

    for item in detalle:
        producto = Productos.objects.get(id_producto=item.id_producto.id_producto)
        imagen_data = nombre_imagen(producto.iProductImg) or None
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
@jwt_cookie_required
@module_access_required('ventas')
def editarPedido(request):
    """Edita las cantidades de un pedido en proceso validando inventario y recalculando totales."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error_message': 'Solicitud no válida.'}, status=405)
    try:
        datos = json.loads(request.body)
        detalles = datos.get('detalles')
        id_pedido = entero_positivo(datos.get('dataIdPedido'), 'pedido')
        if not isinstance(detalles, list) or not detalles:
            raise DatosInvalidos('El pedido debe conservar al menos un producto.')

        with transaction.atomic():
            pedido = Pedidos.objects.select_for_update().get(id_pedido=id_pedido)
            if pedido.estado != 'en proceso':
                raise DatosInvalidos(f'El pedido está {pedido.estado} y ya no se puede modificar.')

            ids_conservados, total, cambios = [], 0.0, []
            for detalle in detalles:
                id_detalle = entero_positivo(detalle.get('id_detalle'), 'detalle')
                cantidad = entero_positivo(detalle.get('cantidad'), 'cantidad')
                det = DetallePedido.objects.select_related('id_producto').filter(
                    id_detallepedido=id_detalle, id_pedido=pedido).first()
                if det is None:
                    raise DatosInvalidos('Uno de los productos no pertenece a este pedido.')
                disponible = max(det.id_producto.cantidad, 0)
                if cantidad > disponible:
                    raise StockError(f'Stock insuficiente de «{det.id_producto.nombre_producto}»: '
                                     f'hay {disponible} disponible(s) y pediste {cantidad}.')
                subtotal = det.precio_uni * cantidad          # el total se calcula en el servidor
                total += subtotal
                ids_conservados.append(id_detalle)
                cambios.append((det, str(detalle.get('sabor', det.sabor))[:50], cantidad, subtotal))

            DetallePedido.objects.filter(id_pedido=pedido).exclude(id_detallepedido__in=ids_conservados).delete()
            for det, sabor, cantidad, subtotal in cambios:
                det.sabor, det.cantidad, det.precio_tot = sabor, cantidad, subtotal
                det.save()
            pedido.total_pedido = total
            pedido.save(update_fields=['total_pedido'])

        return JsonResponse({'success': True})
    except (DatosInvalidos, StockError) as e:
        return JsonResponse({'success': False, 'error_message': str(e)}, status=400)
    except Pedidos.DoesNotExist:
        return JsonResponse({'success': False, 'error_message': 'Pedido no encontrado.'}, status=404)
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        return JsonResponse({'success': False, 'error_message': 'Los datos enviados no son válidos.'}, status=400)




@jwt_cookie_required
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
