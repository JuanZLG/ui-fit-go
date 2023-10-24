
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
import json
from urllib.parse import parse_qs
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from users.models import Roles, Permisos, Usuarios, Rolespermisos
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages

# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         try:
#             # Validar las credenciales del usuario
#             usuario = Usuarios.objects.get(correo=username, contrasena=password)
#             # Iniciar sesión manualmente
#             request.session['usuario_id'] = usuario.id_usuario
#             return redirect('Entrance')
#         except Usuarios.DoesNotExist:
#             # Las credenciales son incorrectas
#             messages.error(request, 'Credenciales incorrectas.')

#     return render(request, 'login.html')

# Nuevo....

# class LoginView(View):
#     def get(self, request):
#         # Render the login form
#         return render(request, 'login.html')

#     def post(self, request):
#         correo = request.POST['correo']
#         contrasena = request.POST['contrasena']
#         user = authenticate(request, correo=correo, password=contrasena)
#         if user is not None:
#             login(request, user)
#             return redirect(reverse_lazy('home'))  # Redirect to the desired URL after login
#         else:
#             # Handle login failure, display an error message, or redirect to the login page
#             return render(request, 'login.html', {'error_message': 'Invalid login credentials'})

# from django.contrib.auth import login, authenticate
# from django.http import HttpResponse

# def login_view(request):
#     if request.method == 'POST':
#         correo = request.POST['correo']
#         contrasena = request.POST['contrasena']

#         print(correo)

#         if user is not None:
#             login(request, user)
#             return HttpResponseRedirect('Entrance')  # Redirige al panel de control
#         else:
#             return HttpResponse("Credenciales incorrectas. Inténtalo de nuevo.")

#     return render(request, 'login.html')  # Reemplaza 'login.html' con tu plantilla de inicio de sesión


# def logout_view(request):
#     logout(request)
#     return redirect('login')

def Home(request):
    user = Usuarios.objects.all()
    
    return render(request, 'usersHome.html', {"Users":user}) 

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


def verDetallesUsuario(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_usuario = request.GET.get('usuario_id')
        
        if id_usuario:
            try:
                usuario = Usuarios.objects.get(id_usuario=id_usuario)
                
                data = {
                    'Rol': usuario.id_rol.nombre_rol,
                    'Nombre de Usuario': usuario.nombre_usuario,
                    'documento': usuario.correo,
                    'Estado': usuario.estado,
                    
                }
                return JsonResponse({'success': data})
            except Usuarios.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de Usuario no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})



def createUser(request):
    roles = Roles.objects.all()
    
    if request.method == 'POST':
        id_rol = request.POST['iRole']
        nombre_usuario = request.POST['iNombre']
        correo = request.POST['iCorreo']
        contrasena = request.POST['iPassword']
        
        rl = Roles.objects.get(id_rol=id_rol)

        Usuarios.objects.create(id_rol=rl, nombre_usuario=nombre_usuario, correo=correo, contrasena=contrasena)
        return JsonResponse({'success': True})
    return render(request, 'createUser.html', {"rols":roles})

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


def rol_unico(request):
    nombre_rol = request.GET.get("nombre_rol", "")
    rol_existe = Roles.objects.filter(nombre_rol=nombre_rol).exists()
    print(rol_existe)
    return JsonResponse({"existe": rol_existe})


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


