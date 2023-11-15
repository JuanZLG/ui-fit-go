
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
import json
from urllib.parse import parse_qs
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from users.models import Roles, Permisos, Usuarios, Rolespermisos
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from dotenv import load_dotenv
import smtplib 
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string
import secrets
from django.template.loader import get_template
from tuiranfitgo.views import jwt_cookie_required, module_access_required
from base64 import urlsafe_b64decode as atob


@jwt_cookie_required
@module_access_required('usuarios')
def Home(request):
    usuarios = Usuarios.objects.all()

    for u in usuarios:
        u.permiso_ver_detalles = u.id_rol_id is not None and u.estado == 1
        u.habilitar_cambio_estado = u.id_rol_id is not None

    context = {
        'Usuarios': usuarios,
    }

    return render(request, 'usersHome.html', context)

import base64
import json

@jwt_cookie_required
def UserProfile(request):
    # Obtener el token desde la cookie
    token = request.COOKIES.get('jwt_token')

    # Decodificar manualmente el token para obtener el payload
    if token:
        try:
            payload = json.loads(base64.b64decode(token.split('.')[1] + '==').decode('utf-8'))
            id_rol = payload.get('id_rol')

            # Obtener el nombre del rol desde la base de datos
            try:
                rol = Roles.objects.get(id_rol=id_rol)
                nombre_rol = rol.nombre_rol
            except Roles.DoesNotExist:
                nombre_rol = "Rol no encontrado"  # Puedes manejar esto de la manera que prefieras

            # Pasar el nombre del rol a la plantilla
            return render(request, 'profile.html', {'nombre_rol': nombre_rol})
        except Exception as e:
            # Manejar cualquier error de decodificación del token
            print(f"Error decodificando el token: {e}")

    # Manejar el caso en que no haya token o se produzca un error
    return render(request, 'profile.html', {'nombre_rol': "Rol no disponible"})


# @jwt_cookie_required
# @module_access_required('usuarios')
def cambiarEstadoDeUsuario(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_usuario = request.GET.get('usuario_id')
        nuevo_estado = request.GET.get('nuevo_estado')
        try:
            usuario = Usuarios.objects.get(id_usuario=id_usuario)
            usuario.estado = int(nuevo_estado)
            usuario.save()
            return JsonResponse({'status': 'success'})
        except Usuarios.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Usuario no Encontrado.'})
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})


# @jwt_cookie_required
# @module_access_required('usuarios')
def verDetallesUsuario(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_usuario = request.GET.get('usuario_id')
        
        if id_usuario:
            try:
                usuario = Usuarios.objects.get(id_usuario=id_usuario)
                rolespermisos = Rolespermisos.objects.get(id_rol=usuario.id_rol)

                permisos = rolespermisos.id_permiso

                data = {
                    'Rol': usuario.id_rol.nombre_rol,
                    'Nombre de Usuario': usuario.nombre_usuario,
                    'documento': usuario.correo,
                    'Estado': usuario.estado,
                    'Permisos': {
                        'Clientes': permisos.clientes,
                        'Usuarios': permisos.usuarios,
                        'Proveedores': permisos.proveedores,
                        'Productos': permisos.productos,
                        'Compras': permisos.compras,
                        'Ventas': permisos.ventas,
                    }
                }
                return JsonResponse({'success': data})
            except Usuarios.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de Usuario no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})


@jwt_cookie_required
@module_access_required('usuarios')
def createUser(request):
    roles = Roles.objects.all()
    
    if request.method == 'POST':
        id_rol = request.POST['iRole']
        nombre_usuario = request.POST['iNombre']
        correo = request.POST['iCorreo']
        contrasena = create_password()
        rl = Roles.objects.get(id_rol=id_rol)
        Usuarios.objects.create(id_rol=rl, nombre_usuario=nombre_usuario, correo=correo, contrasena=contrasena)
        send_email(nombre_usuario, contrasena, correo)

        return JsonResponse({'success': True})

    return render(request, 'createUser.html', {"rols": roles})

# @jwt_cookie_required
# @module_access_required('usuarios')
def send_email(user, password, email):
    load_dotenv()
    remitente = os.getenv("USER")
    destinatario = email
    asunto = "Bienvenido a TuiranFit"

    msg = MIMEMultipart()
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    template = get_template("email.html")
    context = {
        'user': user,
        'password': password,
        'email': email
    }
    html = template.render(context)

    msg.attach(MIMEText(html, "html"))
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(remitente, os.getenv("PASS"))
    
    server.sendmail(remitente, destinatario, msg.as_string())
    server.quit()

# @jwt_cookie_required
# @module_access_required('usuarios')
def create_password(length=8):
    characters = string.ascii_letters + string.digits
    password = ""
    for _ in range(length):
        password += secrets.choice(characters)
    return password


