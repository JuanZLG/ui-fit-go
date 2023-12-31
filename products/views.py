import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Productos
from django.urls import reverse
from urllib.parse import parse_qs
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from products.models import Productos, Categorias, Marcas
import base64
from django.core.files.base import ContentFile
from tuiranfitgo.views import jwt_cookie_required, module_access_required


@jwt_cookie_required
@module_access_required('productos')
def Home(request):
    product = Productos.objects.all()
    return render(request, 'productsHome.html', {"Products":product}) 


@jwt_cookie_required
@module_access_required('productos')
def catHome(request):
    categories = Categorias.objects.all()
    return render(request, 'categoriesHome.html', {"cats":categories}) 

@jwt_cookie_required
@module_access_required('productos')
def brandHome(request):
    brands = Marcas.objects.all()
    return render(request, 'brandsHome.html', {"pbrands":brands}) 

@jwt_cookie_required
@module_access_required('productos')
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
        precioven = request.POST['iPubPrice']
        categoria = request.POST['iCategoria']
        marca = request.POST['iMarca']
        iProductImg = request.FILES['iProductImg']
        iInfoImg = request.FILES['iInfoImg']
        
        
        m = Marcas.objects.get(id_marca=marca)
        c = Categorias.objects.get(id_categoria=categoria)
        
        precio = precio.replace(',', '').replace('.', '')
        precio = float(precio)
        
        precioven = precioven.replace(',', '').replace('.', '')
        precioven = float(precioven)

        Productos.objects.create(
            id_categoria=c,
            id_marca=m,
            nombre_producto=nombre,
            descripcion=descripcion,
            cantidad=cantidad,
            fechaven=fechavencimiento,
            sabor=sabor,
            presentacion=tamano,
            precio=precio,
            precio_pub=precioven,
            iProductImg=iProductImg,
            iInfoImg=iInfoImg,
        )
        
        return JsonResponse({'success': True})
    
    return render(request, 'createProducts.html', {"marcas": marcas, "categorias": categorias})

@jwt_cookie_required
@module_access_required('productos')
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
        precioven = request.POST['iPubPrice']

        m = Marcas.objects.get(id_marca=brand)
        c = Categorias.objects.get(id_categoria=category)

        pPrice = pPrice.replace(',', '').replace('.', '')
        pPrice = int(pPrice)

        precioven = precioven.replace(',', '').replace('.', '')
        # precioven = float(precioven)

        iProductImg = request.FILES.get('iProductImg', None)
        iInfoImg = request.FILES.get('iInfoImg', None)

        productos = Productos.objects.filter(id_producto=id_producto)

        
        # products.precio = '{:,.0f}'.format(products.precio)

        if iProductImg:
            productos.update(iProductImg=iProductImg)
        if iInfoImg:
            productos.update(iInfoImg=iInfoImg)
        productos.update(
            id_categoria=c,
            id_marca=m,
            nombre_producto=name,
            descripcion=desc,
            fechaven=vdate,
            cantidad=cant,
            sabor=flavor,
            presentacion=services,
            precio=pPrice,
            precio_pub=precioven,
            estado=1
        )

        response_data = {'success': True}
        return JsonResponse(response_data)

    products = Productos.objects.get(id_producto=id_producto)
    products.precio_pub = int(products.precio_pub)
    products.precio = int(products.precio)
    
    if products.iInfoImg:
        if isinstance(products.iInfoImg, bytes):
            products.iInfoImg_name = products.iInfoImg.split(b'/')[-1].decode('utf-8')
        else:
            products.iInfoImg_name = products.iInfoImg.name.split('/')[-1]
    
    if products.iProductImg:
        if isinstance(products.iProductImg, bytes):
            products.iProductImg_name = products.iProductImg.split(b'/')[-1].decode('utf-8')
        else:
            products.iProductImg_name = products.iProductImg.name.split('/')[-1]


    return render(request, 'editProducts.html', {"Product": products, "marcas": marcas, "categorias": categorias})


def cambiarEstadoDeProducto(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_producto = request.GET.get('producto_id')
        nuevo_estado = request.GET.get('nuevo_estado')
        try:
            producto = Productos.objects.get(id_producto=id_producto)
            producto.estado = int(nuevo_estado)

            # Guardar solo el campo 'estado'
            producto.save(update_fields=['estado'])
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
                data = {
                    'categoria': producto.id_categoria.nombre_categoria,
                    'marca': producto.id_marca.nombre_marca,
                    'nombre_producto': producto.nombre_producto,
                    'descripcion': producto.descripcion,
                    'fechaven': producto.fechaven,
                    'cantidad': producto.cantidad,
                    'sabor': producto.sabor,
                    'status': producto.estado,
                    'servicios': producto.presentacion,
                    'precio_pub': producto.precio_pub,
                    'img': producto.iProductImg.decode('utf8')
                }
                return JsonResponse({'success': data})
            except Productos.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de producto no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})

@jwt_cookie_required
def crear_categoria(request):
    categorias = Categorias.objects.all()
    if request.method == 'POST':
        nombre_categoria = request.POST.get('nombre_categoria')
        Categorias.objects.create(nombre_categoria=nombre_categoria)
        response_data = {"success": True}
        return JsonResponse(response_data)
    
    return render(request, 'productsHome.html', {'categorias': categorias})

@jwt_cookie_required
def crear_marca(request):
    marcas = Marcas.objects.all()
    if request.method == 'POST':
        nombre_marca = request.POST.get('nombre_marca')
        Marcas.objects.create(nombre_marca=nombre_marca)
        response_data = {"success": True}
        return JsonResponse(response_data)
    
    return render(request, 'productsHome.html', {'marcas': marcas})


def eliminar_categoria(request):
    if request.method == 'POST':
        try:
            categoria_id = request.POST.get('idToDelete')  
            categoria = get_object_or_404(Categorias, id_categoria=categoria_id)
            
            productos = Productos.objects.filter(id_categoria=categoria)
            
            for producto in productos:
                producto.id_categoria_id = None
                producto.estado = 0
                producto.save(update_fields=['id_categoria', 'estado'])
            
            categoria.delete()
            
            return JsonResponse({'message': 'Registro eliminado con Éxito'})
        except Categorias.DoesNotExist:
            return JsonResponse({'error': 'Categoría no encontrada'})
    else:
        return JsonResponse({'error': 'Método no permitido.'})


def eliminar_marca(request):
    if request.method == 'POST':
        try:
            marca_id = request.POST.get('idToDelete')  
            marca = get_object_or_404(Marcas, id_marca=marca_id)
            productos = Productos.objects.filter(id_marca=marca)
            for producto in productos:
                producto.id_marca_id = None
                producto.estado = 0
                producto.save(update_fields=['id_marca', 'estado'])
            
            marca.delete()
            
            return JsonResponse({'message': 'Registro eliminado con Éxito'})
        except Marcas.DoesNotExist:
            return JsonResponse({'error': 'Marca no encontrada'})
    else:
        return JsonResponse({'error': 'Método no permitido.'})



