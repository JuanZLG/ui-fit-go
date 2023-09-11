from django.shortcuts import render, redirect
from .models import Productos
from django.http import JsonResponse
from django.urls import reverse
from products.models import Productos, Categorias, Marcas


def Home(request):
    product = Productos.objects.all()
    return render(request, 'productsHome.html', {"Products":product}) 


def createProduct(request):
    marcas = Marcas.objects.all()
    categorias = Categorias.objects.all()
    
    if request.method == 'POST':
        nombre = request.POST['nombre_producto']
        descripcion = request.POST['descripcion']
        cantidad = request.POST['cantidad']
        fechavencimiento = request.POST['fechaven']
        sabor = request.POST['sabor']
        tamano = request.POST['presentacion']
        precio = request.POST['precio']   
        categoria = request.POST['categoria']
        marca=request.POST['marca']
        
        m = Marcas.objects.filter(nombre_marca=marca)
        c = Categorias.objects.filter(id_categoria=categoria)
        product = Productos.objects.all()

        Productos.objects.create(id_categoria=c.id_categoria, id_marca=m.id_marca, nombre_categoria=nombre, descripcion=descripcion, cantidad=cantidad, fechaven=fechavencimiento, sabor=sabor, presentacion=tamano, precio=precio)
        return JsonResponse({'success': True})
    return render(request, 'productsHome.html', {"marcas":marcas,"categorias":categorias, "Products":product})

# def editProduct(request):
    