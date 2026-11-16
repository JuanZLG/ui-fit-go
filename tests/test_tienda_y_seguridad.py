"""Tienda pública (pedidos de clientes) y seguridad de cuentas."""
import json

import jwt
import pytest
from django.conf import settings
from django.urls import reverse

from authenticator.security import esta_hasheada, hashear, verificar
from customers.models import Clientes, Departamentos, Municipios
from orders.models import DetallePedido, Pedidos
from users.models import Roles, Usuarios

pytestmark = pytest.mark.django_db


# ------------------------------------------------------------------ pedidos de la tienda
def formulario(carrito, **extra):
    base = {'documento': '555', 'nombre': 'Luis', 'apellido': 'Mora', 'celular': '3001112222',
            'correo': 'luis@test.co', 'departamento': 'Antioquia', 'municipio': 'Medellin',
            'barrio': 'Centro', 'direccion': 'Calle 1', 'carrito': json.dumps(carrito)}
    base.update(extra)
    return base


def linea(p, cantidad=1, precio='$1', sabor='Chocolate'):
    return {'idDelProducto': p.id_producto, 'cantidad': cantidad, 'precio': precio, 'sabor': sabor}


def test_pedido_usa_el_precio_de_la_base_de_datos(anonimo, catalogo):
    p = catalogo(cantidad=10, precio_pub=150)
    r = anonimo.post(reverse('pageOrder'), formulario({'a': linea(p, 2, precio='$1')}))
    assert r.status_code == 200
    ped = Pedidos.objects.get()
    det = DetallePedido.objects.get()
    assert (det.precio_uni, det.precio_tot, ped.total_pedido) == (150, 300, 300)      # el "$1" del navegador se ignora


def test_pedido_no_supera_el_stock_ni_acepta_cantidades_raras(anonimo, catalogo):
    p = catalogo(cantidad=3)
    for cantidad in (4, 0, -1, 'x', 1000):
        r = anonimo.post(reverse('pageOrder'), formulario({'a': linea(p, cantidad)}))
        assert r.status_code == 400, cantidad
    assert Pedidos.objects.count() == 0 and Clientes.objects.count() == 0     # nada quedó a medias


def test_stock_se_suma_por_producto_entre_lineas(anonimo, catalogo):
    p = catalogo(cantidad=3)
    carrito = {'a': linea(p, 2, sabor='Chocolate'), 'b': linea(p, 2, sabor='Vainilla')}
    assert anonimo.post(reverse('pageOrder'), formulario(carrito)).status_code == 400


def test_pedido_vacio_producto_inactivo_sabor_y_correo_invalidos(anonimo, catalogo):
    p, inactivo = catalogo('A', cantidad=5), catalogo('B', cantidad=5, estado=0)
    assert anonimo.post(reverse('pageOrder'), formulario({})).status_code == 400
    assert anonimo.post(reverse('pageOrder'), formulario({'a': linea(inactivo)})).status_code == 400
    assert anonimo.post(reverse('pageOrder'), formulario({'a': linea(p, sabor='Inventado')})).status_code == 400
    assert anonimo.post(reverse('pageOrder'), formulario({'a': linea(p)}, correo='no-es-correo')).status_code == 400
    assert Pedidos.objects.count() == 0


def test_pedido_no_descuenta_inventario_hasta_confirmar_la_venta(anonimo, catalogo):
    p = catalogo(cantidad=5)
    assert anonimo.post(reverse('pageOrder'), formulario({'a': linea(p, 2)})).status_code == 200
    p.refresh_from_db(); assert p.cantidad == 5


def test_cliente_existente_no_se_sobrescribe_ni_se_renombra_su_ubicacion(anonimo, catalogo):
    p = catalogo(cantidad=5)
    depto = Departamentos.objects.create(nombre_departamento='Cundinamarca')
    muni = Municipios.objects.create(id_departamento=depto, nombre_municipio='Bogota')
    c = Clientes.objects.create(id_municipio=muni, documento='555', nombres='Original', apellidos='Dueno', celular='111',
                                barrio='B', direccion='Dir real', estado=True, correo='real@test.co')
    r = anonimo.post(reverse('pageOrder'), formulario({'a': linea(p)}, nombre='Hacker', departamento='Otro', municipio='Otro'))
    assert r.status_code == 200
    c.refresh_from_db(); depto.refresh_from_db(); muni.refresh_from_db()
    assert (c.nombres, c.celular, c.direccion, c.correo) == ('Original', '111', 'Dir real', 'real@test.co')
    assert (depto.nombre_departamento, muni.nombre_municipio) == ('Cundinamarca', 'Bogota')
    assert Pedidos.objects.get().id_cliente_id == c.id_cliente


def test_cliente_inactivo_no_puede_pedir(anonimo, catalogo):
    p = catalogo(cantidad=5)
    depto = Departamentos.objects.create(nombre_departamento='D')
    muni = Municipios.objects.create(id_departamento=depto, nombre_municipio='M')
    Clientes.objects.create(id_municipio=muni, documento='555', nombres='X', apellidos='Y', celular='1', barrio='b',
                            direccion='d', estado=False)
    assert anonimo.post(reverse('pageOrder'), formulario({'a': linea(p)})).status_code == 400