@jwt_cookie_required
@module_access_required('usuarios')
def editUser(request, id_usuario):
    roles = Roles.objects.all()
    
    if request.method == 'POST':
        role = request.POST['iRole']
        nombre_usuario = request.POST['iNombre']
        correo = request.POST['iCorreo']
        contrasena = request.POST['iPassword']
        
        rl = Roles.objects.get(id_rol=role)
        
        Usuarios.objects.filter(id_usuario=id_usuario).update(
            id_rol=rl,
            nombre_usuario=nombre_usuario,
            correo=correo,
            contrasena=contrasena,
        )
        
        response_data = {'success': True}
        return JsonResponse(response_data)    
    users = Usuarios.objects.get(id_usuario=id_usuario)
    return render(request, 'editUser.html', {"people":users, "rols":roles}) 

@jwt_cookie_required
@module_access_required('usuarios')
def HomeRoles(request):
    rolPermisos = Rolespermisos.objects.all()
    permisos_count = {}
    for rp in rolPermisos:
        rol = rp.id_rol
        permisos = sum([
            rp.id_permiso.clientes,
            rp.id_permiso.usuarios,
            rp.id_permiso.proveedores,
            rp.id_permiso.productos,
            rp.id_permiso.compras,
            rp.id_permiso.ventas,
        ])
        
        if rol in permisos_count:
            permisos_count[rol] += permisos
        else:
            permisos_count[rol] = permisos
        
    return render(request, 'rolesHome.html', {"permisos_count": permisos_count})

@jwt_cookie_required
# @module_access_required('usuarios')
def accion_rol(request):
    data = json.loads(request.body)
    if request.method == 'POST':
        if data.get("accion") == "create":
            nombre_rol = data.get("nombreRol")
            permisos = data.get("permisos")

            rol = Roles(nombre_rol=nombre_rol)
            rol.save()

            permiso = Permisos(
                clientes=permisos.get("Clientes", 0),
                usuarios=permisos.get("Usuarios", 0),
                proveedores=permisos.get("Proveedores", 0),
                productos=permisos.get("Productos", 0),
                compras=permisos.get("Compras", 0),
                ventas=permisos.get("Ventas", 0)
            )
            permiso.save()

            roles_permisos = Rolespermisos(
                id_rol=rol,
                id_permiso=permiso
            )
            roles_permisos.save()


        elif data.get("accion") == "edit":
            id_rol = data.get("id_rol")
            nombreRol = data.get("nombreRol")
            permisos = data.get("permisos")

            try:
                rol = Roles.objects.get(id_rol=id_rol)
                rol.nombre_rol = nombreRol
                rol.save()
                print(rol.id_rol)

                permiso = Rolespermisos.objects.get(id_rol=rol.id_rol)
                permiso.id_permiso.clientes = permisos.get("Clientes", 0)
                permiso.id_permiso.usuarios = permisos.get("Usuarios", 0)
                permiso.id_permiso.proveedores = permisos.get("Proveedores", 0)
                permiso.id_permiso.productos = permisos.get("Productos", 0)
                permiso.id_permiso.compras = permisos.get("Compras", 0)
                permiso.id_permiso.ventas = permisos.get("Ventas", 0)
                permiso.id_permiso.save()
            except Roles.DoesNotExist:
                print("Excepción: El rol no existe.")
                return JsonResponse({"success": False, "message": "El rol no existe."})
    
    response_data = {"success": True}
    return JsonResponse(response_data)

def email_unique(request):
    email = request.GET.get("email", "")
    email_existe = Usuarios.objects.filter(correo=email).exists()
    return JsonResponse({"existe": email_existe})


@jwt_cookie_required
# @module_access_required('usuarios')
def obtener_datos(request):
        id_rol = request.GET.get('param')
        rolespermisos = Rolespermisos.objects.get(id_rol=id_rol)
        datos = {
            'nombre_rol': rolespermisos.id_rol.nombre_rol,
            'permisos': {
                'Clientes': rolespermisos.id_permiso.clientes,
                'Proveedores': rolespermisos.id_permiso.proveedores,
                'Productos': rolespermisos.id_permiso.productos,
                'Ventas': rolespermisos.id_permiso.ventas,
                'Compras': rolespermisos.id_permiso.compras,
                'Usuarios': rolespermisos.id_permiso.usuarios,
            }
        }
        return JsonResponse({'success': True, 'datos': datos})

@jwt_cookie_required
@module_access_required('usuarios')
def rol_unico(request):
    nombre_rol = request.GET.get("nombre_rol", "")
    rol_existe = Roles.objects.filter(nombre_rol=nombre_rol).exists()
    print(rol_existe)
    return JsonResponse({"existe": rol_existe})


@jwt_cookie_required
# @module_access_required('usuarios')
def eliminar_rol(request):
    id_rol = request.GET.get('idrol')
    
    try:
        rol = Roles.objects.get(id_rol=id_rol)
        
        usuario = Usuarios.objects.filter(id_rol=rol).first()
        if usuario:
            usuario.id_rol = None 
            usuario.estado = 0
            usuario.save()
        
        roles_permisos = Rolespermisos.objects.filter(id_rol=rol).first()
        if roles_permisos:
            permiso = roles_permisos.id_permiso
            permiso.delete()
            
            roles_permisos.delete()
        
        rol.delete()
        
        return JsonResponse({'message': 'Rol, permiso y estado de usuario eliminados con éxito'})
    
    except Roles.DoesNotExist:
        return JsonResponse({'error': 'El rol no existe'})