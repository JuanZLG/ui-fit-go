from control import auditoria as aud
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import locale
import os
import smtplib
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from tuiranfitgo.views import jwt_cookie_required, module_access_required
import json
from sales.models import Clientes, Detalleventa, Ventas, Productos, Marcas, Categorias, Pedidos, DetallePedido

from django.db import transaction
from django.db.models import Q
import logging
from tuiranfitgo.inventory import (
    StockError, DatosInvalidos, descontar_stock, reponer_stock,
    entero_positivo, numero_no_negativo, nombre_imagen,
)

logger = logging.getLogger(__name__)


def _error(mensaje, status=400):
    return JsonResponse({'success': False, 'error': mensaje}, status=status)


@jwt_cookie_required
@module_access_required('ventas')
def Home(request):
    ventas = Ventas.objects.all()
    return render(request, "salesHome.html", {"ventas": ventas})

def formatear_precios_email(valor):
    valor = round(valor, 2)
    precio_formateado = '${:,.2f}'.format(valor)
    return precio_formateado

@transaction.atomic
def _registrar_venta(data):
    """Crea la venta, sus detalles y descuenta el inventario. Todo o nada."""
    documento = str(data.get('documentoCliente', '')).strip()
    cliente = Clientes.objects.filter(documento=documento).first()
    if cliente is None:
        raise DatosInvalidos('Cliente no encontrado.')
    if cliente.estado != 1:
        raise DatosInvalidos('El cliente está inactivo.')

    productos = data.get('productos')
    if not isinstance(productos, dict) or not productos:
        raise DatosInvalidos('Debe agregar al menos un producto a la venta.')

    total_venta = numero_no_negativo(data.get('totalVenta'), 'total de la venta')
    margen_venta = float(data.get('margenGananciaVenta') or 0)

    # Un pedido solo puede confirmarse una vez y por su propio cliente
    ids_pedido = set()
    for datos in productos.values():
        id_pedido = datos.get('idPedido')
        if isinstance(id_pedido, int) or (isinstance(id_pedido, str) and id_pedido.isdigit()):
            ids_pedido.add(int(id_pedido))
    if len(ids_pedido) > 1:
        raise DatosInvalidos('La venta no puede mezclar productos de pedidos distintos.')

    pedido = None
    if ids_pedido:
        pedido = Pedidos.objects.select_for_update().filter(id_pedido=ids_pedido.pop()).first()
        if pedido is None:
            raise DatosInvalidos('El pedido indicado no existe.')
        if pedido.id_cliente_id != cliente.id_cliente:
            raise DatosInvalidos('El pedido pertenece a otro cliente.')
        if pedido.estado != 'en proceso':
            raise DatosInvalidos(f'El pedido ya está {pedido.estado}; no se puede volver a confirmar.')

    venta = Ventas.objects.create(
        id_cliente=cliente,
        totalVenta=total_venta,
        descuentoVenta=str(data.get('descuentoVenta', 'No aplica')),
        totalVentaDescuento=str(data.get('totalVentaDescuento', 'No aplica')),
        margenGanancia=margen_venta,
    )

    detalles_email = []
    for id_producto, datos in productos.items():
        id_producto = entero_positivo(id_producto, 'producto')
        cantidad = entero_positivo(datos.get('cantidad'), 'cantidad')
        precio_compra = numero_no_negativo(datos.get('precioCompra'), 'precio de compra')
        precio_venta = numero_no_negativo(datos.get('precioVenta'), 'precio de venta')
        total_producto = numero_no_negativo(datos.get('totalProducto'), 'total del producto')
        margen_producto = float(datos.get('margenGananciaProducto') or 0)
        descuento = str(datos.get('descuentoProducto', 'No aplica'))

        # Descuento atómico: falla si no alcanza el stock (nunca queda negativo)
        descontar_stock(Productos, id_producto, cantidad)
        producto = Productos.objects.get(pk=id_producto)

        Detalleventa.objects.create(
            id_producto=producto, id_venta=venta, cantidad=cantidad,
            precio_compra=precio_compra, precio_venta=precio_venta,
            descuentoProducto=descuento,
            totalProductoDescuento=str(datos.get('totalProductoDescuento', 'No aplica')),
            margenGanancia=margen_producto, precio_tot=total_producto,
        )

        if pedido is not None:
            DetallePedido.objects.filter(id_pedido=pedido, id_producto=producto).update(
                cantidad=cantidad, precio_uni=precio_venta, precio_tot=total_producto,
            )

        detalles_email.append({
            'nombre_producto': producto.nombre_producto,
            'url': nombre_imagen(producto.iProductImg),
            'cantidad': cantidad,
            'precio_venta': formatear_precios_email(precio_venta),
            'precio_tot': formatear_precios_email(total_producto),
            'descuentoProducto': descuento,
        })

    if pedido is not None:
        pedido.total_pedido = total_venta
        pedido.estado = 'confirmado'
        pedido.id_venta = venta          # enlaza el pedido con su venta (para poder anularlo juntos)
        pedido.save()

    return venta, cliente, detalles_email


