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
from django.db.models import Count, Prefetch

def build_context(request, extra_context=None):
    context = {}
    context["productos"] = Productos.objects.filter(estado=1, cantidad__gt=0).all()
    
    context["marcas"] = Marcas.objects.filter(
        productos__estado=1,
        productos__cantidad__gt=0
    ).distinct()
    
    # Los menús solo muestran productos activos y con stock (antes aparecían también los agotados)
    context["categorias"] = Categorias.objects.filter(
        productos__estado=1,
        productos__cantidad__gt=0
    ).distinct().prefetch_related(
        Prefetch('productos_set', queryset=Productos.objects.filter(estado=1, cantidad__gt=0), to_attr='disponibles')
    )
    
    if extra_context:
        context.update(extra_context)
    return context


def Home(request):
    contexto = build_context(request)
    productos = contexto.get("productos", [])
    # Insignias reales: los 3 más vendidos y los productos con pocas unidades
    mas_vendidos = set(
        Productos.objects.filter(estado=1, cantidad__gt=0)
        .annotate(vendidos=Sum('detalleventa__cantidad')).filter(vendidos__gt=0)
        .order_by('-vendidos').values_list('id_producto', flat=True)[:3]
    )
    for producto in productos:
        producto.badge, producto.badge_tipo = '', ''
        if producto.cantidad <= 5:
            producto.badge = f'Última unidad' if producto.cantidad == 1 else f'Últimas {producto.cantidad} unidades'
            producto.badge_tipo = 'ultimas'
        elif producto.id_producto in mas_vendidos:
            producto.badge, producto.badge_tipo = 'Más vendido', 'top'
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
        productos = Productos.objects.filter(id_marca=id_marca, cantidad__gt=0)
        marca = Marcas.objects.get(id_marca=id_marca) 
        dynamicTitle = marca.nombre_marca
    elif re.match(r'^categoria-\d+$', tipo):
        id_categoria = tipo.split('-')[1]
        productos = Productos.objects.filter(id_categoria=id_categoria, cantidad__gt=0)
        categoria = Categorias.objects.get(id_categoria=id_categoria) 
        dynamicTitle = categoria.nombre_categoria
    elif re.match(r'^producto-\d+$', tipo):
        productos = Productos.objects.filter(estado=1, cantidad__gt=0).all()
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
        Q(cantidad__gt=0) 
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
    ).filter(estado=1, cantidad__gt=0).order_by('-total_vendido')[:5]

    data = []
    for producto in productos:
        precio_formateado = "${:,.2f}".format(producto.precio_pub).rstrip('0').rstrip('.')
        data.append({
            'id_producto': producto.id_producto,
            'nombre_producto': producto.nombre_producto.capitalize(),
            'precio_pub': precio_formateado,
            'presentacion': get_image_name(producto.iProductImg)
        })

    return JsonResponse({'success': True, 'data': data})


def añadir_pedido(request, id_producto):
    if request.method == 'POST':
        return JsonResponse({'success': True})

    producto = get_object_or_404(Productos, id_producto=id_producto, estado=1)
    precio_formateado = "${:,.2f}".format(producto.precio_pub).rstrip('0').rstrip('.')
    producto.precio_pub = precio_formateado
    sabores = producto.sabor.split(',')
    presentaciones = producto.presentacion.split(',')

    return render(request, 'pageAdd.html', {'producto': producto, 'sabores': sabores, 'presentaciones': presentaciones})



from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import logging
from tuiranfitgo.inventory import StockError, DatosInvalidos, entero_positivo

logger = logging.getLogger(__name__)

MAX_LINEAS_PEDIDO = 50
MAX_UNIDADES_LINEA = 999


def _texto(post, clave, etiqueta, maximo, obligatorio=True):
    valor = (post.get(clave) or '').strip()
    if obligatorio and not valor:
        raise DatosInvalidos(f'El campo «{etiqueta}» es obligatorio.')
    if len(valor) > maximo:
        raise DatosInvalidos(f'El campo «{etiqueta}» no puede superar {maximo} caracteres.')
    return valor


