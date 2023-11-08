from django.shortcuts import render, redirect
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
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.auth import get_user_model
import re
from django.core.exceptions import ObjectDoesNotExist


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

# def custom_get_username(user):
#     return user.correo

# Login Bueno 

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

            if usuario.estado == 0:
                return JsonResponse({'error': 'Usuario inactivo'}, status=401)

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
                return Response({'error': 'contrasena incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no Registrado'}, status=status.HTTP_401_UNAUTHORIZED)
        
#-----------------------------------------------------------------------------------------------------
def send_email_codigo(correo, codigo):
    remitente = 'danielperezbedoya382@gmail.com'
    destinatario = correo
    asunto = 'Código de Recuperación de Contraseña'

    msg = MIMEMultipart()
    msg['Subject'] = asunto
    msg['From'] = remitente 
    msg['To'] = destinatario

    mensaje = f'Tu código de recuperación es: {codigo}'

    msg.attach(MIMEText(mensaje, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(remitente, '') 

    # Envía el correo
    server.sendmail(remitente, destinatario, msg.as_string())
    server.quit()

#------------------------------------------------------------------------------------------------------
def olvide_contrasena(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        if validar_correo(correo):
            codigo = str(random.randint(10000, 99999))

            send_email_codigo(correo, codigo)
            request.session['codigo_recuperacion'] = codigo
            return redirect('verificar_codigo')

    return render(request, 'olvide_contrasena.html')

#------------------------------------------------------------------------------------------------------
def validar_correo(correo):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, correo) is not None

#------------------------------------------------------------------------------------------------------
def enviar_codigo(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        if validar_correo(correo):
            try:
                user = Usuarios.objects.get(correo=correo)
                codigo = str(random.randint(10000, 99999))
                send_email_codigo(correo, codigo)
                request.session['codigo_recuperacion'] = codigo
                request.session['correo_recuperacion'] = correo 
                return redirect('verificar_codigo')
            except ObjectDoesNotExist:
                return render(request, 'enviar_codigo.html', {'error': 'El correo no existe'})
    return render(request, 'enviar_codigo.html')
#---------------------------------------------------------------------------------------------------------------
def verificar_codigo(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        codigo_almacenado = request.session.get('codigo_recuperacion')
        if codigo_ingresado == codigo_almacenado:
            return redirect('restablecer_contrasena')
        else:
            return render(request, 'verificar_codigo.html', {'error': True})
    return render(request, 'verificar_codigo.html')


#------------------------------------------------------------------------------------------------------------------
def restablecer_contrasena(request):
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')

        correo = request.session.get('correo_recuperacion')

        if correo and nueva_contrasena == confirmar_contrasena:
            if validar_correo(correo):
                User = get_user_model()
                try:
                    user = User.objects.get(email=correo)
                    user.set_password(nueva_contrasena)
                    user.save()
                    return redirect('login_view')
                except User.DoesNotExist:
                    return render(request, 'restablecer_contrasena.html', {'error': True})
            else:
                return render(request, 'restablecer_contrasena.html', {'error': True})
        else:
            return render(request, 'restablecer_contrasena.html', {'error': True})

    return render(request, 'restablecer_contrasena.html')


            







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