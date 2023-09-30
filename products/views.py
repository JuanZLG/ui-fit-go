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

# def producto_unico(request):
#     producto = request.GET.get("producto", "")
#     producto_existe = Productos.objects.filter(nombre_producto=producto).exists()
#     return JsonResponse({"existe": producto_existe})

def verDetallesProducto(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_producto = request.GET.get('producto_id')
        
        if id_producto:
            try:
                producto = Productos.objects.get(id_producto=id_producto)
                # Si el producto se encuentra
                data = {
                    'categoria': producto.id_categoria.nombre_categoria,
                    'marca': producto.id_marca.nombre_marca,
                    'nombre_producto': producto.nombre_producto,
                    'descripcion': producto.descripcion,
                    'fechaven': producto.fechaven,
                    'cantidad': producto.cantidad,
                    'sabor': producto.sabor,
                    'status': producto.estado,
                    'servicios': producto.presentacion
                }
                return JsonResponse({'success': data})
            except Productos.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de producto no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})

# def crearCategoria(request):
#     if request.method == 'POST':
#         nombre = request.POST['znombre']
#         categoria = Categorias.objects.create(nombre_categoria=nombre)
#         return JsonResponse({'success': True})
#     return render(request, 'createProduct.html')

from .forms import CategoriaForm, MarcaForm

def crear_categoria(request):
    categorias = Categorias.objects.all()
    if request.method == 'POST':
        nombre_categoria = request.POST.get('nombre_categoria')
        Categorias.objects.create(nombre_categoria=nombre_categoria)
        response_data = {"success": True}
        return JsonResponse(response_data)
    
    return render(request, 'productsHome.html', {'categorias': categorias})





def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categorias, id_categoria=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'categoriesHome.html', {'form': form, 'categoria': categoria})


def crear_marca(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('marcas') 
    else:
        form = MarcaForm()
    return render(request, 'productsHome.html', {'form': form})


def eliminar_categoria(request):
    if request.method == 'POST':
        try:
            categoria_id = request.POST.get('idToDelete')  
            categoria = get_object_or_404(Categorias, id_categoria=categoria_id)
            categoria.delete()
            
            return JsonResponse({'message': 'Registro eliminado con Éxito'})
        except Categorias.DoesNotExist:
            return JsonResponse({'error': 'Categoría no encontrada'})
    else:
        return JsonResponse({'error': 'Método no permitido.'})





