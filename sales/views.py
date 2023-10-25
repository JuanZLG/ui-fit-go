from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from sales.models import Clientes, Detalleventa, Ventas, Productos
from django.db.models import Q

def Home(request):
    ventas = Ventas.objects.all()
    return render(request, "salesHome.html", {"ventas": ventas})


from django.http import JsonResponse
import json

@csrf_exempt
def crear_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            documento = data.get('documento', '')
            totalVenta = data.get('totalVenta', '')
            productos = data.get('productos', [])

            cliente = Clientes.objects.filter(documento=documento).first()
            venta = Ventas.objects.create(id_cliente=cliente, totalVenta=totalVenta)
            for producto_datos in productos:
                nombre_producto = producto_datos['nombre']
                cantidad_vendida = producto_datos['cantidad']

                producto = Productos.objects.get(nombre_producto=nombre_producto)

                if producto:
                    producto.cantidad -= cantidad_vendida
                    producto.save()

                Detalleventa.objects.create(
                    id_producto=producto,
                    id_venta=venta,
                    cantidad=cantidad_vendida,
                    precio_uni=producto_datos['precioUnidad'],
                    precio_tot=producto_datos['precioTotal']
                )
            response_data = {'success': True}
            return JsonResponse(response_data)
        except json.JSONDecodeError as e:
            response_data = {'success': False, 'error': str(e)}
            return JsonResponse(response_data, status=400)
    
    clientes = Clientes.objects.all()
    return render(request, 'createSales.html', {'clientes': clientes})

    

def buscar_cliente(request):
    nombre_cliente = request.GET.get("q", "")

    palabras_clave = nombre_cliente.split()
    clientes_encontrados = Clientes.objects.all()

    for palabra_clave in palabras_clave:
        clientes_encontrados = clientes_encontrados.filter(
            Q(nombres__icontains=palabra_clave) | Q(apellidos__icontains=palabra_clave)
        )

    resultados = [
        {
            "documento": cliente.documento,
            "nombre_cliente": f"{cliente.nombres} {cliente.apellidos}",
            "estado": cliente.estado,
        }
        for cliente in clientes_encontrados
    ]

    return JsonResponse({"resultados": resultados})



def buscar_productos(request):
    q = request.GET.get("q", "")
    productos = Productos.objects.filter(nombre_producto__icontains=q).values("nombre_producto", "estado")
    productos_json = [{"nombre_producto": p["nombre_producto"], "estado": p["estado"]} for p in productos]
    return JsonResponse({"productos": productos_json})



def validar_cantidad(request):
    cantidad = request.GET.get("cantidad", "")
    nombre = request.GET.get("nombre", "")
    producto = Productos.objects.get(nombre_producto__iexact=nombre)
    if int(cantidad) > producto.cantidad:
        return JsonResponse({"suficiente": False})
    return JsonResponse({"suficiente": True})


           
def buscar_documentos(request):
    q = request.GET.get("q", "")
    documentos = Clientes.objects.filter(documento__contains=q).values_list(
        "documento", flat=True
    )

    nombre_cliente = ""
    if documentos:
        primer_documento = documentos[0]
        cliente = Clientes.objects.filter(documento=primer_documento).first()
        if cliente:
            nombre_cliente = f"{cliente.nombres} {cliente.apellidos}"

    return JsonResponse(
        {"documentos": list(documentos), "nombre_cliente": nombre_cliente}
    )




def validar_producto(request):
    nombre_producto = request.GET.get("nombre_producto", "")
    producto = Productos.objects.filter(nombre_producto=nombre_producto).first()
    if producto is not None and producto.estado == 0:
        return JsonResponse({"existe": False})
    else:
        return JsonResponse({"existe": producto is not None})



def validar_cliente(request):
    documentoDato = request.GET.get("documentoDato", "")
    cliente_existe = Clientes.objects.filter(documento=documentoDato).exists()
    return JsonResponse({"existe": cliente_existe})

def obtener_precio(request):
    nombre_producto = request.GET.get(
        "nombre_producto", None
    ) 
    if nombre_producto is not None:
        producto = Productos.objects.get(nombre_producto=nombre_producto)
        precio = producto.precio
        return JsonResponse({"precio": precio})
    else:
        return JsonResponse(
            {"error": 'Parámetro "nombre_producto" no proporcionado en la solicitud'},
            status=400,
        )


