from django.shortcuts import render, redirect, get_object_or_404
import jwt
from django.conf import settings
from django.http import JsonResponse

def error_view(request):  
    return render(request, '404.html') 

def jwt_cookie_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('jwt_token')  # Esto me lee el token 
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