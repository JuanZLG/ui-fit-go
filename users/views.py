
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


# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.http import JsonResponse
# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.http import JsonResponse, HttpResponse  # Importa HttpResponse

# def login_view(request):
#     print("Vista de inicio de sesión llamada")

#     if request.method == "POST":
#         correo = request.POST.get('email')  # Campo de correo electrónico del formulario
#         contrasena = request.POST.get('password')  # Campo de contraseña del formulario
        
#         print(f"Correo: {correo}")  # Imprimir el correo electrónico ingresado
#         print(f"Contraseña: {contrasena}")  # Imprimir la contraseña ingresada
        
#         user = authenticate(request, correo=correo, contrasena=contrasena)
        
#         if user is not None:
#             login(request, user)
#             print(f"Usuario autenticado: {user.correo}")  # Imprimir el correo del usuario autenticado
#             return redirect('dashboard')  # Redirigir al panel de control del usuario
#         else:
#             print("Credenciales incorrectas")
#             context = {'error': 'Credenciales incorrectas'}
#             return render(request, 'login.html', context)
    
#     # Manejar solicitudes GET
#     return render(request, 'login.html')  # Devuelve una respuesta HTTP para solicitudes GET

# # Resto del código...







# def logout_view(request):
#     logout(request)
#     return redirect('login')


# def Home(request):
#     user = Usuarios.objects.all()
#     return render(request, 'usersHome.html', {"Users":user}) 

# def cambiarEstadoDeUsuario(request):
#     if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         id_usuario = request.GET.get('usuario_id')
#         nuevo_estado = request.GET.get('nuevo_estado')
#         try:
#             usuario = Usuarios.objects.get(id_usuario=id_usuario)
#             usuario.estado = int(nuevo_estado)
#             usuario.save()
#             return JsonResponse({'status': 'success'})
#         except Usuarios.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Usuario no Encontrado'})
#     return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})