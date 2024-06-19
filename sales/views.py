from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from tuiranfitgo.views import jwt_cookie_required, module_access_required
import json
from sales.models import Clientes, Detalleventa, Ventas, Productos, Marcas, Categorias, Pedidos, DetallePedido
from django.db.models import Q
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, Image, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Detalleventa, Ventas
from django.template.loader import get_template
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from django.db.models import Sum


@jwt_cookie_required
@module_access_required('ventas')
def Home(request):
    ventas = Ventas.objects.all()
    return render(request, "salesHome.html", {"ventas": ventas})

def formatear_precios_email(valor):
    valor = round(valor, 2)
    precio_formateado = '${:,.2f}'.format(valor)
    return precio_formateado

@csrf_exempt
@jwt_cookie_required
def crear_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            documento = data.get('documentoCliente', '')
            totalVenta = data.get('totalVenta', '')
            descuentoVenta = data.get('descuentoVenta', 'No aplica')
            totalVentaDescuento = data.get('totalVentaDescuento', 'No aplica')
            margenGananciaVenta = data.get('margenGananciaVenta')
            productos = data.get('productos', [])
            
            cliente = Clientes.objects.filter(documento=documento).first()
            if cliente is None:
                return JsonResponse({'success': False, 'error': 'Cliente no encontrado'}, status=400)
            
            venta = Ventas.objects.create(
                id_cliente=cliente,
                totalVenta=totalVenta,
                descuentoVenta=descuentoVenta,
                totalVentaDescuento=totalVentaDescuento,
                margenGanancia=margenGananciaVenta
            )

            detalles_venta = []
            for idProducto, producto_datos in productos.items():
                idPedido = producto_datos["idPedido"]
                cantidad_vendida = producto_datos['cantidad']
                precioCompra = producto_datos['precioCompra']
                precioVenta = producto_datos['precioVenta']
                descuento = producto_datos['descuentoProducto']
                totalProductoDescuento = producto_datos['totalProductoDescuento']
                margenGananciaProducto = producto_datos['margenGananciaProducto']  
                totalProducto = producto_datos['totalProducto']
                
                producto = Productos.objects.get(id_producto=idProducto)
                if producto:
                    producto.cantidad -= cantidad_vendida
                    producto.save()

                Detalleventa.objects.create(
                    id_producto=producto,
                    id_venta=venta,
                    cantidad=cantidad_vendida,
                    precio_compra=precioCompra,
                    precio_venta=precioVenta,
                    descuentoProducto=descuento,
                    totalProductoDescuento=totalProductoDescuento,
                    margenGanancia=margenGananciaProducto,
                    precio_tot=totalProducto,
                )

                precio_venta_formateado = formatear_precios_email(precioVenta)
                total_producto_formateado = formatear_precios_email(totalProducto)

                detalles_venta.append({
                    'nombre_producto': producto.nombre_producto,
                    'url': producto.iProductImg.decode('utf8'),
                    'cantidad': producto.cantidad,
                    'precio_venta': precio_venta_formateado,
                    'precio_tot': total_producto_formateado,
                    'descuentoProducto':descuento,
                })
            total_venta_formateado = formatear_precios_email(totalVenta)
            response_data = {'success': True}
            return JsonResponse(response_data)
        except json.JSONDecodeError as e:
            response_data = {'success': False, 'error': str(e)}
            return JsonResponse(response_data, status=400)

    clientes = Clientes.objects.all()
    return render(request, 'createSales.html', {'clientes': clientes})

def pedido_email_confirmacion(venta, email, detalles_venta, total_venta_formateado):
    load_dotenv()
    remitente = os.getenv("USER")
    destinatario = email
    asunto = "Remanente de compra"

    msg = MIMEMultipart()
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    template = get_template("emailConfirmacion.html")
    context = {
        'venta': venta,
        'detalles_venta': detalles_venta,
        'total_venta_formateado': total_venta_formateado
    }
    
    html = template.render(context)

    msg.attach(MIMEText(html, "html"))
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(remitente, os.getenv("PASS"))
    
    server.sendmail(remitente, destinatario, msg.as_string())
    server.quit()

def buscar_productos(request):
    q = request.GET.get("q", "")
    productos = Productos.objects.filter(
        Q(nombre_producto__icontains=q )
    )
    resultados = []
    for producto in productos:
        precio_ganancia = producto.precio_pub - producto.precio 

        try:
            marca = producto.id_marca.nombre_marca
        except Productos.id_marca.RelatedObjectDoesNotExist:
            marca = "No tiene marca"

        try:
            categoria = producto.id_categoria.nombre_categoria
        except Productos.id_categoria.RelatedObjectDoesNotExist:
            categoria = "No tiene categorías"

        resultados.append({
            'id_producto': producto.id_producto,
            'estado': producto.estado,
            'nombre_producto': producto.nombre_producto,
            'cantidad': producto.cantidad,
            'descripcion': producto.descripcion,
            'precio_compra': producto.precio,
            'precio_venta': producto.precio_pub,
            'precio_ganancia': precio_ganancia,
            'marca': marca,
            'categoria': categoria,
            'presentacion': producto.iProductImg.decode('utf8')
        })
    return JsonResponse({"resultados": resultados})

