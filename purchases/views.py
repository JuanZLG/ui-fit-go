from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from tuiranfitgo.views import jwt_cookie_required,module_access_required
from .models import Compras, Detallecompra, Proveedores, Productos
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from django.http import HttpResponse
import os
import json
import logging 
logger = logging.getLogger(__name__)
from django.db.models import Q
import qrcode
from django.db import transaction


@jwt_cookie_required
@module_access_required('compras')
def Home(request):
    compras = Compras.objects.all()
    return render(request, "purchasesHome.html", {"compras": compras})

@csrf_exempt
@jwt_cookie_required
@module_access_required('compras')
def crear_compra(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            proveedor_nombre = data.get('nombreProveedor', '')
            totalCompra = data.get('totalCompra', '')
            productos = data.get('productos', [])

            if not proveedor_nombre:
                return JsonResponse({'error': 'El nombre del proveedor es obligatorio.'}, status=400)

            if not productos:
                return JsonResponse({'error': 'Debe agregar al menos un producto a la compra.'}, status=400)

            proveedor = Proveedores.objects.filter(nombre_proveedor=proveedor_nombre).first()

            if not proveedor:
                return JsonResponse({'error': 'Proveedor no encontrado en la base de datos.'}, status=400)

            compra = Compras.objects.create(id_proveedor=proveedor, totalCompra=totalCompra)

            for producto_id, producto_datos in productos.items():
                cantidad_comprada = producto_datos['cantidad']
                precioCompra = producto_datos['precioCompra']
                precioTotal = producto_datos['totalProducto']

                producto = Productos.objects.get(id_producto=producto_id)

                if producto:
                    producto.cantidad += cantidad_comprada
                    producto.save()

                Detallecompra.objects.create(
                    id_producto=producto,
                    id_compra=compra,
                    cantidad=cantidad_comprada,
                    precio_uni=precioCompra,
                    precio_tot=precioTotal
                )

            response_data = {'success': True}
            return JsonResponse(response_data)

        except json.JSONDecodeError as e:
            response_data = {'success': False, 'error': str(e)}
            return JsonResponse(response_data, status=400)

        except Exception as e:
            response_data = {'success': False, 'error': str(e)}
            return JsonResponse(response_data, status=500)

    return render(request, 'createPurchases.html')


def buscar_proveedor(request):
    nombre_proveedor = request.GET.get("q", "")

    palabras_clave = nombre_proveedor.split()

    # Utiliza Q() para realizar la búsqueda de manera más eficiente
    q_objects = Q()
    for palabra_clave in palabras_clave:
        q_objects |= Q(nombre_proveedor__icontains=palabra_clave) 

    # Utiliza filter() solo una vez para mejorar el rendimiento
    proveedores_encontrados = Proveedores.objects.filter(q_objects)

    resultados = [
        {
            "id_proveedor": proveedor.id_proveedor,
            "nombre_proveedor": proveedor.nombre_proveedor,
            "estado": proveedor.estado,
        }
        for proveedor in proveedores_encontrados
    ]

    return JsonResponse({"resultados": resultados})


def buscar_productos(request):
    q = request.GET.get("q", "")

    productos = Productos.objects.filter(
        Q(nombre_producto__icontains=q )
    )

    resultados = []
    for producto in productos:
        precio_ganancia = producto.precio_pub - producto.precio 

        resultados.append({
            'id_producto': producto.id_producto,
            'estado': producto.estado,
            'nombre_producto': producto.nombre_producto,
            'cantidad': producto.cantidad,
            'descripcion': producto.descripcion,
            'precio_compra': producto.precio,
            'precio_venta': producto.precio_pub,
            'precio_ganancia': precio_ganancia,
            'marca': producto.id_marca.nombre_marca,
            'categoria': producto.id_categoria.nombre_categoria,
            'presentacion': producto.iProductImg.decode('utf8')
        })

    return JsonResponse({"resultados": resultados})



@jwt_cookie_required
def detalles_compra(request, compra_id):
    detalles = Detallecompra.objects.filter(id_compra=compra_id)
    detalles_data = []

    for detalle in detalles:
        producto = Productos.objects.get(id_producto=detalle.id_producto)
        detalle_data = {
            'producto': producto.nombre_producto,
            'cantidad': detalle.cantidad,
            'precio_uni': detalle.precio_uni,
            'precio_tot': detalle.precio_tot,
        }

        detalles_data.append(detalle_data)

    return JsonResponse({'detallecompra': detalles_data})


def cambiarEstado(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        compra_id = request.GET.get('compra_id')
        nuevo_estado = request.GET.get('nuevo_estado')

        try:
            with transaction.atomic():
                compra = Compras.objects.select_for_update().get(id_compra=compra_id)
                
                if nuevo_estado == "1" and compra.estado == 0:
                    # Sumar productos solo si la compra está pasando de Inactivo a Activo
                    detalles = Detallecompra.objects.filter(id_compra=compra_id)
                    for detalle in detalles:
                        producto = detalle.id_producto
                        producto.cantidad += detalle.cantidad
                        producto.save()
                elif nuevo_estado == "0" and compra.estado == 1:
                    # Restar productos solo si la compra está pasando de Activo a Inactivo
                    detalles = Detallecompra.objects.filter(id_compra=compra_id)
                    for detalle in detalles:
                        producto = detalle.id_producto
                        producto.cantidad -= detalle.cantidad
                        if producto.cantidad < 0:
                            # Revertir cambios y retornar mensaje de error
                            transaction.set_rollback(True)
                            return JsonResponse({'status': 'error', 'message': 'No es posible desactivar la compra, pues su stock quedaría negativo.'})

                        producto.save()

                compra.estado = int(nuevo_estado)
                compra.save()

            return JsonResponse({'status': 'success'})

        except Compras.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Compra no encontrada.'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Solicitud no válida.'}, status=400)



