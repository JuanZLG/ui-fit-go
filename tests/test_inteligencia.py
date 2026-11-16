"""Inteligencia de inventario, marcador comparativo, orden de compra sugerida y búsqueda global."""
from datetime import date, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from customers.models import Clientes, Departamentos, Municipios
from dashboard import insights
from sales.models import Detalleventa, Ventas

pytestmark = pytest.mark.django_db


@pytest.fixture
def cliente(db):
    depto = Departamentos.objects.create(nombre_departamento='Antioquia')
    muni = Municipios.objects.create(id_departamento=depto, nombre_municipio='Medellin')
    return Clientes.objects.create(id_municipio=muni, documento='900', nombres='Marta', apellidos='Lopez', celular='300',
                                   barrio='b', direccion='d', estado=True, correo='m@t.co')


def vender_hace(cliente, producto, dias, unidades, total=None):
    fecha = timezone.localdate() - timedelta(days=dias)
    total = total if total is not None else unidades * producto.precio_pub
    venta = Ventas.objects.create(id_cliente_id=cliente.id_cliente, fechareg=fecha, totalVenta=total, margenGanancia=total * .3,
                                  descuentoVenta='', totalVentaDescuento='', estado=1)
    Detalleventa.objects.create(id_producto_id=producto.id_producto, id_venta=venta, cantidad=unidades, precio_compra=producto.precio,
                                precio_venta=producto.precio_pub, descuentoProducto='', totalProductoDescuento='',
                                margenGanancia=1, precio_tot=total, estado=1)
    return venta


def test_reposicion_predice_dias_y_sugiere_compra(catalogo, cliente):
    p = catalogo('Whey', cantidad=5, precio=100)
    vender_hace(cliente, p, 3, 30)                       # 30 unidades en 30 dias = 1 por dia
    fila = [r for r in insights.reposicion() if r['id_producto'] == p.id_producto][0]
    assert fila['ventas_por_dia'] == 1.0 and fila['dias_restantes'] == 5.0 and fila['nivel'] == 'critico'
    assert fila['sugerido'] == 25 and fila['costo_estimado'] == 2500          # cubrir 30 dias: 30 - 5


def test_reposicion_ignora_lo_que_alcanza_y_marca_agotados(catalogo, cliente):
    sobrado = catalogo('Sobrado', cantidad=200); vender_hace(cliente, sobrado, 2, 30)
    agotado = catalogo('Agotado', cantidad=0)
    atencion = catalogo('Atencion', cantidad=12); vender_hace(cliente, atencion, 2, 30)   # 12 dias
    por_id = {r['id_producto']: r for r in insights.reposicion()}
    assert sobrado.id_producto not in por_id
    assert por_id[agotado.id_producto]['nivel'] == 'critico'
    assert por_id[atencion.id_producto]['nivel'] == 'atencion'


def test_ventas_anuladas_o_antiguas_no_cuentan_para_el_ritmo(catalogo, cliente):
    p = catalogo('P', cantidad=5)
    vender_hace(cliente, p, 90, 60)                                   # fuera de la ventana de 30 dias
    anulada = vender_hace(cliente, p, 2, 60); anulada.estado = 0; anulada.save()
    assert insights._ritmo_de_ventas().get(p.id_producto) is None


def test_por_vencer(catalogo):
    pronto, lejos, vencido = catalogo('Pronto', 5), catalogo('Lejos', 5), catalogo('Vencido', 5)
    ahora = timezone.now()
    for prod, dias in ((pronto, 20), (lejos, 200), (vencido, -3)):
        prod.fechaven = ahora + timedelta(days=dias); prod.save()
    res = {r['id_producto']: r for r in insights.por_vencer()}
    assert lejos.id_producto not in res
    assert res[pronto.id_producto]['nivel'] == 'critico' and res[vencido.id_producto]['nivel'] == 'vencido'


