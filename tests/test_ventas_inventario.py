"""Ventas: el inventario nunca puede quedar negativo y las anulaciones no duplican ajustes."""
import json

import pytest
from django.urls import reverse

from customers.models import Departamentos, Municipios
from sales.models import Clientes, Detalleventa, Pedidos, DetallePedido, Ventas

pytestmark = pytest.mark.django_db


@pytest.fixture
def cliente_venta(db):
    depto = Departamentos.objects.create(nombre_departamento='Antioquia')
    muni = Municipios.objects.create(id_departamento=depto, nombre_municipio='Medellin')
    from customers.models import Clientes as C
    c = C.objects.create(id_municipio=muni, documento='123', nombres='Ana', apellidos='Ruiz', celular='300',
                         barrio='Centro', direccion='Calle 1', estado=True, correo='ana@test.co')
    return c


def payload(producto, cantidad, id_pedido='no pedido', precio_venta=150, documento='123'):
    return {
        'documentoCliente': documento, 'totalVenta': precio_venta * (cantidad if isinstance(cantidad, int) else 1),
        'descuentoVenta': 'No aplica', 'totalVentaDescuento': 'No aplica', 'margenGananciaVenta': 50,
        'productos': {str(producto.id_producto): {
            'idPedido': id_pedido, 'cantidad': cantidad, 'precioCompra': 100, 'precioVenta': precio_venta,
            'descuentoProducto': 'No aplica', 'margenGananciaProducto': 50,
            'totalProducto': precio_venta * (cantidad if isinstance(cantidad, int) else 1),
            'totalProductoDescuento': 'No aplica'}},
    }


def vender(client, data):
    return client.post(reverse('crear_venta'), json.dumps(data), content_type='application/json')


def test_venta_descuenta_el_stock(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=10)
    r = vender(admin_client, payload(p, 3))
    assert r.status_code == 200 and r.json()['success'] is True
    p.refresh_from_db()
    assert p.cantidad == 7
    assert Detalleventa.objects.get().cantidad == 3


def test_no_se_puede_vender_mas_que_el_stock(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=2)
    r = vender(admin_client, payload(p, 3))
    assert r.status_code == 400
    assert 'insuficiente' in r.json()['error'].lower()
    p.refresh_from_db()
    assert p.cantidad == 2                       # intacto
    assert Ventas.objects.count() == 0           # y no quedó una venta a medias


def test_vender_exactamente_todo_el_stock_deja_cero_no_negativo(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=4)
    assert vender(admin_client, payload(p, 4)).status_code == 200
    p.refresh_from_db()
    assert p.cantidad == 0
    # el siguiente intento de vender 1 más debe fallar
    assert vender(admin_client, payload(p, 1)).status_code == 400
    p.refresh_from_db()
    assert p.cantidad == 0


@pytest.mark.parametrize('cantidad', [0, -1, -5, 'abc', 1.5, None, True])
def test_cantidades_invalidas_se_rechazan(admin_client, catalogo, cliente_venta, cantidad):
    p = catalogo(cantidad=10)
    data = payload(p, 1)
    data['productos'][str(p.id_producto)]['cantidad'] = cantidad
    r = vender(admin_client, data)
    assert r.status_code == 400
    p.refresh_from_db()
    assert p.cantidad == 10 and Ventas.objects.count() == 0


def test_producto_inactivo_no_se_vende(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=5, estado=0)
    assert vender(admin_client, payload(p, 1)).status_code == 400
    p.refresh_from_db()
    assert p.cantidad == 5


def test_si_un_producto_falla_no_se_descuenta_ninguno(admin_client, catalogo, cliente_venta):
    ok, sin_stock = catalogo('A', cantidad=10), catalogo('B', cantidad=1)
    data = payload(ok, 2)
    data['productos'][str(sin_stock.id_producto)] = dict(data['productos'][str(ok.id_producto)], cantidad=5)
    assert vender(admin_client, data).status_code == 400
    ok.refresh_from_db(); sin_stock.refresh_from_db()
    assert (ok.cantidad, sin_stock.cantidad) == (10, 1)
    assert Detalleventa.objects.count() == 0


def test_venta_sin_productos_o_cliente_inexistente(admin_client, catalogo, cliente_venta):
    p = catalogo()
    assert vender(admin_client, dict(payload(p, 1), productos={})).status_code == 400
    assert vender(admin_client, payload(p, 1, documento='nope')).status_code == 400


