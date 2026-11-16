import pytest
from django.urls import reverse

from eproviders.models import Proveedores

pytestmark = pytest.mark.django_db


def crear(**extra):
    datos = dict(nombre_proveedor="Ejemplo", telefono="1234567890", correo="ejemplo@correo.com", direccion="Ejemplo St.",
                 informacion_adicional="Descripción de ejemplo", tipo_documento="Documento", numero_documento_nit="1234567890")
    datos.update(extra)
    return Proveedores.objects.create(**datos)


def test_lista_de_proveedores_exige_sesion(anonimo):
    assert anonimo.get(reverse('proveedores')).status_code == 302


def test_lista_de_proveedores(admin_client):
    crear()
    r = admin_client.get(reverse('proveedores'))
    assert r.status_code == 200 and 'Ejemplo' in r.content.decode()


def test_creacion_de_proveedor():
    assert crear() is not None and Proveedores.objects.count() == 1


def test_editar_proveedor(admin_client):
    proveedor = crear()
    assert admin_client.get(reverse('editarProveedor', args=[proveedor.id_proveedor])).status_code == 200
