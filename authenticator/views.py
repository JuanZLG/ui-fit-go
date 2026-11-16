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
import secrets
import time
from django.views.decorators.http import require_POST
from .security import verificar, hashear, esta_hasheada, es_valida, REGLA_CONTRASENA


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

            if verificar(contrasena, usuario.contrasena):
                if not esta_hasheada(usuario.contrasena):
                    # Cuenta antigua con contraseña en texto plano: se migra a hash
                    usuario.contrasena = hashear(contrasena)
                    usuario.save(update_fields=['contrasena'])
                payload = custom_jwt_payload_handler(usuario_data)
                payload['id_rol'] = usuario_data['id_rol']
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
        codigo = str(secrets.randbelow(90000) + 10000)
        request.session['correo_almacenado'] = correo
        request.session['codigo_almacenado'] = codigo
        request.session['codigo_emitido'] = time.time()
        request.session['codigo_intentos'] = 0
        request.session['codigo_verificado'] = False
        send_email_codigo(user, correo, codigo)
    return JsonResponse({'existe': existe})

#---------------------------------------------------------------------------------------------------------------
def verificar_codigo(request):
    codigo_ingresado = request.GET.get('codigo') or ''
    codigo_almacenado = request.session.get('codigo_almacenado')
    emitido = request.session.get('codigo_emitido', 0)
    intentos = request.session.get('codigo_intentos', 0)

    # El código caduca a los 10 minutos y permite 5 intentos
    if not codigo_almacenado or time.time() - emitido > 600 or intentos >= 5:
        return JsonResponse({'success': False})

    request.session['codigo_intentos'] = intentos + 1
    if secrets.compare_digest(codigo_ingresado, codigo_almacenado):
        request.session['codigo_verificado'] = True
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
#------------------------------------------------------------------------------------------------------------------


@require_POST
def restablecer_contrasena(request):
    # Solo se puede cambiar la contraseña si el código enviado al correo fue verificado
    if not request.session.get('codigo_verificado'):
        return JsonResponse({'error': 'Primero debes verificar el código enviado a tu correo.'}, status=403)

    nueva_contrasena = request.POST.get('newPassword') or ''
    if not es_valida(nueva_contrasena):
        return JsonResponse({'error': REGLA_CONTRASENA}, status=400)

    correo = request.session.get('correo_almacenado')
    user = Usuarios.objects.filter(correo=correo).first()
    if user is None:
        return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)

    user.contrasena = hashear(nueva_contrasena)
    user.save(update_fields=['contrasena'])

    # El código es de un solo uso
    for clave in ('correo_almacenado', 'codigo_almacenado', 'codigo_emitido', 'codigo_intentos', 'codigo_verificado'):
        request.session.pop(clave, None)
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