@jwt_cookie_required
def obtener_detalles_compra(request, compra_id):
    detalles_compra = Detallecompra.objects.filter(id_compra=compra_id)

    detalles = [
        {
            'producto': detalle.id_producto.nombre_producto,
            'precioUnitario': str(detalle.precio_uni),
            'totalProducto': str(detalle.precio_tot),
            'cantidad': detalle.cantidad
            
        }
        for detalle in detalles_compra
    ]

    compra = detalles_compra.first().id_compra 
    datos_generales = {
        'proveedor': compra.id_proveedor.nombre_proveedor,
        'documento': compra.id_proveedor.numero_documento_nit,

        
        'fechaRegistro': compra.fechareg,
        'estado': 'Activo' if compra.estado == 1 else 'Inactivo',
    }

    respuesta = {
        'proveedor': datos_generales['proveedor'],
        'documento': datos_generales['documento'],
        'fechaRegistro': str(datos_generales['fechaRegistro']),
        'estado': datos_generales['estado'],
        'detalles': detalles,
    }

    return JsonResponse(respuesta)

# @csrf_exempt
# def editar_compra(request, id_compra):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             print("Datos recibidos en la solicitud POST:", data)  # Imprimir los datos recibidos en el servidor

#             proveedor_nombre = data.get('proveedor', '')
#             totalCompra = data.get('totalCompra', 0)
#             productos = data.get('productos', [])

#             compra = Compras.objects.get(id_compra=id_compra)

#             if proveedor_nombre:
#                 proveedor = Proveedores.objects.get(nombre_proveedor=proveedor_nombre)
#                 compra.id_proveedor = proveedor
#             compra.totalCompra = totalCompra
#             compra.save()

#             productos_nuevos = []
#             productos_actualizar = []
#             for producto in productos:
#                 if producto["idDetalle"] is None or producto["idDetalle"] == "":
#                     productos_nuevos.append(producto)
#                 else:
#                     productos_actualizar.append(producto)
                    
#             detalles = Detallecompra.objects.filter(id_compra=compra)
            
#             idDetalles_faltantes = [detalle.id_detallecompra for detalle in detalles if detalle.id_detallecompra not in [producto["idDetalle"] for producto in productos]]

#             Detallecompra.objects.filter(id_detallecompra__in=idDetalles_faltantes).delete()

#             for productoDatos in productos_actualizar:
#                 nombre_producto = productoDatos["nombre"]
#                 id_detalle = productoDatos["idDetalle"]
#                 detalle = Detallecompra.objects.get(id_detallecompra=id_detalle)
#                 producto = Productos.objects.get(nombre_producto=nombre_producto)
#                 try:
#                     detalle.id_producto = producto
#                     detalle.cantidad = productoDatos["cantidad"]
#                     detalle.precio_uni = productoDatos["precioUnidad"]
#                     detalle.precio_tot = productoDatos["precioTotal"]
#                     detalle.save()
#                 except Exception as e:
#                     print(f"Error al guardar detalle: {str(e)}")
        

