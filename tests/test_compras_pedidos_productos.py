"""Compras, pedidos internos y productos."""
import io
import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from eproviders.models import Proveedores
from orders.models import DetallePedido, Pedidos
from purchases.models import Compras
from products.models import Productos
from customers.models import Clientes, Departamentos, Municipios

pytestmark = pytest.mark.django_db


@pytest.fixture
def proveedor(db):
    return Proveedores.objects.create(nombre_proveedor='Prov', telefono='1', correo='p@p.co', direccion='x',
                                      informacion_adicional='-', tipo_documento='NIT', numero_documento_nit='1', estado=1)


def comprar(client, productos, total=1000, proveedor='Prov'):
    return client.post(reverse('crear_compra'), json.dumps({'nombreProveedor': proveedor, 'totalCompra': total, 'productos': productos}),
                       content_type='application/json')


def item(cantidad, precio=100):
    return {'cantidad': cantidad, 'precioCompra': precio, 'totalProducto': precio * (cantidad if isinstance(cantidad, int) else 0)}


def test_compra_suma_stock(admin_client, catalogo, proveedor):
    p = catalogo(cantidad=2)
    assert comprar(admin_client, {str(p.id_producto): item(5)}).status_code == 200
    p.refresh_from_db(); assert p.cantidad == 7


@pytest.mark.parametrize('cantidad', [0, -3, 'x', 2.5])
def test_compra_con_cantidad_invalida_no_toca_nada(admin_client, catalogo, proveedor, cantidad):
    p = catalogo(cantidad=2)
    r = comprar(admin_client, {str(p.id_producto): item(cantidad)})
    assert r.status_code == 400
    p.refresh_from_db(); assert p.cantidad == 2 and Compras.objects.count() == 0


def test_compra_es_todo_o_nada(admin_client, catalogo, proveedor):
    a = catalogo('A', cantidad=1)
    r = comprar(admin_client, {str(a.id_producto): item(4), '99999': item(1)})
    assert r.status_code == 400
    a.refresh_from_db(); assert a.cantidad == 1 and Compras.objects.count() == 0


def anular_compra(client, compra, estado):
    return client.get(reverse('cambiarEstadoCompra'), {'compra_id': compra.id_compra, 'nuevo_estado': estado},
                      HTTP_X_REQUESTED_WITH='XMLHttpRequest').json()


def test_anular_compra_no_permite_stock_negativo(admin_client, catalogo, proveedor):
    p = catalogo(cantidad=0)
    comprar(admin_client, {str(p.id_producto): item(5)})
    compra = Compras.objects.get()
    p.refresh_from_db(); p.cantidad = 2; p.save()          # ya se vendieron 3 de esas 5
    res = anular_compra(admin_client, compra, 0)
    assert res['status'] == 'error'
    compra.refresh_from_db(); p.refresh_from_db()
    assert compra.estado == 1 and p.cantidad == 2          # nada cambió


def test_anular_y_reactivar_compra_es_simetrico(admin_client, catalogo, proveedor):
    p = catalogo(cantidad=0)
    comprar(admin_client, {str(p.id_producto): item(5)})
    compra = Compras.objects.get()
    assert anular_compra(admin_client, compra, 0)['status'] == 'success'
    p.refresh_from_db(); assert p.cantidad == 0
    anular_compra(admin_client, compra, 0)                  # repetir no resta de nuevo
    p.refresh_from_db(); assert p.cantidad == 0
    assert anular_compra(admin_client, compra, 1)['status'] == 'success'
    p.refresh_from_db(); assert p.cantidad == 5


def test_estado_de_compra_exige_sesion(anonimo, db):
    assert anonimo.get(reverse('cambiarEstadoCompra'), {'compra_id': 1, 'nuevo_estado': 0}).status_code == 302


# ------------------------------------------------------------------ pedidos internos
@pytest.fixture
def pedido(db, catalogo):
    p = catalogo(cantidad=5)
    depto = Departamentos.objects.create(nombre_departamento='D')
    muni = Municipios.objects.create(id_departamento=depto, nombre_municipio='M')
    c = Clientes.objects.create(id_municipio=muni, documento='1', nombres='A', apellidos='B', celular='1', barrio='b',
                                direccion='d', estado=True)
    ped = Pedidos.objects.create(id_venta=None, id_cliente_id=c.id_cliente, total_pedido=0, estado='en proceso')
    det = DetallePedido.objects.create(id_pedido=ped, id_producto_id=p.id_producto, sabor='Chocolate', cantidad=1, precio_uni=150, precio_tot=150)
    return ped, det, p


def editar(client, ped, detalles):
    return client.post(reverse('editarPedido'), json.dumps({'dataIdPedido': ped.id_pedido, 'detalles': detalles}),
                       content_type='application/json')


def test_editar_pedido_recalcula_total_en_el_servidor(admin_client, pedido):
    ped, det, _ = pedido
    r = editar(admin_client, ped, [{'id_detalle': det.id_detallepedido, 'sabor': 'Vainilla', 'cantidad': 3, 'total_producto': 1}])
    assert r.status_code == 200
    ped.refresh_from_db(); det.refresh_from_db()
    assert det.cantidad == 3 and det.precio_tot == 450 and ped.total_pedido == 450   # ignora el total del cliente


