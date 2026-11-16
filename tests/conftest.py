import jwt
import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import Client

from authenticator.security import hashear
from products.models import Categorias, Marcas, Productos
from users.models import Permisos, Roles, Rolespermisos, Usuarios


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Los modelos del proyecto son managed=False: se crean sus tablas para las pruebas."""
    with django_db_blocker.unblock():
        call_command('create_dev_tables')


@pytest.fixture(autouse=True)
def sin_correos(monkeypatch):
    """Ninguna prueba envía correos reales (Gmail/SMTP)."""
    enviados = []
    monkeypatch.setattr('sales.views.pedido_email_confirmacion', lambda *a, **k: enviados.append(a))
    monkeypatch.setattr('page.views.pedido_email_proceso', lambda *a, **k: enviados.append(a))
    monkeypatch.setattr('authenticator.views.send_email_codigo', lambda *a, **k: enviados.append(a))
    return enviados


def _cliente_con_rol(id_rol, permisos):
    token = jwt.encode({'id_rol': id_rol, 'nombre_usuario': 'Tester', 'correo': 'tester@tuiranfit.test'},
                       settings.SECRET_KEY, algorithm='HS256')
    c = Client()
    c.cookies['jwt_token'] = token if isinstance(token, str) else token.decode()
    return c


@pytest.fixture
def admin_client(db):
    """Cliente autenticado con un rol que tiene permiso sobre todos los módulos."""
    rol = Roles.objects.create(nombre_rol='Administrador')
    permiso = Permisos.objects.create(clientes=1, usuarios=1, proveedores=1, productos=1, compras=1, ventas=1)
    Rolespermisos.objects.create(id_rol=rol, id_permiso=permiso)
    Usuarios.objects.create(id_rol=rol, correo='tester@tuiranfit.test', nombre_usuario='Tester',
                            contrasena=hashear('Secreta123'), estado=1)
    return _cliente_con_rol(rol.id_rol, permiso)


@pytest.fixture
def cliente_sin_permisos(db):
    """Autenticado, pero su rol no tiene ningún permiso."""
    rol = Roles.objects.create(nombre_rol='Invitado')
    permiso = Permisos.objects.create(clientes=0, usuarios=0, proveedores=0, productos=0, compras=0, ventas=0)
    Rolespermisos.objects.create(id_rol=rol, id_permiso=permiso)
    return _cliente_con_rol(rol.id_rol, permiso)


@pytest.fixture
def anonimo():
    return Client()


@pytest.fixture
def catalogo(db):
    categoria = Categorias.objects.create(nombre_categoria='Proteinas')
    marca = Marcas.objects.create(nombre_marca='Marca X')

    def crear(nombre='Whey', cantidad=10, estado=1, precio=100.0, precio_pub=150.0, sabor='Chocolate,Vainilla'):
        return Productos.objects.create(
            id_categoria=categoria, id_marca=marca, nombre_producto=nombre, descripcion='desc',
            cantidad=cantidad, fechaven='2030-01-01 00:00:00', sabor=sabor, presentacion='1 lb',
            estado=estado, precio=precio, precio_pub=precio_pub,
        )
    return crear