@transaction.atomic
def _crear_pedido_publico(post):
    """Valida el carrito contra el inventario y crea el pedido. Todo o nada.

    El precio SIEMPRE sale de la base de datos: el navegador no decide cuánto se cobra.
    """
    documento = _texto(post, 'documento', 'documento', 25)
    nombre = _texto(post, 'nombre', 'nombre', 60)
    apellido = _texto(post, 'apellido', 'apellido', 60)
    celular = _texto(post, 'celular', 'celular', 15)
    correo = _texto(post, 'correo', 'correo', 100)
    departamento = _texto(post, 'departamento', 'departamento', 50)
    municipio = _texto(post, 'municipio', 'municipio', 60)
    barrio = _texto(post, 'barrio', 'barrio', 40, obligatorio=False)
    direccion = _texto(post, 'direccion', 'dirección', 50, obligatorio=False)
    try:
        validate_email(correo)
    except ValidationError:
        raise DatosInvalidos('El correo electrónico no es válido.')

    try:
        carrito = json.loads(post.get('carrito') or '{}')
    except (json.JSONDecodeError, TypeError):
        raise DatosInvalidos('El carrito no es válido.')
    if not isinstance(carrito, dict) or not carrito:
        raise DatosInvalidos('Tu pedido está vacío.')
    if len(carrito) > MAX_LINEAS_PEDIDO:
        raise DatosInvalidos('El pedido tiene demasiados productos.')

    # --- Cliente: si ya existe NO se sobrescriben sus datos (el formulario es público) ---
    cliente = Clientes.objects.filter(documento=documento).first()
    if cliente is not None:
        if not cliente.estado:
            raise DatosInvalidos('Tu cuenta de cliente está inactiva. Escríbenos por WhatsApp para ayudarte.')
        pendientes = {'nombres': nombre, 'apellidos': apellido, 'celular': celular,
                      'barrio': barrio, 'direccion': direccion, 'correo': correo}
        cambios = [campo for campo, valor in pendientes.items() if valor and not getattr(cliente, campo)]
        for campo in cambios:
            setattr(cliente, campo, pendientes[campo])
        if cambios:
            cliente.save(update_fields=cambios)
    else:
        # Departamentos y municipios son compartidos: se reutilizan, nunca se renombran
        depto = Departamentos.objects.filter(nombre_departamento__iexact=departamento).first() \
            or Departamentos.objects.create(nombre_departamento=departamento)
        muni = Municipios.objects.filter(id_departamento=depto, nombre_municipio__iexact=municipio).first() \
            or Municipios.objects.create(id_departamento=depto, nombre_municipio=municipio)
        cliente = Clientes.objects.create(
            id_municipio=muni, documento=documento, nombres=nombre, apellidos=apellido,
            celular=celular, barrio=barrio, direccion=direccion, correo=correo, estado=True,
        )

    # --- Carrito: productos activos, con stock suficiente y precio de la base de datos ---
    lineas, demanda = [], {}
    for item in carrito.values():
        if not isinstance(item, dict):
            raise DatosInvalidos('El carrito no es válido.')
        id_producto = entero_positivo(item.get('idDelProducto'), 'producto')
        cantidad = entero_positivo(item.get('cantidad'), 'cantidad')
        if cantidad > MAX_UNIDADES_LINEA:
            raise DatosInvalidos('La cantidad solicitada es demasiado alta.')
        producto = Productos.objects.filter(pk=id_producto, estado=1).first()
        if producto is None:
            raise StockError('Uno de los productos ya no está disponible.')
        sabor = str(item.get('sabor') or '').strip()
        sabores = [x.strip() for x in (producto.sabor or '').split(',') if x.strip()]
        if sabores and sabor not in sabores:
            raise DatosInvalidos(f'El sabor elegido para «{producto.nombre_producto}» no es válido.')
        demanda[id_producto] = demanda.get(id_producto, 0) + cantidad
        lineas.append((producto, sabor[:50], cantidad))

    for id_producto, pedido_total in demanda.items():
        producto = next(p for p, _, _ in lineas if p.id_producto == id_producto)
        if pedido_total > max(producto.cantidad, 0):
            raise StockError(f'Solo quedan {max(producto.cantidad, 0)} unidad(es) de «{producto.nombre_producto}».')

    pedido = Pedidos.objects.create(id_venta=None, id_cliente=cliente, total_pedido=0, estado='en proceso')
    total = 0.0
    for producto, sabor, cantidad in lineas:
        subtotal = producto.precio_pub * cantidad
        total += subtotal
        DetallePedido.objects.create(
            id_pedido=pedido, id_producto=producto, sabor=sabor, cantidad=cantidad,
            precio_uni=producto.precio_pub, precio_tot=subtotal,
        )
    pedido.total_pedido = total
    pedido.save(update_fields=['total_pedido'])
    return pedido, cliente


@csrf_exempt
def ver_pedido(request):
    if request.method != 'POST':
        return render(request, 'pageOrder.html')

    try:
        pedido, cliente = _crear_pedido_publico(request.POST)
    except (DatosInvalidos, StockError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        logger.exception('Error al crear un pedido desde la tienda')
        return JsonResponse({'error': 'No se pudo registrar el pedido. Inténtalo de nuevo.'}, status=500)

    # El correo se envía fuera de la transacción: si falla, el pedido ya quedó registrado
    try:
        pedido_email_proceso(f"{cliente.nombres} {cliente.apellidos}", cliente.correo)
    except Exception:
        logger.exception('No se pudo enviar el correo del pedido %s', pedido.id_pedido)

    return JsonResponse({'message': 'Datos guardados correctamente'})

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
            'municipio': cliente.id_municipio.nombre_municipio,
            'departamento': cliente.id_municipio.id_departamento.nombre_departamento,
        }
        return JsonResponse({'success': data})
    except Clientes.DoesNotExist:
        return JsonResponse({'error': 'No se encontró un cliente con el documento proporcionado.'})
    except Exception:
        return JsonResponse({'error': 'No se pudo consultar el cliente.'})




