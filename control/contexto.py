"""Usuario de la petición en curso (para saber quién hizo cada cambio sin pasar `request` a todos lados)."""
import threading

import jwt
from django.conf import settings

_local = threading.local()


def fijar(**datos):
    _local.datos = datos


def obtener():
    return getattr(_local, 'datos', None) or {}


def limpiar():
    _local.datos = {}


def _ip(request):
    adelante = request.META.get('HTTP_X_FORWARDED_FOR')
    return (adelante.split(',')[0].strip() if adelante else request.META.get('REMOTE_ADDR', ''))[:45]


class ContextoMiddleware:
    """Lee el JWT de la cookie (si hay uno válido) y deja disponible quién es el usuario."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        payload = {}
        token = request.COOKIES.get('jwt_token')
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.InvalidTokenError:
                payload = {}
        fijar(usuario_nombre=payload.get('nombre_usuario', ''), usuario_correo=payload.get('correo', ''),
              rol_id=payload.get('id_rol'), ip=_ip(request))
        try:
            return self.get_response(request)
        finally:
            limpiar()
