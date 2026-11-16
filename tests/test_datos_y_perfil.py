"""Datos de Colombia empaquetados localmente y perfil de usuario."""
import json
from pathlib import Path

import pytest
from django.conf import settings
from django.urls import reverse

RUTA = Path(settings.BASE_DIR) / 'tuiranfitgo' / 'static' / 'data' / 'colombia.json'


def test_departamentos_y_municipios_estan_completos():
    datos = json.loads(RUTA.read_text(encoding='utf-8'))['departamentos']
    assert len(datos) == 33                                  # 32 departamentos + Bogotá D.C.
    assert sum(len(d['municipios']) for d in datos) >= 1100
    por_nombre = {d['nombre']: d['municipios'] for d in datos}
    assert 'Medellín' in por_nombre['Antioquia'] and 'Cali' in por_nombre['Valle del Cauca']
    assert por_nombre['Bogotá D.C.'] == ['Bogotá D.C.']
    for d in datos:
        assert d['municipios'] == sorted(set(d['municipios']), key=lambda s: s.lower()) or len(set(d['municipios'])) == len(d['municipios'])


def test_el_archivo_se_sirve_como_estatico(anonimo, settings):
    from django.contrib.staticfiles import finders
    assert finders.find('data/colombia.json')
    assert finders.find('js/colombia.js') and finders.find('css/colombia.css')


@pytest.mark.django_db
def test_perfil_muestra_el_nombre_del_rol_no_su_numero(admin_client):
    html = admin_client.get(reverse('myProfile')).content.decode()
    assert 'Administrador' in html
    assert 'payload.id_rol' not in html            # ya no se sobrescribe con el número del token
