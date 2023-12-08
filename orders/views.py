from django.http import JsonResponse
from django.shortcuts import render
from orders.models import Pedidos, Clientes, Detalleventa, Ventas, Productos

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



def editarPedido(request, id_pedido):
    if request.method == 'POST':
        pass
        # nombre = request.POST.get('nombre_proveedor')
        # telefono = request.POST.get('telefono')
        # correo = request.POST.get('correo')
        # direccion = request.POST.get('direccion')
        # informacion_adicional = request.POST.get('informacion')
        # tipo_documento = request.POST.get('tipoIdentificacion')
        # numero_documento_nit = request.POST.get('identificacion')
        # Proveedores.objects.filter(id_proveedor=id_proveedor).update(
        #     nombre_proveedor=nombre,
        #     telefono=telefono,
        #     correo=correo,
        #     direccion=direccion,
        #     informacion_adicional=informacion_adicional,
        #     tipo_documento=tipo_documento,
        #     numero_documento_nit=numero_documento_nit
        # )
        # response_data = {'success': True}
        # return JsonResponse(response_data)    
    pedidos = Pedidos.objects.get(id_pedido=id_pedido)
    return render(request, 'editOrder.html', {"pedidos":pedidos})