def agregarDetalleATabla(request):
    id_pedido = request.GET.get("id_pedido")
    id_producto = request.GET.get("id_producto")
    sabor = request.GET.get("sabor")
    precio_venta_pagina = float(request.GET.get("precio_uni").replace('$', '').replace(',', ''))
    cantidad_pagina = request.GET.get("cantidad")

    producto = Productos.objects.get(id_producto=id_producto)

    precio_ganancia = precio_venta_pagina - producto.precio 

    try:
        marca = producto.id_marca.nombre_marca
    except Productos.id_marca.RelatedObjectDoesNotExist:
        marca = "No tiene marca"

    try:
        categoria = producto.id_categoria.nombre_categoria
    except Productos.id_categoria.RelatedObjectDoesNotExist:
        categoria = "No tiene categorías"
    
    resultado = {
        'id_pedido': id_pedido,
        'id_producto': producto.id_producto,
        'estado': producto.estado,
        'sabor': sabor,
        'nombre_producto': producto.nombre_producto,
        'cantidad_pagina': cantidad_pagina,
        'cantidad': producto.cantidad,
        'descripcion': producto.descripcion,
        'precio_compra': producto.precio,
        'precio_venta_pagina': precio_venta_pagina,
        'precio_ganancia': precio_ganancia,
        'marca': marca,
        'categoria': categoria,
        'presentacion': producto.iProductImg.decode('utf8')
    }
    return JsonResponse({"resultado": resultado})

def verificar_stock(request):
    producto = request.GET.get('id_producto')
    cantidad_str = request.GET.get('cantidad')
    if cantidad_str.isdigit():
        cantidad = int(cantidad_str)
    else:
        cantidad = 0  
    try:
        producto_obj = Productos.objects.get(id_producto=producto)
        supera_stock = cantidad > producto_obj.cantidad
    except Productos.DoesNotExist:
        supera_stock = False

    return JsonResponse({'supera_stock': supera_stock, 'cantidad_disponible': producto_obj.cantidad})

def buscar_detalles_pedidos(id_pedido):
    detalles = DetallePedido.objects.filter(id_pedido=id_pedido).select_related('id_producto')
    detalles_formateados = []
    for detalle in detalles:
        detalles_formateados.append({
            "id_detallepedido": detalle.id_detallepedido,
            "id_producto": detalle.id_producto.id_producto,
            "nombre_producto": detalle.id_producto.nombre_producto,
            "sabor": detalle.sabor,
            "cantidad": detalle.cantidad,
            "cantidad_stock": detalle.id_producto.cantidad,
            "estado_producto": detalle.id_producto.estado,
            "precio_uni": detalle.precio_uni,
            "precio_tot": detalle.precio_tot  
        })
    return detalles_formateados if detalles.exists() else []

def buscar_pedidos(cliente):
    pedidos = Pedidos.objects.filter(id_cliente=cliente)
    pedidos_con_detalles = []
    for pedido in pedidos:
        detalles = buscar_detalles_pedidos(pedido.id_pedido)
        pedidos_con_detalles.append({
            "id_pedido": pedido.id_pedido,
            "fecha_pedido": pedido.fecha_pedido,
            "total_pedido": pedido.total_pedido,
            "estado": pedido.estado,
            "detalles": detalles
        })
    return pedidos_con_detalles
    
def buscar_cliente(request):
    nombre_cliente = request.GET.get("nombreCliente")
    tipoPedido = request.GET.get("tipoPedido")
    palabras_clave = nombre_cliente.split()
    clientes_encontrados = Clientes.objects.all()
    
    for palabra_clave in palabras_clave:
        clientes_encontrados = clientes_encontrados.filter(
            Q(nombres__icontains=palabra_clave) | Q(apellidos__icontains=palabra_clave)
        )
    
    if tipoPedido == "con pedido":
        clientes_con_pedido = clientes_encontrados.filter(
            pedidos__estado="en proceso"
        ).distinct()
        clientes_encontrados = clientes_con_pedido
    elif tipoPedido == "sin pedido":
        clientes_sin_pedido = clientes_encontrados.filter(
            pedidos__isnull=True
        ).distinct()
        clientes_encontrados = clientes_sin_pedido

    resultados = []
    for cliente in clientes_encontrados:
        pedidos_cliente = buscar_pedidos(cliente) if tipoPedido == "con pedido" else []
        resultados.append({
            "documento": cliente.documento,
            "nombre_cliente": f"{cliente.nombres} {cliente.apellidos}",
            "estado": cliente.estado,
            "pedidos": pedidos_cliente,  
        })

    return JsonResponse({"resultados": resultados})

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
                        'precio_compra': detalle.precio_compra,
                        'precio_venta': detalle.precio_venta,
                        'descuento': detalle.descuentoProducto,
                        'precio_descuento': detalle.totalProductoDescuento,
                        'ganancia': detalle.margenGanancia,
                        'precio_tot': detalle.precio_tot,
                        
                    }
                    detalles_data.append(detalle_data)

                data = {
                    'fechareg': venta.fechareg,
                    'cliente': venta.id_cliente.nombres + ' ' + venta.id_cliente.apellidos,
                    'estado': venta.estado,
                    'documento': venta.id_cliente.documento,
                    'descuentoVenta': venta.descuentoVenta,
                    'totalVentaDescuento': venta.totalVentaDescuento,
                    'margenGanancia': venta.margenGanancia,
                    'totalVenta': venta.totalVenta,
                    'detalles': detalles_data
                }
                return JsonResponse({'success': data})
            except Ventas.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Venta no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de Venta no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})

