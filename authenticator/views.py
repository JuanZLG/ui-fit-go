from django.shortcuts import render
from authenticator.models import Usuarios
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from .models import Usuarios
from django.core import serializers
import json
from .utils import custom_jwt_payload_handler
from authenticator.models import Usuarios
from django.core.mail import send_mail
from django.template.loader import get_template
from django.http import HttpResponse
from django.core.exceptions import MultipleObjectsReturned

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


from rest_framework.response import Response
from rest_framework import status

class loginmio(APIView):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        correo = request.data.get('correo')
        contrasena = request.data.get('contra')
        try:
            usuario = Usuarios.objects.get(correo=correo)
            usuario_data = serializers.serialize('python', [usuario])[0]['fields']

            if usuario.contrasena == contrasena:
                payload = custom_jwt_payload_handler(usuario_data)
                payload['id_rol'] = usuario_data['id_rol']

                print(usuario_data)
                print("payload:", payload)
                token = jwt_encode_handler(payload)
                response_data = {
                    'token': token,
                    'nombre_usuario': usuario_data['nombre_usuario'],
                    'id_rol': usuario_data['id_rol']
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no Registrado'}, status=status.HTTP_401_UNAUTHORIZED)
        

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

def olvide_contrasena(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        try:
            usuario = Usuarios.objects.get(correo=correo)

            reset_link = "http://tu-sitio.com/restablecer-contrasena/" + usuario.correo + "/token/"
            send_mail(
                'Recuperar Contraseña',
                f'Para restablecer tu contraseña, haz clic en este enlace: {reset_link}',
                'noreply@tu-sitio.com',
                [correo],
                fail_silently=False,
            )
            return render(request, 'olvide_contrasena_exito.html', {'correo': correo})

        except ObjectDoesNotExist:
            error_message = 'El correo no existe'
            return render(request, 'olvide_contrasena.html', {'error_message': error_message, 'correo': correo})

        except MultipleObjectsReturned:
            error_message = 'Se encontraron múltiples usuarios con el mismo correo'
            return render(request, 'olvide_contrasena.html', {'error_message': error_message, 'correo': correo})

    return render(request, 'olvide_contrasena.html')


def olvide_contrasena_exito(request):
    return render(request, 'olvide_contrasena_exito.html')

#Login Malo
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth import get_user_model

# @csrf_exempt
# def custom_login(request):
#     if request.method == 'POST':
#         email = request.POST.get('correo')
#         password = request.POST.get('contra')

#         user = get_user_model().objects.filter(correo=email).first()

#         if user and user.check_password(password):
#             # Iniciar una sesión para el usuario
#             request.session['user_id'] = user.id_usuario
#             request.session.save()
#             return JsonResponse({'message': 'Inicio de sesión exitoso'})
#         else:
#             return JsonResponse({'message': 'Credenciales incorrectas'}, status=401)
    
#     return render(request, 'login.html')


# def verificar_permiso(usuario, permiso):
#     try:
        
#         rol = usuario.id_rol

#         if Rolespermisos.objects.filter(id_rol=rol, id_permiso__clientes=permiso).exists():
#             return True
#         else:
#             return False
#     except Roles.DoesNotExist:
#         return False

# def cerrar_sesion(request):
#     logout(request)
#     return redirect('login_view')

# def vista_con_permiso(request):
#     if verificar_permiso(request.user, 'clientes'):
#         # Este es el ejemplo para bloquear vistas después
#     else:
#         return HttpResponseForbidden("No tiene permiso para acceder a esta vista.")