from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Productos, Marcas, Categorias, Detalleventa, Ventas
from django.db.models import Sum

def build_context(request, extra_context=None):
    context = {}
    context["productos"] =  Productos.objects.filter(estado=1).all()
    context["marcas"] = Marcas.objects.all()
    context["categorias"] = Categorias.objects.all()
    if extra_context:
        context.update(extra_context)
    return context


def Home(request):
    contexto = build_context(request)
    productos = contexto.get("productos", [])  
    for producto in productos:
        precio_formateado = "{:,.2f}".format(producto.precio).rstrip('0').rstrip('.')
        producto.precio = precio_formateado
        producto.iProductImg_name = get_image_name(producto.iProductImg)
        producto.iInfoImg_name = get_image_name(producto.iInfoImg)

    return render(request, 'pageHome.html', contexto)

from django.http import JsonResponse

def pageDetails(request):
    producto_id = request.GET.get('producto_id')
    productoDetalle = Productos.objects.get(id_producto=producto_id)
    precio_formateado = "{:,.2f}".format(productoDetalle.precio).rstrip('0').rstrip('.')
    productoDetalle.precio = precio_formateado
    productoDetalle.iInfoImg_name = get_image_name(productoDetalle.iInfoImg)
    productoDetalle.iProductImg_name = get_image_name(productoDetalle.iProductImg)
    
    # Construye un diccionario con los datos del producto
    response_data = {
        'nombre_producto': productoDetalle.nombre_producto,
        'precio': productoDetalle.precio,
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

    if tipo == 'Marcas':
        filtro = Productos.objects.filter(id_marca__nombre_marca=valor, estado=1)
        dynamicTitle = f"Marca {valor}"
    elif tipo == 'Categorias':
        filtro = Productos.objects.filter(id_categoria__nombre_categoria=valor, estado=1)
        dynamicTitle = valor
    else:
        if valor == 'best-sellers':
            filtro = Productos.objects.annotate(
                total_vendido=Sum('detalleventa__cantidad')
            ).filter(estado=1, total_vendido__gt=0).order_by('-total_vendido')
            dynamicTitle = "Productos Más Vendidos"
        elif valor == 'high-price':
            filtro = Productos.objects.filter(estado=1).order_by('-precio')
            dynamicTitle = "Productos de Mayor Precio"
        elif valor == 'low-price':
            filtro = Productos.objects.filter(estado=1).order_by('precio')
            dynamicTitle = "Productos de Menor Precio"
        else:
            filtro = Productos.objects.filter(estado=1).all()
            dynamicTitle = "Todos los Productos"

    data = []
    for producto in filtro:
        precio_formateado = "${:,.2f}".format(producto.precio).rstrip('0').rstrip('.')
        data.append({
            'id_producto': producto.id_producto,
            'nombre_producto': producto.nombre_producto,
            'descripcion': producto.descripcion,
            'precio': precio_formateado,
            'iProductImg_name': get_image_name(producto.iProductImg),
            'iInfoImg_name': get_image_name(producto.iInfoImg),
            'dynamicTitle': dynamicTitle
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
        precio_formateado = "${:,.2f}".format(producto.precio).rstrip('0').rstrip('.')
        data.append({
            'id_producto': producto.id_producto,
            'nombre_producto': producto.nombre_producto,
            'descripcion': producto.descripcion,
            'precio': precio_formateado,
            'iProductImg_name': get_image_name(producto.iProductImg),
            'iInfoImg_name': get_image_name(producto.iInfoImg),
        })

    return JsonResponse({'success': True, 'data': data})
