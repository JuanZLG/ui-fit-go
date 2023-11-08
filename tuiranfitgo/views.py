from django.shortcuts import render, redirect, get_object_or_404
import jwt
from django.conf import settings
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from products.models import Productos


from django.http import JsonResponse
from .models import Productos

def verificar_notificaciones(request):
    mensaje = []

    productos_pocos = Productos.objects.filter(cantidad__lt=3)
    productos_muchos = Productos.objects.filter(cantidad__gt=12)

    if productos_pocos.exists():
        for producto in productos_pocos:
            mensaje.append(f"Pocos {producto.nombre_producto} en inventario ({producto.cantidad} disponibles).")

    if productos_muchos.exists():
        for producto in productos_muchos:
            mensaje.append(f"Inventario con alta cantidad de {producto.nombre_producto} ({producto.cantidad} disponibles).")

    if mensaje:
        # Si hay mensajes, devuelve solo el primer mensaje (puedes ajustar esto según tus necesidades)
        return JsonResponse({"mensaje": mensaje[0]})
    else:
        # Si no hay mensajes, devuelve un mensaje en blanco
        return JsonResponse({"mensaje": ""})









def error_view(request):  
    return render(request, '404.html') 

def mixin_view(request):  
    return render(request, '401Forbidden.html') 

def jwt_cookie_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('jwt_token') # Esto me lee el token 
        if not token:
            return redirect('initerror')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    
            #Espacio para mas comprobaciones si algo
            request.user = payload
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token JWT caducado'}, status=401)
        except jwt.DecodeError:
            return JsonResponse({'error': 'Token JWT no válido'}, status=401)
            
        return view_func(request, *args, **kwargs)
      

    return _wrapped_view


def logout_view(request):
    response = redirect('login_view') 
    response.delete_cookie('jwt_token')
    return response

from functools import wraps
from django.http import HttpResponseForbidden
from users.models import Rolespermisos
from rest_framework_simplejwt.tokens import Token
import jwt  

def module_access_required(module_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = request.COOKIES.get('jwt_token')

            if token:
                try:
                    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    user_id = decoded_token['id_rol']
                    user_role = user_id

                    if Rolespermisos.objects.filter(id_rol=user_role, **{f'id_permiso__{module_name}': 1}).exists():
                         return view_func(request, *args, **kwargs)
                    else:
                        print("No se encontraron permisos para este usuario en el modulo:", module_name)
                        return redirect('mixint')
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Token no encontrado en las cookies.")

        return _wrapped_view

    return decorator