@csrf_exempt
@jwt_cookie_required
@module_access_required('ventas')
def crear_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _error('Los datos enviados no son válidos.')
        if not isinstance(data, dict):
            return _error('Los datos enviados no son válidos.')

        try:
            venta, cliente, detalles_email = _registrar_venta(data)
        except (DatosInvalidos, StockError) as e:
            return _error(str(e))

        # El correo se envía fuera de la transacción: si falla, la venta ya quedó registrada
        try:
            pedido_email_confirmacion(venta, cliente.correo, detalles_email,
                                      formatear_precios_email(venta.totalVenta))
        except Exception:
            logger.exception('No se pudo enviar el correo de la venta %s', venta.id_venta)

        aud.registrar('crear', 'ventas',
                      f'Registró la venta #{venta.id_venta:06d} de {cliente.nombres} {cliente.apellidos} por ${round(venta.totalVenta):,}'.replace(',', '.'),
                      'Venta', venta.id_venta,
                      [{'campo': 'Productos', 'antes': '—', 'despues': ', '.join(f"{d['cantidad']}× {d['nombre_producto']}" for d in detalles_email)}])
        return JsonResponse({'success': True, 'id_venta': venta.id_venta})

    clientes = Clientes.objects.all()
    return render(request, 'createSales.html', {'clientes': clientes})


from django.template.loader import get_template

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


@jwt_cookie_required
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
            'presentacion': nombre_imagen(producto.iProductImg)
        })

    return JsonResponse({"resultados": resultados})


@jwt_cookie_required
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
        'presentacion': nombre_imagen(producto.iProductImg)
    }

    return JsonResponse({"resultado": resultado})



@jwt_cookie_required
def verificar_stock(request):
    try:
        cantidad = int(request.GET.get('cantidad', '0'))
    except (TypeError, ValueError):
        cantidad = 0
    id_producto = request.GET.get('id_producto', '')
    producto = Productos.objects.filter(pk=id_producto).first() if id_producto.isdigit() else None
    if producto is None:
        return JsonResponse({'supera_stock': True, 'cantidad_disponible': 0})
    disponible = max(producto.cantidad, 0)
    return JsonResponse({'supera_stock': cantidad > disponible, 'cantidad_disponible': disponible})

from django.http import JsonResponse
from django.db.models import Q

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
    

@jwt_cookie_required
def buscar_cliente(request):
    nombre_cliente = (request.GET.get("nombreCliente") or "").strip()
    tipoPedido = request.GET.get("tipoPedido")
    palabras_clave = nombre_cliente.split()
    clientes_encontrados = Clientes.objects.all()

    # Cada palabra puede coincidir con el nombre, el apellido o el documento
    for palabra_clave in palabras_clave:
        clientes_encontrados = clientes_encontrados.filter(
            Q(nombres__icontains=palabra_clave) | Q(apellidos__icontains=palabra_clave)
            | Q(documento__icontains=palabra_clave)
        )

    if tipoPedido == "con pedido":
        # Solo clientes que tienen un pedido en proceso por confirmar
        clientes_encontrados = clientes_encontrados.filter(pedidos__estado="en proceso").distinct()
    # "sin pedido": cualquier cliente puede comprar sin pedido previo, tenga o no historial de pedidos
    # (antes solo aparecian los clientes que NUNCA habian hecho un pedido y la venta quedaba bloqueada)
    clientes_encontrados = clientes_encontrados[:30]

    resultados = []
    for cliente in clientes_encontrados:
        pedidos_cliente = buscar_pedidos(cliente) if tipoPedido == "con pedido" else []
        resultados.append({
            "documento": cliente.documento,
            "nombre_cliente": f"{cliente.nombres} {cliente.apellidos}",
            "estado": 1 if cliente.estado else 0,     # siempre 0/1 (segun la base llegaba como true/false)
            "pedidos": pedidos_cliente,  
        })

    return JsonResponse({"resultados": resultados})


