from control import auditoria as aud
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
from tuiranfitgo.inventory import (StockError, DatosInvalidos, reponer_stock, quitar_stock_compra,
                                    entero_positivo, numero_no_negativo, nombre_imagen)


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
            proveedor_nombre = data.get('nombreProveedor', '')
            productos = data.get('productos', {})

            if not proveedor_nombre:
                return JsonResponse({'error': 'El nombre del proveedor es obligatorio.'}, status=400)

            if not isinstance(productos, dict) or not productos:
                return JsonResponse({'error': 'Debe agregar al menos un producto a la compra.'}, status=400)

            proveedor = Proveedores.objects.filter(nombre_proveedor=proveedor_nombre).first()

            if not proveedor:
                return JsonResponse({'error': 'Proveedor no encontrado en la base de datos.'}, status=400)

            total_compra = numero_no_negativo(data.get('totalCompra'), 'total de la compra')

            # Todo o nada: si un producto falla no queda una compra a medias ni stock sumado
            with transaction.atomic():
                compra = Compras.objects.create(id_proveedor=proveedor, totalCompra=total_compra)

                for producto_id, producto_datos in productos.items():
                    producto_id = entero_positivo(producto_id, 'producto')
                    cantidad_comprada = entero_positivo(producto_datos.get('cantidad'), 'cantidad')
                    precio_compra = numero_no_negativo(producto_datos.get('precioCompra'), 'precio de compra')
                    precio_total = numero_no_negativo(producto_datos.get('totalProducto'), 'total del producto')

                    producto = Productos.objects.filter(pk=producto_id).first()
                    if producto is None:
                        raise DatosInvalidos('Uno de los productos ya no existe.')

                    reponer_stock(Productos, producto_id, cantidad_comprada)

                    Detallecompra.objects.create(
                        id_producto=producto,
                        id_compra=compra,
                        cantidad=cantidad_comprada,
                        precio_uni=precio_compra,
                        precio_tot=precio_total
                    )

            aud.registrar('crear', 'compras', f'Registró la compra #{compra.id_compra:06d} a {proveedor.nombre_proveedor} por ${round(total_compra):,}'.replace(',', '.'),
                          'Compra', compra.id_compra, [{'campo': 'Productos', 'antes': '—', 'despues': f'{len(productos)} producto(s)'}])
            return JsonResponse({'success': True})

        except DatosInvalidos as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

        except (json.JSONDecodeError, AttributeError) as e:
            return JsonResponse({'success': False, 'error': 'Los datos enviados no son válidos.'}, status=400)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return render(request, 'createPurchases.html')


@jwt_cookie_required
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


@jwt_cookie_required
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
            'presentacion': nombre_imagen(producto.iProductImg)
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


@jwt_cookie_required
@module_access_required('compras')
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
                        reponer_stock(Productos, detalle.id_producto_id, detalle.cantidad)
                elif nuevo_estado == "0" and compra.estado == 1:
                    # Restar productos solo si la compra está pasando de Activo a Inactivo
                    detalles = Detallecompra.objects.filter(id_compra=compra_id)
                    for detalle in detalles:
                        # Lanza StockError (y revierte todo) si el stock quedaría negativo
                        quitar_stock_compra(Productos, detalle.id_producto_id, detalle.cantidad)

                cambio = compra.estado != int(nuevo_estado)
                compra.estado = int(nuevo_estado)
                compra.save()

            if cambio:
                aud.registrar('anular' if nuevo_estado == "0" else 'reactivar', 'compras',
                              f'{"Anuló" if nuevo_estado == "0" else "Reactivó"} la compra #{int(compra_id):06d} (el inventario se ajustó)', 'Compra', compra_id)
            return JsonResponse({'status': 'success'})

        except Compras.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Compra no encontrada.'}, status=404)

        except StockError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

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


def generar_qr_code(content):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(content)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


