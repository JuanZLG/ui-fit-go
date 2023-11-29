from django.shortcuts import render
from orders.models import Pedidos, Clientes, Detalleventa, Ventas, Productos

def Home(request):
    pedidos = Pedidos.objects.all()
    return render(request, "ordersHome.html", {"pedidos": pedidos})