@jwt_cookie_required
@module_access_required('ventas')
def cambiarEstado(request):
    """Anula (0) o reactiva (1) una venta ajustando el inventario una sola vez."""
    if request.method != "GET" or request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Solicitud no válida.'}, status=400)

    try:
        nuevo_estado = int(request.GET.get('nuevo_estado'))
        if nuevo_estado not in (0, 1):
            raise ValueError
        venta_id = int(request.GET.get('venta_id'))
    except (TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Datos no válidos.'}, status=400)

    cambio = False
    try:
        with transaction.atomic():
            venta = Ventas.objects.select_for_update().get(id_venta=venta_id)

            # Si la venta ya está en ese estado no se toca el inventario (evita duplicar ajustes)
            if venta.estado != nuevo_estado:
                cambio = True
                detalles = Detalleventa.objects.filter(id_venta=venta.id_venta)
                if nuevo_estado == 0:
                    for detalle in detalles.filter(estado=1):
                        reponer_stock(Productos, detalle.id_producto_id, detalle.cantidad)
                    detalles.update(estado=0)
                    Pedidos.objects.filter(id_venta=venta.id_venta).update(estado='cancelado')
                else:
                    for detalle in detalles.filter(estado=0):
                        descontar_stock(Productos, detalle.id_producto_id, detalle.cantidad)
                    detalles.update(estado=1)
                    Pedidos.objects.filter(id_venta=venta.id_venta).update(estado='confirmado')
                venta.estado = nuevo_estado
                venta.save(update_fields=['estado'])
    except Ventas.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Venta no encontrada.'}, status=404)
    except StockError as e:
        return JsonResponse({'status': 'error', 'message': f'No se puede reactivar la venta. {e}'})

    if cambio:
        aud.registrar('anular' if nuevo_estado == 0 else 'reactivar', 'ventas',
                      f'{"Anuló" if nuevo_estado == 0 else "Reactivó"} la venta #{venta_id:06d} (el inventario se ajustó)', 'Venta', venta_id,
                      [{'campo': 'Estado', 'antes': 'Activa' if nuevo_estado == 0 else 'Anulada', 'despues': 'Anulada' if nuevo_estado == 0 else 'Activa'}])
    return JsonResponse({'status': 'success'})



@jwt_cookie_required
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


@jwt_cookie_required
def cargar_pedidos(request):
    ids_pedidos = request.GET.getlist('ids_pedidos[]')
    detalles_pedidos = list(DetallePedido.objects.filter(id_pedido__in=ids_pedidos).values())
    return JsonResponse({'detalles': detalles_pedidos})

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from tuiranfitgo.reports import Informe, cop, fecha, rango_de_fechas


def _porcentaje(texto):
    """'10' -> '10%'; 'No aplica' / '0' -> '—'."""
    try:
        valor = float(str(texto).replace('%', '').strip())
    except ValueError:
        return '—'
    return f'{valor:g}%' if valor > 0 else '—'


@jwt_cookie_required
@module_access_required('ventas')
def generar_factura_pdf_venta(request, venta_id):
    """Comprobante de una venta. Muestra el precio de VENTA (antes mostraba el de compra)."""
    venta = get_object_or_404(Ventas, id_venta=venta_id)
    cliente = venta.id_cliente
    detalles = Detalleventa.objects.filter(id_venta=venta_id).select_related('id_producto')

    referencia = f'N° {venta.id_venta:06d}' + ('  ·  ANULADA' if venta.estado == 0 else '')
    informe = Informe('Comprobante de venta', fecha(venta.fechareg), referencia)
    informe.espacio(2)
    informe.ficha([
        ('Cliente', f'{cliente.nombres} {cliente.apellidos}'.strip()), ('Documento', cliente.documento),
        ('Correo', cliente.correo), ('Fecha de venta', fecha(venta.fechareg)),
    ])
    informe.seccion('Detalle de la venta')

    filas, subtotal = [], 0
    for d in detalles:
        filas.append([d.id_producto.nombre_producto, d.cantidad, cop(d.precio_venta),
                      _porcentaje(d.descuentoProducto), cop(d.precio_tot)])
        subtotal += d.precio_tot
    informe.tabla(['Producto', 'Cant.', 'Precio unitario', 'Desc.', 'Total'], filas, [226, 44, 90, 50, 122], 'LCRCR')

    lineas = [('Subtotal', cop(subtotal))]
    descuento = subtotal - venta.totalVenta
    if descuento > 0.5:
        porcentaje = _porcentaje(venta.descuentoVenta)
        lineas.append((f'Descuento {porcentaje}' if porcentaje != '—' else 'Descuento', '-' + cop(descuento)))
    informe.totales(lineas, ('Total', cop(venta.totalVenta)))
    informe.espacio(26)
    informe.parrafo('Gracias por tu compra. Conserva este comprobante como soporte de tu pedido.')
    aud.registrar('exportar', 'ventas', f'Generó el comprobante de la venta #{venta.id_venta:06d}', 'Venta', venta.id_venta)
    return informe.respuesta(f'comprobante_venta_{venta.id_venta:06d}.pdf')


@jwt_cookie_required
@module_access_required('ventas')
def generar_informe_pdf_ventas(request):
    if request.method != 'POST':
        return HttpResponse('Solicitud no válida.', status=405)
    try:
        inicio, fin = rango_de_fechas(request.POST)
    except ValueError as e:
        return HttpResponse(str(e), status=400)

    ventas = list(Ventas.objects.filter(fechareg__range=(inicio, fin), estado=1)
                  .select_related('id_cliente').order_by('fechareg', 'id_venta'))
    informe = Informe('Informe de ventas', f'Del {fecha(inicio)} al {fecha(fin)}', 'Ventas registradas')
    nombre = f'informe_ventas_{inicio}_{fin}.pdf'
    if not ventas:
        informe.aviso('No se encontraron ventas en el período seleccionado.')
        return informe.respuesta(nombre)

    total = sum(v.totalVenta for v in ventas)
    margen = sum(v.margenGanancia for v in ventas)
    informe.espacio(2)
    informe.tarjetas([('Total vendido', cop(total)), ('N° de ventas', str(len(ventas))),
                      ('Ticket promedio', cop(total / len(ventas))),
                      ('Margen de ganancia', cop(margen))])

    top = (Detalleventa.objects.filter(id_venta__in=[v.id_venta for v in ventas], estado=1)
           .values('id_producto__nombre_producto')
           .annotate(unidades=Sum('cantidad'), ingresos=Sum('precio_tot')).order_by('-unidades')[:5])
    if top:
        informe.seccion('Productos más vendidos')
        informe.tabla(['#', 'Producto', 'Unidades', 'Ingresos'],
                      [[i, t['id_producto__nombre_producto'], t['unidades'], cop(t['ingresos'])] for i, t in enumerate(top, 1)],
                      [30, 292, 80, 130], 'CLCR')

    informe.seccion('Detalle de ventas')
    filas = [[f'{v.id_venta:06d}', fecha(v.fechareg), f'{v.id_cliente.nombres} {v.id_cliente.apellidos}'.strip(),
              v.id_cliente.documento, cop(v.totalVenta)] for v in ventas]
    informe.tabla(['N°', 'Fecha', 'Cliente', 'Documento', 'Total'], filas, [60, 70, 200, 90, 112], 'LLLLR',
                  total=['', '', '', 'TOTAL', cop(total)])
    aud.registrar('exportar', 'ventas', f'Generó el informe de ventas del {fecha(inicio)} al {fecha(fin)} ({len(ventas)} ventas)')
    return informe.respuesta(nombre)


@jwt_cookie_required
@module_access_required('ventas')
def pos(request):
    """Venta rápida: catálogo táctil + carrito. Usa los mismos endpoints (y validaciones) de la venta normal."""
    return render(request, 'posSales.html')
