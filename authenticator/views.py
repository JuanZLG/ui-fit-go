import os
from django.shortcuts import render, redirect
from dotenv import load_dotenv
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
from django.contrib.auth.hashers import make_password
from django.contrib import messages


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
                    'id_rol': usuario_data['id_rol'],
              
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'contrasena incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no Registrado'}, status=status.HTTP_401_UNAUTHORIZED)
        
#-----------------------------------------------------------------------------------------------------
from django.template.loader import get_template
def send_email_codigo(user, email, codigo):
    load_dotenv()
    remitente = os.getenv("USER")
    destinatario = email
    asunto = "Recuperación de cuenta"

    msg = MIMEMultipart()
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    template = get_template("emailCodig.html")
    context = {
        'user': user,
        'codigo': codigo,
        'email': email
    }
    html = template.render(context)

    msg.attach(MIMEText(html, "html"))
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(remitente, os.getenv("PASS"))
    
    server.sendmail(remitente, destinatario, msg.as_string())
    server.quit()

#------------------------------------------------------------------------------------------------------
def verificar_correo(request):
    correo = request.GET.get('correo')
    existe = Usuarios.objects.filter(correo=correo).exists()
    if existe:
        user = Usuarios.objects.filter(correo=correo).first()
        user = user.nombre_usuario
        codigo = str(random.randint(10000, 99999))
        request.session['correo_almacenado'] = correo  
        request.session['codigo_almacenado'] = codigo  
        send_email_codigo(user, correo, codigo)
    return JsonResponse({'existe': existe})

#---------------------------------------------------------------------------------------------------------------
def verificar_codigo(request):
    codigo_ingresado = request.GET.get('codigo')
    codigo_almacenado = request.session.get('codigo_almacenado') 
    if codigo_ingresado == codigo_almacenado:
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})
#------------------------------------------------------------------------------------------------------------------


def restablecer_contrasena(request):
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('newPassword')
        correo = request.session.get('correo_almacenado') 

        user = Usuarios.objects.get(correo=correo)
        user.contrasena = nueva_contrasena
        user.save()
    return redirect('login_view')









            







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