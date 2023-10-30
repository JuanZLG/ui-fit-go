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
        producto.iProductImg_name = get_image_name(producto.iProductImg)
        producto.iInfoImg_name = get_image_name(producto.iInfoImg)

    return render(request, 'pageHome.html', contexto)


def pageDetails(request):
    producto_id = request.GET.get('producto_id')
    productoDetalle = Productos.objects.get(id_producto=producto_id)
    productoDetalle.iInfoImg_name = get_image_name(productoDetalle.iInfoImg)
    productoDetalle.iProductImg_name = get_image_name(productoDetalle.iProductImg)
    contexto = build_context(request, {"detalle": productoDetalle})
    return render(request, 'pageDetails.html', contexto)



def get_image_name(image_field):
    if image_field:
        if isinstance(image_field, bytes):
            return image_field.decode('utf-8')
        else:
            return image_field.name
    return "No Image"



def filter_products(request):
    print(12323)
    option = request.GET.get('sortOption')
    if option == 'best-sellers':
        filtro = Productos.objects.annotate(
            total_vendido=Sum('detalleventa__cantidad')
        ).filter(estado=1, total_vendido__gt=0).order_by('-total_vendido')
    elif option == 'high-price':
        filtro = Productos.objects.filter(estado=1).order_by('-precio')
    elif option == 'low-price':
        filtro = Productos.objects.filter(estado=1).order_by('precio')
    else:
        filtro = Productos.objects.filter(estado=1).all()

    data = []
    for producto in filtro:
        data.append({
            'id_producto': producto.id_producto,
            'nombre_producto': producto.nombre_producto,
            'descripcion': producto.descripcion,
            'precio': producto.precio,
            'iProductImg_name': get_image_name(producto.iProductImg),
            'iInfoImg_name': get_image_name(producto.iInfoImg),
        })

    return JsonResponse({'success': True, 'data': data})