def obtener_nombre(request):
    nombre_producto = request.GET.get(
        "nombre_producto", None
    )  
    if nombre_producto is not None:
        try:
            producto = Productos.objects.get(nombre_producto=nombre_producto)
            precio = producto.precio
            return JsonResponse({"precio": precio})
        except Productos.DoesNotExist:
            return JsonResponse({"error": "Producto no encontrado"}, status=404)
    else:
        return JsonResponse(
            {"error": 'Parámetro "nombre_producto" no proporcionado en la solicitud'},
            status=400,
        )




def cambiarEstado(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        venta_id = request.GET.get('venta_id')
        nuevo_estado = request.GET.get('nuevo_estado')
        
        venta = Ventas.objects.get(id_venta=venta_id)
        venta.estado = int(nuevo_estado)
        venta.save()

        detalles = Detalleventa.objects.filter(id_venta=venta_id)
        for detalle in detalles:
            producto = detalle.id_producto
            if venta.estado == 0: 
                detalle.estado = 0  
                producto.cantidad += detalle.cantidad 
                producto.save()  
            detalle.save() 
        
        return JsonResponse({'status': 'success'})


def detalles_venta(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_venta = request.GET.get('venta_id')
        if id_venta:
            try:
                venta = Ventas.objects.get(id_venta=id_venta)
                detalles = Detalleventa.objects.filter(id_venta=id_venta)
                detalles_data = []

                for detalle in detalles:
                    producto = Productos.objects.get(id_producto=detalle.id_producto.id_producto)
                    detalle_data = {
                        'producto': producto.nombre_producto,
                        'cantidad': detalle.cantidad,
                        'precio_uni': detalle.precio_uni,
                        'precio_tot': detalle.precio_tot,
                    }
                    detalles_data.append(detalle_data)

                data = {
                    'fechareg': venta.fechareg,
                    'cliente': venta.id_cliente.nombres + ' ' + venta.id_cliente.apellidos,
                    'estado': venta.estado,
                    'documento': venta.id_cliente.documento,
                    'totalVenta': venta.totalVenta,
                    'detalles': detalles_data
                }
                return JsonResponse({'success': data})
            except Ventas.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Venta no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de Venta no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Detalleventa, Ventas
import os

def formatear_precios(valor):
    valor = round(valor, 2)
    precio_formateado = '${:,.2f}'.format(valor)
    return precio_formateado

def generar_factura_pdf_venta(request, venta_id):
    venta = get_object_or_404(Ventas, id_venta=venta_id)
    detalles_venta = Detalleventa.objects.filter(id_venta=venta_id)

    totalVenta = 0
    detalles = []

    for detalle in detalles_venta:
        producto = detalle.id_producto.nombre_producto
        precioUnitario = formatear_precios(detalle.precio_uni)
        cantidad = detalle.cantidad
        totalProducto = formatear_precios(detalle.precio_tot)
        totalVenta += detalle.precio_tot

        detalles.append([producto, precioUnitario, cantidad, totalProducto])

    totalVentaFormateado = formatear_precios(totalVenta)

    # Crear una respuesta de tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=factura_venta_{venta.id_cliente.nombres}_{venta.id_cliente.apellidos}.pdf'


    # Crear un objeto PDF
    buffer = response
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()

    # Contenido de la factura
    elements = []

    # Agregar la imagen de logo como un círculo
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img/GIcon.png')
    logo = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
    logo.drawHeight = 1.5 * inch
    logo.drawWidth = 1.5 * inch
    elements.append(logo)

    # Línea roja
    elements.append(Spacer(1, 6))
    elements.append(Paragraph('Factura de Venta', styles['Title']))
    elements.append(Spacer(1, 6))

    centered_style = ParagraphStyle(name='CenteredStyle', alignment=TA_CENTER)

    # Detalles de la factura en la parte superior izquierda
    elements.append(Paragraph(f'<b>Cliente:</b> {venta.id_cliente.nombres}', centered_style))
    elements.append(Paragraph(f'<b>Documento:</b> {venta.id_cliente.documento}', centered_style))
    elements.append(Paragraph(f'<b>Fecha de Registro:</b> {venta.fechareg}', centered_style))

    # Espacio entre detalles y tabla
    elements.append(Spacer(1, 12))

    # Detalles de compra (la tabla)
    data = [["Producto", "Precio Unitario", "Cantidad", "Total"]]
    data.extend(detalles)
    data.append(["", "", "", totalVentaFormateado])  # Agrega el total al final

    # Ajustar el ancho de las columnas de la tabla
    t = Table(data, colWidths=[180, 80, 60, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))

    elements.append(t)

    doc.build(elements)

    return response
