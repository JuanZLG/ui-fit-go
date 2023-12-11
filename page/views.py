from datetime import timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
import re
import smtplib
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from dotenv import load_dotenv
from .models import Productos, Marcas, Categorias, Pedidos, DetallePedido, Clientes, Departamentos, Municipios
from django.db.models import Sum
from django.db.models import Count

def build_context(request, extra_context=None):
    context = {}
    context["productos"] = Productos.objects.filter(estado=1, cantidad__gt=0).all()
    
    context["marcas"] = Marcas.objects.filter(
        productos__estado=1,
        productos__cantidad__gt=0
    ).distinct()
    
    context["categorias"] = Categorias.objects.filter(
        productos__estado=1,
        productos__cantidad__gt=0
    ).distinct()
    
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
        'nombre_producto': productoDetalle.nombre_producto.capitalize(),
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
        productos = Productos.objects.filter(id_marca=id_marca, cantidad__gt=1)
        marca = Marcas.objects.get(id_marca=id_marca) 
        dynamicTitle = marca.nombre_marca
    elif re.match(r'^categoria-\d+$', tipo):
        id_categoria = tipo.split('-')[1]
        productos = Productos.objects.filter(id_categoria=id_categoria, cantidad__gt=1)
        categoria = Categorias.objects.get(id_categoria=id_categoria) 
        dynamicTitle = categoria.nombre_categoria
    elif re.match(r'^producto-\d+$', tipo):
        productos = Productos.objects.filter(estado=1, cantidad__gt=1).all()
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
            'nombre_producto': producto.nombre_producto.capitalize(),
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
        Q(nombre_producto__icontains=buscar),
        Q(cantidad__gt=1) 
    )[:5]

    data = []
    for producto in productos:
        precio_formateado = "${:,.2f}".format(producto.precio_pub).rstrip('0').rstrip('.')
        data.append({
            'id_producto': producto.id_producto,
            'nombre_producto': producto.nombre_producto.capitalize(),
            'descripcion': producto.descripcion,
            'precio_pub': precio_formateado,
            'iProductImg_name': get_image_name(producto.iProductImg),
            'iInfoImg_name': get_image_name(producto.iInfoImg),
        })

    return JsonResponse({'success': True, 'data': data})



def mas_vendidos(request):
    productos = Productos.objects.annotate(
        total_vendido=Sum('detalleventa__cantidad')
    ).filter(estado=1, cantidad__gt=1).order_by('-total_vendido')[:5]

    data = []
    for producto in productos:
        precio_formateado = "${:,.2f}".format(producto.precio_pub).rstrip('0').rstrip('.')
        data.append({
            'id_producto': producto.id_producto,
            'nombre_producto': producto.nombre_producto.capitalize(),
            'precio_pub': precio_formateado,
            'presentacion': producto.iProductImg.decode('utf8')
        })

    return JsonResponse({'success': True, 'data': data})


def añadir_pedido(request, id_producto):
    if request.method == 'POST':
        return JsonResponse({'success': True})

    producto = Productos.objects.get(id_producto=id_producto)
    producto.iProductImg = producto.iProductImg.decode('utf8')
    producto.iInfoImg = producto.iInfoImg.decode('utf8')
    precio_formateado = "${:,.2f}".format(producto.precio_pub).rstrip('0').rstrip('.')
    producto.precio_pub = precio_formateado
    sabores = producto.sabor.split(',')
    presentaciones = producto.presentacion.split(',')

    return render(request, 'pageAdd.html', {'producto': producto, 'sabores': sabores, 'presentaciones': presentaciones})