def cargar_pedidos(request):
    ids_pedidos = request.GET.getlist('ids_pedidos[]')
    detalles_pedidos = list(DetallePedido.objects.filter(id_pedido__in=ids_pedidos).values())
    return JsonResponse({'detalles': detalles_pedidos})

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
        precioUnitario = formatear_precios(detalle.precio_compra) 
        cantidad = detalle.cantidad
        totalProducto = formatear_precios(detalle.precio_tot)
        totalVenta += detalle.precio_tot

        detalles.append([producto, precioUnitario, cantidad, totalProducto])

    totalVentaFormateado = formatear_precios(totalVenta)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Informe_venta_{venta.id_cliente.nombres}_{venta.id_cliente.apellidos}.pdf'

    buffer = response
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()

    elements = []

    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img/GIcon.png')
    logo = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
    logo.drawHeight = 1.5 * inch
    logo.drawWidth = 1.5 * inch
    elements.append(logo)

    elements.append(Spacer(1, 6))
    elements.append(Paragraph('Informe de Venta', styles['Title']))
    elements.append(Spacer(1, 6))

    centered_style = ParagraphStyle(name='CenteredStyle', alignment=TA_CENTER)

    elements.append(Paragraph(f'<b>Cliente:</b> {venta.id_cliente.nombres}', centered_style))
    elements.append(Paragraph(f'<b>Documento:</b> {venta.id_cliente.documento}', centered_style))
    elements.append(Paragraph(f'<b>Fecha de Registro:</b> {venta.fechareg}', centered_style))

    elements.append(Spacer(1, 12))

    data = [["Producto", "Precio Unitario", "Cantidad", "Total"]]
    data.extend(detalles)
    data.append(["", "", "", totalVentaFormateado])  

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

def generar_informe_pdf_ventas(request):
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        
        ventas = Ventas.objects.filter(
            fechareg__range=(fecha_inicio, fecha_fin),
            estado=1
        )

        totalventa = ventas.aggregate(Sum('totalVenta'))['totalVenta__sum'] or 0

        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename=informe_ventas.pdf'

        buffer = response
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = []
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img/GIcon.png')
        logo = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
        logo.drawHeight = 1.5 * inch
        logo.drawWidth = 1.5 * inch
        elements.append(logo)

        elements.append(Spacer(1, 6))
        elements.append(Paragraph('Informe de Ventas', styles['Title']))
        elements.append(Spacer(1, 6))
        
        periodo_style = ParagraphStyle(name='PeriodoStyle', alignment=TA_CENTER, textColor=colors.red)
        periodo_paragraph = Paragraph(f'Período de tiempo: {fecha_inicio} - {fecha_fin}', periodo_style)
        
        elements.append(periodo_paragraph)
        elements.append(Spacer(1, 12))

        if ventas:
            detalles = []

            for venta in ventas:
                clientes = venta.id_cliente.nombres
                documento_nit = venta.id_cliente.documento
                fecha_registro = venta.fechareg
                total_venta = formatear_precios(venta.totalVenta)
                detalles.append([clientes, documento_nit, fecha_registro, total_venta])

            totalventaFormateado = formatear_precios(totalventa)

            data = [["Clientes", "Documento", "Fecha de Registro", "Total"]]
            data.extend(detalles)
            data.append(["", "", "", totalventaFormateado])

            t = Table(data, colWidths=[180, 100, 100, 100])
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
        else:
            mensaje_style = ParagraphStyle(name='MensajeStyle', alignment=TA_CENTER, textColor=colors.red)
            mensaje = Paragraph("No se encontraron ventas en el período de tiempo.", mensaje_style)
            elements.append(mensaje)

        try:
            doc.build(elements)
            print("PDF generado con éxito")
            print(response)
        except Exception as e:
            print(f"Error al generar el PDF: {str(e)}")
            return HttpResponse("No se pudo generar el PDF")

        return response
    return HttpResponse("No se ha enviado una solicitud POST")