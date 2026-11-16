from functools import wraps

import jwt
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect

from products.models import Productos
from users.models import Rolespermisos

STOCK_BAJO = 5       # a partir de aquí (incluido 0) se avisa de stock mínimo
STOCK_ALTO = 13      # por encima de esto se avisa de exceso


def _token_payload(request):
    """Devuelve el payload del JWT de la cookie, o None si falta o no es válido."""
    token = request.COOKIES.get('jwt_token')
    if not token:
        return None
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None


def verificar_notificaciones(request):
    payload = _token_payload(request)
    if payload is None:
        return JsonResponse({"mensajes": [], "cantidad": 0}, status=401)

    if payload.get('id_rol') != 1:
        mensajes = [{"tipo": "info", "mensaje": "Las notificaciones solo están disponibles para el administrador."}]
        return JsonResponse({"mensajes": mensajes, "cantidad": len(mensajes)})

    activos = Productos.objects.filter(estado=1)
    mensajes = []
    for producto in activos.filter(cantidad__lte=STOCK_BAJO).order_by('cantidad'):
        mensajes.append({
            "tipo": "advertencia",
            "mensaje": f"{producto.nombre_producto}: ({max(producto.cantidad, 0)} disponibles).",
        })
    for producto in activos.filter(cantidad__gt=STOCK_ALTO).order_by('-cantidad'):
        mensajes.append({
            "tipo": "exceso",
            "mensaje": f"{producto.nombre_producto}: ({producto.cantidad} disponibles).",
        })

    cantidad_mensajes = len(mensajes)
    anterior = request.session.get('cantidadMensajes', 0)
    request.session['cantidadMensajes'] = cantidad_mensajes

    return JsonResponse({
        "mensajes": mensajes,
        "cantidad": cantidad_mensajes,
        "nuevosMensajes": cantidad_mensajes > anterior,
    })


def error_view(request):
    return render(request, '404.html')


def mixin_view(request):
    return render(request, '401Forbidden.html')


def jwt_cookie_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('jwt_token')
        if not token:
            return redirect('initerror')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token JWT caducado'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token JWT no válido'}, status=401)

        request.user = payload
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def logout_view(request):
    response = redirect('login_view')
    response.delete_cookie('jwt_token')
    return response


def module_access_required(module_name):
    """Exige que el rol del usuario tenga permiso sobre ``module_name``."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            payload = _token_payload(request)
            if payload is None:
                return redirect('initerror')

            tiene_permiso = Rolespermisos.objects.filter(
                id_rol=payload.get('id_rol'), **{f'id_permiso__{module_name}': 1}
            ).exists()
            if not tiene_permiso:
                return redirect('mixint')
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
