import pytest
from django.urls import reverse
from django.test import Client
from django.http import JsonResponse
from eproviders.models import Proveedores

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_lista_proveedores(client):
    url = reverse('proveedores') 
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_creacion_proveedor():
    Proveedores.objects.create(nombre_proveedor="Ejemplo", telefono="1234567890", correo="ejemcorreo.com", direccion="Ejemplo St.", informacion_adicional="Descripción de ejemplo", tipo_documento="Documento", numero_documento_nit="1234567890")
    proveedor = Proveedores.objects.first()
    assert proveedor is not None

@pytest.mark.django_db
def test_editar_proveedor(client):
    proveedor = Proveedores.objects.create(nombre_proveedor="Ejemplo", telefono="1234567890", correo="ejemplo@correo.com", direccion="Ejemplo St.", informacion_adicional="Descripción de ejemplo", tipo_documento="Documento", numero_documento_nit="1234567890")
    url = reverse('editarProveedor', args=[proveedor]) 
    response = client.get(url)
    assert response.status_code == 200