def test_editar_pedido_valida_stock(admin_client, pedido):
    ped, det, _ = pedido
    r = editar(admin_client, ped, [{'id_detalle': det.id_detallepedido, 'sabor': 'x', 'cantidad': 6, 'total_producto': 1}])
    assert r.status_code == 400 and 'insuficiente' in r.json()['error_message'].lower()
    det.refresh_from_db(); assert det.cantidad == 1


def test_pedido_confirmado_no_se_edita_ni_cancela(admin_client, pedido):
    ped, det, _ = pedido
    ped.estado = 'confirmado'; ped.save()
    assert editar(admin_client, ped, [{'id_detalle': det.id_detallepedido, 'sabor': 'x', 'cantidad': 2, 'total_producto': 1}]).status_code == 400
    r = admin_client.get(reverse('cambiarEstadoPedido'), {'pedido_id': ped.id_pedido}).json()
    assert r['status'] == 'error'
    ped.refresh_from_db(); assert ped.estado == 'confirmado'


def test_cancelar_pedido_en_proceso(admin_client, pedido):
    ped, _, _ = pedido
    assert admin_client.get(reverse('cambiarEstadoPedido'), {'pedido_id': ped.id_pedido}).json()['status'] == 'success'
    ped.refresh_from_db(); assert ped.estado == 'cancelado'


# ------------------------------------------------------------------ productos
def datos_producto(**extra):
    base = {'iNombre': 'Nuevo', 'iDescripcion': 'd', 'iCantidad': '5', 'iFechaven': '2030-05-01', 'iSabor': 'Choco',
            'iServices': '1 lb', 'iPrice': '10.000', 'iPubPrice': '15.000'}
    base.update(extra)
    return base


def png():
    buf = io.BytesIO(); Image.new('RGB', (10, 10), 'red').save(buf, 'PNG')
    return SimpleUploadedFile('p.png', buf.getvalue(), content_type='image/png')


def test_editar_producto_no_lo_reactiva(admin_client, catalogo):
    p = catalogo(cantidad=5, estado=0)
    data = datos_producto(iCategoria=p.id_categoria_id, iMarca=p.id_marca_id)
    assert admin_client.post(reverse('editAProduct', args=[p.id_producto]), data).status_code == 200
    p.refresh_from_db()
    assert p.estado == 0 and p.cantidad == 5 and p.precio == 10000


@pytest.mark.parametrize('campo,valor', [('iCantidad', '-3'), ('iCantidad', 'abc'), ('iCantidad', '2.5'),
                                         ('iPrice', 'gratis'), ('iFechaven', 'mañana'), ('iNombre', '  ')])
def test_producto_rechaza_datos_invalidos(admin_client, catalogo, campo, valor):
    p = catalogo(cantidad=5)
    data = datos_producto(iCategoria=p.id_categoria_id, iMarca=p.id_marca_id, **{campo: valor})
    r = admin_client.post(reverse('editAProduct', args=[p.id_producto]), data)
    assert r.status_code == 400
    p.refresh_from_db(); assert p.cantidad == 5


def test_crear_producto_valida_la_imagen(admin_client, catalogo):
    p = catalogo()
    data = datos_producto(iCategoria=p.id_categoria_id, iMarca=p.id_marca_id)
    falsa = SimpleUploadedFile('x.png', b'no soy una imagen', content_type='image/png')
    assert admin_client.post(reverse('createAProduct'), dict(data, iProductImg=falsa)).status_code == 400
    assert admin_client.post(reverse('createAProduct'), dict(data)).status_code == 400      # sin imagen
    assert admin_client.post(reverse('createAProduct'), dict(data, iProductImg=png())).status_code == 200
    assert Productos.objects.filter(nombre_producto='Nuevo', cantidad=5).exists()


def test_cambiar_estado_de_producto_exige_permiso(cliente_sin_permisos, anonimo, catalogo):
    p = catalogo()
    url = reverse('cambiarEstadoDeProducto')
    args = {'producto_id': p.id_producto, 'nuevo_estado': 0}
    assert anonimo.get(url, args, HTTP_X_REQUESTED_WITH='XMLHttpRequest').status_code == 302
    assert cliente_sin_permisos.get(url, args, HTTP_X_REQUESTED_WITH='XMLHttpRequest').status_code == 302
    p.refresh_from_db(); assert p.estado == 1


# ------------------------------------------------------------------ informes PDF de compras
def test_comprobante_e_informe_de_compras(admin_client, catalogo, proveedor):
    p = catalogo(cantidad=1)
    comprar(admin_client, {str(p.id_producto): item(4, 100)}, total=400)
    compra = Compras.objects.get()
    r = admin_client.get(reverse('generar_factura_pdf', args=[compra.id_compra]))
    assert r.status_code == 200 and r.content.startswith(b'%PDF') and 'comprobante_compra_' in r['Content-Disposition']
    hoy = str(compra.fechareg)
    r = admin_client.post(reverse('generar_informe_pdf'), {'fecha_inicio': hoy, 'fecha_fin': hoy})
    assert r.status_code == 200 and r.content.startswith(b'%PDF')
    assert admin_client.post(reverse('generar_informe_pdf'), {'fecha_inicio': hoy}).status_code == 400
    assert admin_client.post(reverse('generar_informe_pdf'), {'fecha_inicio': '2000-01-01', 'fecha_fin': '2000-01-02'}).status_code == 200
