import re
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Productos, Marcas, Categorias, Detalleventa, Ventas
from django.db.models import Sum
from django.db.models import Count

def build_context(request, extra_context=None):
    context = {}
    context["productos"] =  Productos.objects.filter(estado=1).all()
    context["marcas"] = Marcas.objects.annotate(num_productos=Count('productos')).filter(num_productos__gt=0)
    context["categorias"] = Categorias.objects.annotate(num_productos=Count('productos')).filter(num_productos__gt=0)
    if extra_context:
        context.update(extra_context)
    return context



def Home(request):
    contexto = build_context(request)
    productos = contexto.get("productos", [])  
    for producto in productos:
        precio_formateado = "{:,.2f}".format(producto.precio_pub).rstrip('0').rstrip('.')
        producto.precio_pub = precio_formateado
        producto.iProductImg_name = get_image_name(producto.iProductImg)
        producto.iInfoImg_name = get_image_name(producto.iInfoImg)

    return render(request, 'pageHome.html', contexto)

from django.http import JsonResponse

def pageDetails(request):
    producto_id = request.GET.get('producto_id')
    productoDetalle = Productos.objects.get(id_producto=producto_id)
    precio_formateado = "{:,.2f}".format(productoDetalle.precio_pub).rstrip('0').rstrip('.')
    productoDetalle.precio_pub = precio_formateado
    productoDetalle.iInfoImg_name = get_image_name(productoDetalle.iInfoImg)
    productoDetalle.iProductImg_name = get_image_name(productoDetalle.iProductImg)
    
    # Construye un diccionario con los datos del producto
    response_data = {
        'nombre_producto': productoDetalle.nombre_producto,
        'precio_pub': productoDetalle.precio_pub,
        'descripcion': productoDetalle.descripcion,
        'sabor': productoDetalle.sabor,
        'presentacion': productoDetalle.presentacion,
        'iInfoImg_name': productoDetalle.iInfoImg_name,
        'iProductImg_name': productoDetalle.iProductImg_name
    }
    
    return JsonResponse(response_data)


def get_image_name(image_field):
    if image_field:
        if isinstance(image_field, bytes):
            return image_field.decode('utf-8')
        else:
            return image_field.name
    return "No Image"

def filter_products(request):
    valor = request.GET.get('valor')
    tipo = request.GET.get('tipo')
    dynamicTitle = ""
    productos = None

    if re.match(r'^marca-\d+$', tipo):
        id_marca = tipo.split('-')[1]
        productos = Productos.objects.filter(id_marca=id_marca)
        marca = Marcas.objects.get(id_marca=id_marca) 
        dynamicTitle = marca.nombre_marca
    elif re.match(r'^categoria-\d+$', tipo):
        id_categoria = tipo.split('-')[1]
        productos = Productos.objects.filter(id_categoria=id_categoria)
        categoria = Categorias.objects.get(id_categoria=id_categoria) 
        dynamicTitle = categoria.nombre_categoria
    elif re.match(r'^producto-\d+$', tipo):
        productos = Productos.objects.filter(estado=1).all()
        dynamicTitle = "Suplementos"

    if productos:
        if valor == "best-sellers":
            productos = productos.annotate(
                total_vendido=Sum('detalleventa__cantidad')
            ).filter(estado=1).order_by('-total_vendido')
            dynamicTitle += " - Más populares"
        elif valor == "high-price":
            productos = productos.filter(estado=1).order_by('-precio_pub')
            dynamicTitle += " - Mayor precio"
        elif valor == "low-price":
            productos = productos.filter(estado=1).order_by('precio_pub')
            dynamicTitle += " - Menor Precio"
        else:
            productos = productos.filter(estado=1)

    data = []
    for producto in productos:
        precio_formateado = "${:,.2f}".format(producto.precio_pub).rstrip('0').rstrip('.')
        data.append({
            'id_producto': producto.id_producto,
            'nombre_producto': producto.nombre_producto,
            'descripcion': producto.descripcion,
            'precio_pub': precio_formateado,
            'iProductImg_name': get_image_name(producto.iProductImg),
            'iInfoImg_name': get_image_name(producto.iInfoImg),
            'dynamicTitle': dynamicTitle,
            'identificador': tipo
        })

    return JsonResponse({'success': True, 'data': data})


from django.db.models import Q
def search_products(request):
    buscar = request.GET.get('search')
    productos = Productos.objects.filter(
        Q(estado=1),
        Q(nombre_producto__icontains=buscar)
    )

    data = []
    for producto in productos:
        precio_formateado = "${:,.2f}".format(producto.precio_pub).rstrip('0').rstrip('.')
        data.append({
            'id_producto': producto.id_producto,
            'nombre_producto': producto.nombre_producto,
            'descripcion': producto.descripcion,
            'precio_pub': precio_formateado,
            'iProductImg_name': get_image_name(producto.iProductImg),
            'iInfoImg_name': get_image_name(producto.iInfoImg),
        })

    return JsonResponse({'success': True, 'data': data})
