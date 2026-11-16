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
import re
from django.utils.dateparse import parse_date, parse_datetime
from PIL import Image
from tuiranfitgo.inventory import DatosInvalidos, entero_no_negativo, nombre_imagen

MAX_IMAGEN_BYTES = 5 * 1024 * 1024


def _texto(post, clave, etiqueta, maximo):
    valor = (post.get(clave) or '').strip()
    if not valor:
        raise DatosInvalidos(f'El campo «{etiqueta}» es obligatorio.')
    if len(valor) > maximo:
        raise DatosInvalidos(f'El campo «{etiqueta}» no puede superar {maximo} caracteres.')
    return valor


def _precio(valor, etiqueta):
    """Los precios llegan formateados ("12.500"): se quitan los separadores de miles."""
    limpio = str(valor or '').replace(',', '').replace('.', '').strip()
    if not re.fullmatch(r'\d+', limpio):
        raise DatosInvalidos(f'El campo «{etiqueta}» debe ser un valor numérico.')
    return float(limpio)


def _imagen(archivo, etiqueta):
    """Acepta solo imágenes reales de hasta 5 MB."""
    if archivo is None:
        return None
    if archivo.size > MAX_IMAGEN_BYTES:
        raise DatosInvalidos(f'La imagen «{etiqueta}» supera los 5 MB.')
    try:
        Image.open(archivo).verify()
    except Exception:
        raise DatosInvalidos(f'El archivo de «{etiqueta}» no es una imagen válida.')
    archivo.seek(0)
    return archivo


def _datos_producto(post):
    """Valida y normaliza el formulario de producto (crear y editar)."""
    fecha_txt = (post.get('iFechaven') or '').strip()
    fecha = parse_datetime(fecha_txt) or parse_date(fecha_txt)
    if fecha is None:
        raise DatosInvalidos('La fecha de vencimiento no es válida (usa AAAA-MM-DD).')
    return {
        'nombre_producto': _texto(post, 'iNombre', 'nombre', 75),
        'descripcion': _texto(post, 'iDescripcion', 'descripción', 400),
        'cantidad': entero_no_negativo(post.get('iCantidad'), 'cantidad'),
        'fechaven': fecha,
        'sabor': _texto(post, 'iSabor', 'sabor', 50),
        'presentacion': _texto(post, 'iServices', 'presentación', 45),
        'precio': _precio(post.get('iPrice'), 'precio de compra'),
        'precio_pub': _precio(post.get('iPubPrice'), 'precio al público'),
    }


def _error_json(mensaje, status=400):
    return JsonResponse({'success': False, 'error': mensaje}, status=status)


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
        try:
            datos = _datos_producto(request.POST)
            marca = Marcas.objects.filter(id_marca=request.POST.get('iMarca') or 0).first()
            categoria = Categorias.objects.filter(id_categoria=request.POST.get('iCategoria') or 0).first()
            if marca is None or categoria is None:
                raise DatosInvalidos('Selecciona una marca y una categoría válidas.')
            img_producto = _imagen(request.FILES.get('iProductImg'), 'imagen del producto')
            img_info = _imagen(request.FILES.get('iInfoImg'), 'información nutricional')
            if img_producto is None:
                raise DatosInvalidos('La imagen del producto es obligatoria.')
        except DatosInvalidos as e:
            return _error_json(str(e))

        Productos.objects.create(
            id_categoria=categoria, id_marca=marca,
            iProductImg=img_producto, iInfoImg=img_info, **datos,
        )
        return JsonResponse({'success': True})

    return render(request, 'createProducts.html', {"marcas": marcas, "categorias": categorias})

@jwt_cookie_required
@module_access_required('productos')
def editProduct(request, id_producto):
    marcas = Marcas.objects.all()
    categorias = Categorias.objects.all()
    
    if request.method == 'POST':
        producto = Productos.objects.filter(id_producto=id_producto).first()
        if producto is None:
            return _error_json('Producto no encontrado.', 404)
        try:
            datos = _datos_producto(request.POST)
            marca = Marcas.objects.filter(id_marca=request.POST.get('iMarca') or 0).first()
            categoria = Categorias.objects.filter(id_categoria=request.POST.get('iCategoria') or 0).first()
            if marca is None or categoria is None:
                raise DatosInvalidos('Selecciona una marca y una categoría válidas.')
            img_producto = _imagen(request.FILES.get('iProductImg'), 'imagen del producto')
            img_info = _imagen(request.FILES.get('iInfoImg'), 'información nutricional')
        except DatosInvalidos as e:
            return _error_json(str(e))

        # Editar un producto NO cambia su estado (antes lo reactivaba sin avisar)
        for campo, valor in datos.items():
            setattr(producto, campo, valor)
        producto.id_categoria, producto.id_marca = categoria, marca
        if img_producto:
            producto.iProductImg = img_producto
        if img_info:
            producto.iInfoImg = img_info
        producto.save()
        return JsonResponse({'success': True})

    products = Productos.objects.get(id_producto=id_producto)
    products.precio_pub = int(products.precio_pub)
    products.precio = int(products.precio)
    
    if products.iInfoImg:
        products.iInfoImg_name = nombre_imagen(products.iInfoImg).split('/')[-1]

    if products.iProductImg:
        products.iProductImg_name = nombre_imagen(products.iProductImg).split('/')[-1]


    return render(request, 'editProducts.html', {"Product": products, "marcas": marcas, "categorias": categorias})


@jwt_cookie_required
@module_access_required('productos')
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



@jwt_cookie_required
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
                    'img': nombre_imagen(producto.iProductImg)
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


@jwt_cookie_required
@module_access_required('productos')
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


@jwt_cookie_required
@module_access_required('productos')
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



