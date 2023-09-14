from django.shortcuts import render, redirect
from .models import Productos
from django.urls import reverse
import json
from urllib.parse import parse_qs
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
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
    return render(request, 'createProducts.html', {"marcas":marcas,"categorias":categorias})


@csrf_exempt
def modifyProduct(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        form_data = request.POST.get('formData')
        form_data_dict = parse_qs(form_data)

        nombre_producto = form_data_dict.get('nombre_producto', [''])[0]
        descripcion = form_data_dict.get('descripcion', [''])[0]
        cantidad = form_data_dict.get('cantidad', [''])[0]
        fechaven = form_data_dict.get('fechaven', [''])[0]
        sabor = form_data_dict.get('sabor', [''])[0]
        presentacion = form_data_dict.get('presentacion', [''])[0]
        precio = form_data_dict.get('precio', [''])[0]

        Productos.objects.filter(id_producto=producto_id).update(
            nombre_producto=nombre_producto,
            descripcion=descripcion,
            cantidad=cantidad,
            fechaven=fechaven,
            sabor = sabor,
            presentacion = presentacion,
            precio=precio
        )

def cambiarEstadoDeProducto(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_producto = request.GET.get('producto_id')
        nuevo_estado = request.GET.get('nuevo_estado')
        try:
            producto = Productos.objects.get(id_producto=id_producto)
            producto.estado = int(nuevo_estado)
            producto.save()
            return JsonResponse({'status': 'success'})
        except Productos.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Producto no Encontrado'})
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})

