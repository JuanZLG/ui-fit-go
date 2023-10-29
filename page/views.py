from django.http import HttpResponse
from django.shortcuts import render
from .models import Productos, Marcas, Categorias, Detalleventa, Ventas
from django.db.models import Sum

def build_context(request, extra_context=None):
    context = {}
    context["productos"] = Productos.objects.all()
    context["marcas"] = Marcas.objects.all()
    context["categorias"] = Categorias.objects.all()
    if extra_context:
        context.update(extra_context)
    return context

def Home(request):
    vendidos = mas_vendidos()
    contexto = build_context(request, {"vendidos": vendidos})
    return render(request, 'pageHome.html', contexto)

def pageDetails(request):
    producto_id = request.GET.get('producto_id')
    productoDetalle = Productos.objects.get(id_producto=producto_id)
    productoDetalle.iInfoImg_name = get_image_name(productoDetalle.iInfoImg)
    productoDetalle.iProductImg_name = get_image_name(productoDetalle.iProductImg)
    contexto = build_context(request, {"detalle": productoDetalle})
    return render(request, 'pageDetails.html', contexto)

def mas_vendidos():
    vendidos = Productos.objects.annotate(
        total_vendido=Sum('detalleventa__cantidad')
    ).filter(estado=1).order_by('-total_vendido')[:10]
    for producto in vendidos:
        producto.iInfoImg_name = get_image_name(producto.iInfoImg)
        producto.iProductImg_name = get_image_name(producto.iProductImg)
    return vendidos

def get_image_name(image_field):
    if image_field:
        if isinstance(image_field, bytes):
            return image_field.decode('utf-8')
        else:
            return image_field.name
    return "No Image"
