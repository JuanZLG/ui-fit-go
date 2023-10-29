from django.shortcuts import render

from .models import Productos, Marcas, Categorias


def Home(request):
    productos = Productos.objects.all()
    marcas = Marcas.objects.all()
    categorias = Categorias.objects.all()

    return render(request, 'pageHome.html', {"productos":productos, "marcas":marcas, "categorias":categorias}) 

def pageCatalog(request):
    productos = Productos.objects.all()
    marcas = Marcas.objects.all()
    categorias = Categorias.objects.all()

    return render(request, 'pageCatalog.html', {"productos":productos, "marcas":marcas, "categorias":categorias}) 

