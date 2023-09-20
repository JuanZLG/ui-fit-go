from django.shortcuts import render, redirect, get_object_or_404
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

def catHome(request):
    categories = Categorias.objects.all()
    return render(request, 'categoriesHome.html', {"cats":categories}) 

def brandHome(request):
    brands = Marcas.objects.all()
    return render(request, 'brandsHome.html', {"pbrands":brands}) 

def createProduct(request):
    marcas = Marcas.objects.all()
    categorias = Categorias.objects.all()
    
    if request.method == 'POST':
        nombre = request.POST['iNombre']
        descripcion = request.POST['iDescripcion']
        cantidad = request.POST['iCantidad']
        fechavencimiento = request.POST['iFechaven']
        sabor = request.POST['iSabor']
        tamano = request.POST['iServices']
        precio = request.POST['iPrice']   
        categoria = request.POST['iCategoria']
        marca=request.POST['iMarca']
        
        m = Marcas.objects.get(id_marca=marca)
        c = Categorias.objects.get(id_categoria=categoria)
        product = Productos.objects.all()

        Productos.objects.create(id_categoria=c,id_marca=m, nombre_producto=nombre, descripcion=descripcion, cantidad=cantidad, fechaven=fechavencimiento, sabor=sabor, presentacion=tamano, precio=precio)
        return JsonResponse({'success': True})
    return render(request, 'createProducts.html', {"marcas":marcas,"categorias":categorias})


def editProduct(request, id_producto):
    marcas = Marcas.objects.all()
    categorias = Categorias.objects.all()
    
    if request.method == 'POST':
        category = request.POST['iCategoria']
        brand = request.POST['iMarca']
        name = request.POST['iNombre']
        desc = request.POST['iDescripcion']
        vdate = request.POST['iFechaven']
        cant = request.POST['iCantidad']
        flavor = request.POST['iSabor']
        services = request.POST['iServices']
        pPrice = request.POST['iPrice']
        
        m = Marcas.objects.get(id_marca=brand)
        c = Categorias.objects.get(id_categoria=category)
        
        Productos.objects.filter(id_producto=id_producto).update(
            id_categoria=c,
            id_marca=m,
            nombre_producto=name,
            descripcion=desc,
            fechaven=vdate,
            cantidad=cant,
            sabor=flavor,
            presentacion=services,
            precio=pPrice
        )
        
        response_data = {'success': True}
        return JsonResponse(response_data)    
    products = Productos.objects.get(id_producto=id_producto)
    products.precio = int(products.precio)
    return render(request, 'editProducts.html', {"Product":products, "marcas":marcas,"categorias":categorias}) 

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

def verDetallesProducto(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_producto = request.GET.get('producto_id')
        
        if id_producto:
            try:
                producto = Productos.objects.get(id_producto=id_producto)
                # Si el producto se encuentra
                data = {
                    'nombre_producto': producto.nombre_producto,
                    'descripcion': producto.descripcion,
                    'cantidad': producto.cantidad,
                    'sabor': producto.sabor,
                }
                return JsonResponse({'success': data})
            except Productos.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de producto no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})