def test_sin_rotacion_y_capital(catalogo, cliente):
    parado = catalogo('Parado', cantidad=10, precio=1000, precio_pub=1500)
    rota = catalogo('Rota', cantidad=10, precio=1000, precio_pub=1500); vender_hace(cliente, rota, 5, 2)
    ids = [x['id_producto'] for x in insights.sin_rotacion()]
    assert parado.id_producto in ids and rota.id_producto not in ids
    cap = insights.capital()
    assert cap['unidades'] == 20 and cap['costo'] == 20000 and cap['publico'] == 30000 and cap['margen_pct'] == 33.3


def test_marcador_compara_el_mismo_tramo_del_mes_anterior(catalogo, cliente):
    p = catalogo('P')
    def venta(dia_mes, mes, total):
        v = vender_hace(cliente, p, 0, 1, total=total); v.fechareg = date(2026, mes, dia_mes); v.save()
    venta(5, 11, 200); venta(5, 10, 100)
    venta(20, 10, 500)                                              # fuera del tramo 1-15 de octubre: no cuenta
    r = insights.resumen_marcador(hoy=date(2026, 11, 15))
    assert r['ventas']['valor'] == 200 and r['ventas']['previo'] == 100 and r['ventas']['variacion'] == 100.0
    assert len(r['ventas']['serie']) == 14
    assert r['margen_pct'] == 30.0


def test_variacion_sin_mes_previo_es_nula():
    r = insights.resumen_marcador(hoy=date(2026, 11, 15))
    assert r['ventas']['variacion'] is None and r['ventas']['valor'] == 0


def test_endpoints_exigen_sesion(anonimo):
    for nombre in ('obtener_resumen', 'inteligencia_inventario', 'orden_compra_sugerida_pdf', 'buscar_global'):
        assert anonimo.get(reverse(nombre)).status_code == 302, nombre


def test_endpoint_de_inteligencia(admin_client, catalogo, cliente):
    p = catalogo('Critico', cantidad=2); vender_hace(cliente, p, 1, 30)
    data = admin_client.get(reverse('inteligencia_inventario')).json()
    assert data['reposicion'][0]['producto'] == 'Critico' and data['inversion_sugerida'] > 0
    assert {'capital', 'por_vencer', 'sin_rotacion', 'parametros'} <= set(data)
    assert admin_client.get(reverse('obtener_resumen')).json()['ventas']['valor'] >= 0


def test_orden_de_compra_sugerida_pdf(admin_client, catalogo, cliente):
    vacio = admin_client.get(reverse('orden_compra_sugerida_pdf'))
    assert vacio.status_code == 200 and vacio.content.startswith(b'%PDF')
    p = catalogo('Critico', cantidad=1); vender_hace(cliente, p, 1, 30)
    r = admin_client.get(reverse('orden_compra_sugerida_pdf'))
    assert r.status_code == 200 and r.content.startswith(b'%PDF') and len(r.content) > len(vacio.content) - 500


def test_busqueda_global_agrupa_por_modulo_y_respeta_permisos(admin_client, cliente_sin_permisos, catalogo, cliente):
    catalogo('Whey Gold')
    url = reverse('buscar_global')
    assert admin_client.get(url, {'q': 'w'}).json() == {'grupos': []}                 # minimo 2 letras
    grupos = {g['grupo']: g for g in admin_client.get(url, {'q': 'whey'}).json()['grupos']}
    assert grupos['Productos']['items'][0]['label'] == 'Whey Gold' and '/editproduct/' in grupos['Productos']['items'][0]['url']
    clientes = {g['grupo']: g for g in admin_client.get(url, {'q': 'marta'}).json()['grupos']}
    assert clientes['Clientes']['items'][0]['label'] == 'Marta Lopez'
    assert admin_client.get(url, {'q': '900'}).json()['grupos']                       # por documento
    assert cliente_sin_permisos.get(url, {'q': 'whey'}).json() == {'grupos': []}      # sin permisos no ve nada