@jwt_cookie_required
@module_access_required('compras')
def generar_factura_pdf(request, compra_id):
    """Comprobante de una compra, con código QR de verificación."""
    from io import BytesIO
    from django.http import HttpResponse
    from reportlab.platypus import Image as PdfImage, Table as PdfTable, TableStyle as PdfTableStyle, Paragraph as PdfParagraph
    from tuiranfitgo.reports import Informe, cop, fecha, esc, E_PEQ, E_CELDA_B, GRIS_FONDO, ANCHO_UTIL

    compra = get_object_or_404(Compras, id_compra=compra_id)
    proveedor = compra.id_proveedor
    detalles = Detallecompra.objects.filter(id_compra=compra_id).select_related('id_producto')

    referencia = f'N° {compra.id_compra:06d}' + ('  ·  ANULADA' if compra.estado == 0 else '')
    informe = Informe('Comprobante de compra', fecha(compra.fechareg), referencia)
    informe.espacio(2)
    informe.ficha([('Proveedor', proveedor.nombre_proveedor), ('Documento / NIT', proveedor.numero_documento_nit),
                   ('Contacto', f'{proveedor.telefono}  ·  {proveedor.correo}'), ('Fecha de compra', fecha(compra.fechareg))])
    informe.seccion('Productos comprados')

    filas, subtotal = [], 0
    for d in detalles:
        filas.append([d.id_producto.nombre_producto, d.cantidad, cop(d.precio_uni), cop(d.precio_tot)])
        subtotal += d.precio_tot
    informe.tabla(['Producto', 'Cant.', 'Precio unitario', 'Total'], filas, [276, 50, 100, 106], 'LCRR')
    informe.totales([('Productos', str(sum(d.cantidad for d in detalles)))], ('Total compra', cop(compra.totalCompra or subtotal)))

    # Código QR de verificación
    qr = generar_qr_code(f'TUIRANFIT|COMPRA|{compra.id_compra}|{round(compra.totalCompra)}|{compra.fechareg}')
    buffer = BytesIO()
    qr.save(buffer, 'PNG')
    buffer.seek(0)
    verificacion = PdfTable([[PdfImage(buffer, 64, 64),
                              [PdfParagraph('<b>CÓDIGO DE VERIFICACIÓN</b>', E_CELDA_B),
                               PdfParagraph(esc(f'Compra N° {compra.id_compra:06d} · {cop(compra.totalCompra)} · {fecha(compra.fechareg)}'), E_PEQ)]]],
                            colWidths=[76, ANCHO_UTIL - 76])
    verificacion.setStyle(PdfTableStyle([('BACKGROUND', (0, 0), (-1, -1), GRIS_FONDO), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 8),
                                         ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    informe.espacio(22)
    informe.adjuntar(verificacion)
    aud.registrar('exportar', 'compras', f'Generó el comprobante de la compra #{compra.id_compra:06d}', 'Compra', compra.id_compra)
    return informe.respuesta(f'comprobante_compra_{compra.id_compra:06d}.pdf')


@jwt_cookie_required
@module_access_required('compras')
def generar_informe_pdf(request):
    from django.db.models import Count, Sum
    from django.http import HttpResponse
    from tuiranfitgo.reports import Informe, cop, fecha, rango_de_fechas

    if request.method != 'POST':
        return HttpResponse('Solicitud no válida.', status=405)
    try:
        inicio, fin = rango_de_fechas(request.POST)
    except ValueError as e:
        return HttpResponse(str(e), status=400)

    compras = list(Compras.objects.filter(fechareg__range=(inicio, fin), estado=1)
                   .select_related('id_proveedor').order_by('fechareg', 'id_compra'))
    informe = Informe('Informe de compras', f'Del {fecha(inicio)} al {fecha(fin)}', 'Compras registradas')
    nombre = f'informe_compras_{inicio}_{fin}.pdf'
    if not compras:
        informe.aviso('No se encontraron compras en el período seleccionado.')
        return informe.respuesta(nombre)

    total = sum(c.totalCompra for c in compras)
    proveedores = {c.id_proveedor_id for c in compras}
    informe.espacio(2)
    informe.tarjetas([('Total comprado', cop(total)), ('N° de compras', str(len(compras))),
                      ('Proveedores', str(len(proveedores))), ('Compra promedio', cop(total / len(compras)))])

    por_proveedor = (Compras.objects.filter(id_compra__in=[c.id_compra for c in compras])
                     .values('id_proveedor__nombre_proveedor')
                     .annotate(n=Count('id_compra'), importe=Sum('totalCompra')).order_by('-importe')[:5])
    informe.seccion('Principales proveedores')
    informe.tabla(['#', 'Proveedor', 'Compras', 'Importe'],
                  [[i, p['id_proveedor__nombre_proveedor'], p['n'], cop(p['importe'])] for i, p in enumerate(por_proveedor, 1)],
                  [30, 292, 80, 130], 'CLCR')

    informe.seccion('Detalle de compras')
    filas = [[f'{c.id_compra:06d}', fecha(c.fechareg), c.id_proveedor.nombre_proveedor,
              c.id_proveedor.numero_documento_nit, cop(c.totalCompra)] for c in compras]
    informe.tabla(['N°', 'Fecha', 'Proveedor', 'Documento / NIT', 'Total'], filas, [60, 70, 190, 100, 112], 'LLLLR',
                  total=['', '', '', 'TOTAL', cop(total)])
    aud.registrar('exportar', 'compras', f'Generó el informe de compras del {fecha(inicio)} al {fecha(fin)} ({len(compras)} compras)')
    return informe.respuesta(nombre)