def test_venta_con_pedido_lo_confirma_y_lo_enlaza(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=10)
    pedido = Pedidos.objects.create(id_venta=None, id_cliente_id=cliente_venta.id_cliente, total_pedido=0, estado='en proceso')
    DetallePedido.objects.create(id_pedido=pedido, id_producto_id=p.id_producto, sabor='Chocolate', cantidad=2, precio_uni=150, precio_tot=300)
    assert vender(admin_client, payload(p, 2, id_pedido=pedido.id_pedido)).status_code == 200
    pedido.refresh_from_db()
    assert pedido.estado == 'confirmado' and pedido.id_venta_id == Ventas.objects.get().id_venta


def test_un_pedido_no_se_confirma_dos_veces(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=10)
    pedido = Pedidos.objects.create(id_venta=None, id_cliente_id=cliente_venta.id_cliente, total_pedido=0, estado='en proceso')
    assert vender(admin_client, payload(p, 1, id_pedido=pedido.id_pedido)).status_code == 200
    r = vender(admin_client, payload(p, 1, id_pedido=pedido.id_pedido))
    assert r.status_code == 400
    p.refresh_from_db()
    assert p.cantidad == 9                        # solo se descontó una vez


def test_pedido_de_otro_cliente_se_rechaza(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=10)
    from customers.models import Clientes as C
    otro = C.objects.create(id_municipio=cliente_venta.id_municipio, documento='999', nombres='Otro', apellidos='X',
                            celular='1', barrio='b', direccion='d', estado=True)
    pedido = Pedidos.objects.create(id_venta=None, id_cliente_id=otro.id_cliente, total_pedido=0, estado='en proceso')
    assert vender(admin_client, payload(p, 1, id_pedido=pedido.id_pedido)).status_code == 400


def cambiar(client, venta, estado):
    return client.get(reverse('cambiarEstadoVentas'), {'venta_id': venta.id_venta, 'nuevo_estado': estado},
                      HTTP_X_REQUESTED_WITH='XMLHttpRequest').json()


def test_anular_devuelve_stock_una_sola_vez(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=10)
    vender(admin_client, payload(p, 4))
    venta = Ventas.objects.get()
    assert cambiar(admin_client, venta, 0)['status'] == 'success'
    p.refresh_from_db(); assert p.cantidad == 10
    # anular de nuevo NO debe sumar otra vez
    assert cambiar(admin_client, venta, 0)['status'] == 'success'
    p.refresh_from_db(); assert p.cantidad == 10


def test_reactivar_vuelve_a_descontar_y_valida_stock(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=5)
    vender(admin_client, payload(p, 5))
    venta = Ventas.objects.get()
    cambiar(admin_client, venta, 0)
    # mientras está anulada se vende todo el stock a otra persona
    p.refresh_from_db(); p.cantidad = 1; p.save()
    res = cambiar(admin_client, venta, 1)
    assert res['status'] == 'error'
    venta.refresh_from_db(); p.refresh_from_db()
    assert venta.estado == 0 and p.cantidad == 1  # nada cambió
    p.cantidad = 8; p.save()
    assert cambiar(admin_client, venta, 1)['status'] == 'success'
    p.refresh_from_db(); assert p.cantidad == 3


def test_anular_venta_cancela_su_pedido(admin_client, catalogo, cliente_venta):
    p = catalogo(cantidad=10)
    pedido = Pedidos.objects.create(id_venta=None, id_cliente_id=cliente_venta.id_cliente, total_pedido=0, estado='en proceso')
    vender(admin_client, payload(p, 1, id_pedido=pedido.id_pedido))
    cambiar(admin_client, Ventas.objects.get(), 0)
    pedido.refresh_from_db()
    assert pedido.estado == 'cancelado'


def test_endpoints_de_ventas_exigen_sesion(anonimo, catalogo, cliente_venta):
    p = catalogo()
    assert anonimo.get(reverse('cambiarEstadoVentas'), {'venta_id': 1, 'nuevo_estado': 0}).status_code == 302
    assert anonimo.get(reverse('buscar_productos'), {'q': 'a'}).status_code == 302
    assert anonimo.get(reverse('buscar_cliente'), {'nombreCliente': 'a'}).status_code == 302
    assert anonimo.post(reverse('crear_venta'), json.dumps(payload(p, 1)), content_type='application/json').status_code == 302
    p.refresh_from_db(); assert p.cantidad == 10


def test_verificar_stock(admin_client, catalogo):
    p = catalogo(cantidad=3)
    r = admin_client.get(reverse('verificar_stock'), {'id_producto': p.id_producto, 'cantidad': 4}).json()
    assert r == {'supera_stock': True, 'cantidad_disponible': 3}
    assert admin_client.get(reverse('verificar_stock'), {'id_producto': p.id_producto, 'cantidad': 3}).json()['supera_stock'] is False
    assert admin_client.get(reverse('verificar_stock'), {'id_producto': 99999, 'cantidad': 1}).json()['supera_stock'] is True