from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def ver_pedido(request):
    if request.method == 'POST':
        try:
            documento_cliente = request.POST['documento']
            nombre_departamento = request.POST['departamento']
            nombre_municipio = request.POST['municipio']

            cliente = Clientes.objects.filter(documento=documento_cliente).first()

            if cliente:
                municipio_actual = cliente.id_municipio
                departamento_actual = municipio_actual.id_departamento

                if departamento_actual.nombre_departamento != nombre_departamento:
                    departamento_actual.nombre_departamento = nombre_departamento
                    departamento_actual.save()

                if municipio_actual.nombre_municipio != nombre_municipio:
                    municipio_actual.nombre_municipio = nombre_municipio
                    municipio_actual.save()

                cliente.nombres = request.POST['nombre']
                cliente.apellidos = request.POST['apellido']
                cliente.celular = request.POST['celular']
                cliente.barrio = request.POST['barrio']
                cliente.direccion = request.POST['direccion']
                cliente.correo = request.POST['correo']
                cliente.save()
            else:
                departamento = Departamentos.objects.create(nombre_departamento=nombre_departamento)
                municipio = Municipios.objects.create(nombre_municipio=nombre_municipio, id_departamento=departamento)

                cliente = Clientes.objects.create(
                    id_municipio=municipio,
                    documento=documento_cliente,
                    nombres=request.POST['nombre'],
                    apellidos=request.POST['apellido'],
                    celular=request.POST['celular'],
                    barrio=request.POST['barrio'],
                    direccion=request.POST['direccion'],
                    correo=request.POST['correo'],
                )

            carrito = json.loads(request.POST.get('carrito', '{}'))

            pedido = Pedidos.objects.create(
                id_venta=None,
                id_cliente=cliente,
                total_pedido=0,  
                estado='en proceso',
            )

            total_pedido = 0
            for idProducto, detalles in carrito.items():
                precio_uni = float(detalles['precio'].replace('$', '').replace(',', ''))
                cantidad = int(detalles['cantidad'])
                idDelProducto = int(detalles['idDelProducto'])
                precio_tot = precio_uni * cantidad
                total_pedido += precio_tot  

                producto_obj = Productos.objects.get(id_producto=idDelProducto)
                DetallePedido.objects.create(
                    id_pedido=pedido,
                    id_producto=producto_obj,
                    sabor=detalles['sabor'],
                    cantidad=cantidad,
                    precio_uni=precio_uni,
                    precio_tot=precio_tot,
                )

            pedido.total_pedido = total_pedido
            pedido.save()

            nombreCompletoCliente = cliente.nombres + " " + cliente.apellidos
            correo = cliente.correo
            pedido_email_proceso(nombreCompletoCliente, correo)
            return JsonResponse({'message': 'Datos guardados correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'pageOrder.html')

from django.template.loader import get_template

def pedido_email_proceso(user, email):
    load_dotenv()
    remitente = os.getenv("USER")
    destinatario = email
    asunto = "Confirmación de Pedido y Próximos Pasos"

    msg = MIMEMultipart()
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    template = get_template("emailProceso.html")
    context = {'user': user}
    
    html = template.render(context)

    msg.attach(MIMEText(html, "html"))
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(remitente, os.getenv("PASS"))
    
    server.sendmail(remitente, destinatario, msg.as_string())
    server.quit()
    


def document_exist(request):
    documento = request.GET.get("documento", "")
    cliente = Clientes.objects.filter(documento=documento).exists()
    return JsonResponse({"existe": cliente})


def obtener_cliente(request):
    documento = request.GET.get('documento')
    try:
        cliente = Clientes.objects.get(documento=documento)
        data = {
            'estado': cliente.estado,
            'nombres': cliente.nombres,
            'apellidos': cliente.apellidos,
            'celular': cliente.celular,
            'correo': cliente.correo,
            'barrio': cliente.barrio,
            'direccion': cliente.direccion,
            'municipio': cliente.id_municipio.nombre_municipio,
            'departamento': cliente.id_municipio.id_departamento.nombre_departamento,
        }
        return JsonResponse({'success': data})
    except Clientes.DoesNotExist:
        return JsonResponse({'error': 'No se encontró un cliente con el documento proporcionado.'})
    except Exception as e:
        return JsonResponse({'error': str(e)})