def test_consulta_publica_de_cliente_no_filtra_datos_privados(anonimo):
    depto = Departamentos.objects.create(nombre_departamento='D')
    muni = Municipios.objects.create(id_departamento=depto, nombre_municipio='M')
    Clientes.objects.create(id_municipio=muni, documento='555', nombres='Ana', apellidos='Y', celular='3009998888',
                            barrio='Secreto', direccion='Calle privada', estado=True, correo='ana@privado.co')
    data = anonimo.get(reverse('obtener_cliente'), {'documento': '555'}).json()['success']
    assert set(data) == {'estado', 'nombres', 'apellidos', 'municipio', 'departamento'}


def test_tienda_solo_lista_productos_con_stock(anonimo, catalogo):
    catalogo('Hay', cantidad=1)           # 1 unidad todavía se puede vender
    catalogo('Agotado', cantidad=0)
    html = anonimo.get(reverse('pageHome')).content.decode()
    assert 'Hay' in html and 'Agotado' not in html
    assert anonimo.get(reverse('mas_vendidos')).status_code == 200


# ------------------------------------------------------------------ cuentas y contraseñas
def login(client, correo, contra):
    return client.post(reverse('login_view'), json.dumps({'correo': correo, 'contra': contra}), content_type='application/json')


@pytest.fixture
def usuario(db):
    rol = Roles.objects.create(nombre_rol='Admin')
    return Usuarios.objects.create(id_rol=rol, correo='u@test.co', nombre_usuario='U', contrasena=hashear('Clave1234'), estado=1)


def test_login_con_hash_y_sin_contrasena_en_el_token(anonimo, usuario):
    r = login(anonimo, 'u@test.co', 'Clave1234')
    assert r.status_code == 200
    payload = jwt.decode(r.json()['token'], settings.SECRET_KEY, algorithms=['HS256'])
    assert 'contrasena' not in payload and 'Clave1234' not in json.dumps(payload)
    assert login(anonimo, 'u@test.co', 'incorrecta').status_code == 401


def test_cuenta_antigua_en_texto_plano_se_migra_a_hash(anonimo, usuario):
    usuario.contrasena = 'Vieja1234'; usuario.save()
    assert login(anonimo, 'u@test.co', 'Vieja1234').status_code == 200
    usuario.refresh_from_db()
    assert esta_hasheada(usuario.contrasena) and verificar('Vieja1234', usuario.contrasena)
    assert len(usuario.contrasena) <= 64                    # cabe en la columna original
    assert login(anonimo, 'u@test.co', 'Vieja1234').status_code == 200


def test_usuario_inactivo_no_entra(anonimo, usuario):
    usuario.estado = 0; usuario.save()
    assert login(anonimo, 'u@test.co', 'Clave1234').status_code == 401


def test_no_se_puede_restablecer_sin_verificar_el_codigo(anonimo, usuario):
    anonimo.get(reverse('verificar_correo'), {'correo': 'u@test.co'})          # solo pide el código
    r = anonimo.post(reverse('restablecer_contrasena'), {'newPassword': 'Hackeada123'})
    assert r.status_code == 403
    usuario.refresh_from_db(); assert verificar('Clave1234', usuario.contrasena)


def test_restablecer_con_codigo_correcto_guarda_hash_y_es_de_un_solo_uso(anonimo, usuario):
    anonimo.get(reverse('verificar_correo'), {'correo': 'u@test.co'})
    codigo = anonimo.session['codigo_almacenado']
    assert anonimo.get(reverse('verificar_codigo'), {'codigo': codigo}).json()['success'] is True
    assert anonimo.post(reverse('restablecer_contrasena'), {'newPassword': 'debil'}).status_code == 400     # sin mayúscula/número
    assert anonimo.post(reverse('restablecer_contrasena'), {'newPassword': 'Nueva1234'}).status_code == 302
    usuario.refresh_from_db()
    assert esta_hasheada(usuario.contrasena) and verificar('Nueva1234', usuario.contrasena)
    assert anonimo.post(reverse('restablecer_contrasena'), {'newPassword': 'Otra12345'}).status_code == 403


def test_codigo_se_bloquea_tras_cinco_intentos(anonimo, usuario):
    anonimo.get(reverse('verificar_correo'), {'correo': 'u@test.co'})
    codigo = anonimo.session['codigo_almacenado']
    for _ in range(5):
        assert anonimo.get(reverse('verificar_codigo'), {'codigo': '00000'}).json()['success'] is False
    assert anonimo.get(reverse('verificar_codigo'), {'codigo': codigo}).json()['success'] is False


def test_notificaciones_requieren_sesion_y_avisan_stock_cero(anonimo, admin_client, catalogo):
    assert anonimo.get(reverse('verificar_notificaciones')).status_code == 401
    catalogo('Poco', cantidad=2); catalogo('Cero', cantidad=0); catalogo('Normal', cantidad=8)
    nombres = ' '.join(m['mensaje'] for m in admin_client.get(reverse('verificar_notificaciones')).json()['mensajes'])
    assert 'Poco' in nombres and 'Cero' in nombres and 'Normal' not in nombres


def test_modulo_sin_permiso_redirige(cliente_sin_permisos, admin_client):
    assert cliente_sin_permisos.get(reverse('ventas')).status_code == 302
    assert admin_client.get(reverse('ventas')).status_code == 200


def test_jwt_manipulado_o_ausente_no_entra(anonimo):
    assert anonimo.get(reverse('ventas')).status_code == 302
    anonimo.cookies['jwt_token'] = jwt.encode({'id_rol': 1}, 'otra-clave', algorithm='HS256')
    assert anonimo.get(reverse('ventas')).status_code == 401