#             for productoDatos in productos_nuevos:
#                 nombre_producto = productoDatos["nombre"]
#                 producto = Productos.objects.get(nombre_producto=nombre_producto)
#                 try:
#                     Detallecompra.objects.create(
#                     id_producto=producto,
#                     id_compra=compra,
#                     cantidad=productoDatos["cantidad"],
#                     precio_uni=productoDatos["precioUnidad"],
#                     precio_tot=productoDatos["precioTotal"]
#                 )
#                 except Exception as e:
#                     print(f"Error al guardar detalle: {str(e)}")



#             response_data = {'success': True}
#         except Exception as e:
#             response_data = {'success': False, 'error_message': str(e)}
#             print("Error en la vista editar_compra:", str(e))  # Imprimir cualquier error que ocurra

#         return JsonResponse(response_data)

#     compra = Compras.objects.get(id_compra=id_compra)
#     detalles = Detallecompra.objects.filter(id_compra=id_compra)
#     return render(request, 'editPurchases.html', {"detalles": detalles, "compra": compra})


def formatear_precios(valor):
    valor = round(valor, 2)
    precio_formateado = '${:,.2f}'.format(valor)
    return precio_formateado
def generar_qr_code(content):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def generar_factura_pdf(request, compra_id):
    compra = get_object_or_404(Compras, id_compra=compra_id)
    detalles_compra = Detallecompra.objects.filter(id_compra=compra_id)

    totalCompra = 0
    detalles = []

    for detalle in detalles_compra:
        producto = detalle.id_producto.nombre_producto
        precioUnitario = formatear_precios(detalle.precio_uni)
        cantidad = detalle.cantidad
        totalProducto = formatear_precios(detalle.precio_tot)
        totalCompra += detalle.precio_tot

        detalles.append([producto, precioUnitario, cantidad, totalProducto])

    totalCompraFormateado = formatear_precios(totalCompra)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Informe_compra_{compra.id_proveedor.nombre_proveedor}_{compra.id_proveedor.numero_documento_nit}.pdf'

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
    elements.append(Paragraph('Informe de Compra', styles['Title']))
    elements.append(Spacer(1, 6))

    centered_style = ParagraphStyle(name='CenteredStyle', alignment=TA_CENTER)

    elements.append(Paragraph(f'<b>Proveedor:</b> {compra.id_proveedor.nombre_proveedor}', centered_style))
    elements.append(Paragraph(f'<b>Documento/NIT:</b> {compra.id_proveedor.numero_documento_nit}', centered_style))
    elements.append(Paragraph(f'<b>Fecha de Registro:</b> {compra.fechareg}', centered_style))

    elements.append(Spacer(1, 12))

    data = [["Producto", "Precio Unitario", "Cantidad", "Total"]]
    data.extend(detalles)
    data.append(["", "", "", totalCompraFormateado])  

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
    print(response)

    return response

def generar_informe_pdf(request):
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        
        compras = Compras.objects.filter(
            fechareg__range=(fecha_inicio, fecha_fin),
            estado=1
        )

        totalCompra = 0
        detalles = []

        for compra in compras:
            proveedor = compra.id_proveedor.nombre_proveedor
            documento_nit = compra.id_proveedor.numero_documento_nit
            fecha_registro = compra.fechareg
            total_compra = formatear_precios(compra.totalCompra)
            detalles.append([proveedor, documento_nit, fecha_registro, total_compra])
            totalCompra += compra.totalCompra

        totalCompraFormateado = formatear_precios(totalCompra)

        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename=informe_compras.pdf'

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
        elements.append(Paragraph('Informe de Compras', styles['Title']))
        elements.append(Spacer(1, 6))
        
        periodo_style = ParagraphStyle(name='PeriodoStyle', alignment=TA_CENTER, textColor=colors.red)
        periodo_paragraph = Paragraph(f'Período de tiempo: {fecha_inicio} - {fecha_fin}', periodo_style)
        
        elements.append(periodo_paragraph)
        elements.append(Spacer(1, 12))

        if compras:
            data = [["Proveedor", "Documento/NIT", "Fecha de Registro", "Total"]]
            data.extend(detalles)
            data.append(["", "", "", totalCompraFormateado])

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
       
            mensaje_style = ParagraphStyle(
                name='MensajeStyle',
                alignment=TA_CENTER,
                textColor=colors.red
            )
            mensaje = Paragraph("No se encontraron compras en el período de tiempo.", mensaje_style)
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




















