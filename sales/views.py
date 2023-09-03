from django.shortcuts import render


# from sales.models import Ventas
from sales.models import Clientes, Detalleventa, Ventas
def Home(request):
    ventas = Ventas.objects.all()
    return render(request, 'salesHome.html', {"ventas":ventas})  


# def Home(request):
#     return render(request, 'salesHome.html') 

