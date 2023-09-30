
# from django.shortcuts import render, redirect
# from django.urls import reverse
# import json
# from urllib.parse import parse_qs
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.views.decorators.csrf import csrf_exempt
# from users.models import Roles, Permisos, Usuarios, Rolespermisos
# from django.contrib.auth import authenticate, login, logout
# from django.shortcuts import render, redirect

# def login_view(request):
#     if request.method == 'POST':
#         form = CustomAuthenticationForm(request, request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 # Redirigir al usuario a donde quieras después de iniciar sesión
#                 return redirect('ruta_despues_de_inicio_de_sesion')
#             else:
#                 # El inicio de sesión falló
#                 # Puedes mostrar un mensaje de error o realizar otras acciones aquí
#                 pass
#     else:
#         form = CustomAuthenticationForm()
#     return render(request, 'login.html', {'form': form})


# def logout_view(request):
#     logout(request)
#     return redirect('login')


# def Home(request):
#     user = Usuarios.objects.all()
#     return render(request, 'usersHome.html', {"Users":user}) 

# def Home(request):
#     user = Usuarios.objects.all()
#     return render(request, 'algo.html', {"Users":user}) 

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
        rol = rp.id_rol.nombre_rol
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

    return render(request, 'rolesHome.html', {"permisos_count": permisos_count })


@csrf_exempt
def createRol(request):
    print("crear")

    if request.method == 'POST':
        data = json.loads(request.body)
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

        response_data = {"success": True}
        return JsonResponse(response_data)



@csrf_exempt
def editRol(request):
    print("editar")



