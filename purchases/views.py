from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from tuiranfitgo.views import jwt_cookie_required
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

@jwt_cookie_required
def Home(request):
    compras = Compras.objects.all()
    return render(request, "purchasesHome.html", {"compras": compras})

@csrf_exempt
@jwt_cookie_required
def crear_compra(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug("Datos JSON recibidos: %s", data)

            proveedor_nombre = data.get('proveedor', '')
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

            for producto_datos in productos:
                producto = Productos.objects.filter(nombre_producto=producto_datos['nombre']).first()

                if not producto:
                    return JsonResponse({'error': f'Producto "{producto_datos["nombre"]}" no encontrado en la base de datos.'}, status=400)

                detalle = Detallecompra.objects.create(
                    id_producto=producto,
                    id_compra=compra,
                    cantidad=producto_datos['cantidad'],
                    precio_uni=producto_datos['precioUnidad'],
                    precio_tot=producto_datos['precioTotal']
                )

                producto.cantidad += producto_datos['cantidad']
                producto.save()

            response_data = {'success': True}
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            logger.error("Error al decodificar datos JSON: %s", request.body)
            return JsonResponse({'error': 'Datos JSON no válidos.'}, status=400)

        except Exception as e:
            logger.error("Error al crear la compra: %s", str(e))
            return JsonResponse({'error': 'Error al crear la compra. Intente nuevamente más tarde.'}, status=500)

    return render(request, 'createPurchases.html')

def buscar_proveedor(request):
    nombre_proveedor = request.GET.get("q", "")

    palabras_clave = nombre_proveedor.split()
    proveedores_encontrados = Proveedores.objects.all()

    for palabra_clave in palabras_clave:
        proveedores_encontrados = proveedores_encontrados.filter(
            Q(nombre_proveedor__icontains=palabra_clave)
        )

    resultados = [
        {
            "documento": proveedor.numero_documento_nit,
            "nombre_proveedor": proveedor.nombre_proveedor,
            "estado": proveedor.estado,
        }
        for proveedor in proveedores_encontrados
    ]

    return JsonResponse({"resultados": resultados})

def buscar_productos(request):
    q = request.GET.get("q", "")
    productos = Productos.objects.filter(
        nombre_producto__icontains=q,
    ).values_list("nombre_producto", flat=True)
    return JsonResponse({"productos": list(productos)})

def validar_producto(request):
    nombre_producto = request.GET.get("nombre_producto", "")
    producto_existe = Productos.objects.filter(nombre_producto=nombre_producto).exists()
    return JsonResponse({"existe": producto_existe})

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
        
        compra = Compras.objects.get(id_compra=compra_id)
        estado_anterior = compra.estado 
        compra.estado = int(nuevo_estado)
        compra.save()

        detalles = Detallecompra.objects.filter(id_compra=compra_id)
        for detalle in detalles:
            producto = detalle.id_producto

            if detalle.estado == 1: 
                if compra.estado == 1: 
                    producto.cantidad += detalle.cantidad  
                else:  
                    producto.cantidad -= detalle.cantidad 

                producto.save()  

            detalle.save() 
        
        if estado_anterior == 0 and nuevo_estado == "1":
            return JsonResponse({'status': 'error', 'message': 'No se puede cambiar de Inactivo a Activo.'})
        else:
            return JsonResponse({'status': 'success'})

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
    response['Content-Disposition'] = f'attachment; filename=factura_compra_{compra.id_proveedor.nombre_proveedor}_{compra.id_proveedor.numero_documento_nit}.pdf'

    buffer = response
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()

   
    elements = []

   
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/img/GIcon.png')
    logo = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
    logo.drawHeight = 1.5 * inch
    logo.drawWidth = 1.5 * inch
    elements.append(logo)

    # Línea roja
    elements.append(Spacer(1, 6))
    elements.append(Paragraph('Factura de Compra', styles['Title']))
    elements.append(Spacer(1, 6))

    centered_style = ParagraphStyle(name='CenteredStyle', alignment=TA_CENTER)

    # Detalles de la factura en la parte superior izquierda
    elements.append(Paragraph(f'<b>Proveedor:</b> {compra.id_proveedor.nombre_proveedor}', centered_style))
    elements.append(Paragraph(f'<b>Documento/NIT:</b> {compra.id_proveedor.numero_documento_nit}', centered_style))
    elements.append(Paragraph(f'<b>Fecha de Registro:</b> {compra.fechareg}', centered_style))

    # Espacio entre detalles y tabla
    elements.append(Spacer(1, 12))

    # Detalles de compra (la tabla)
    data = [["Producto", "Precio Unitario", "Cantidad", "Total"]]
    data.extend(detalles)
    data.append(["", "", "", totalCompraFormateado])  # Agrega el total al final

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













