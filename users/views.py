
from django.shortcuts import render, redirect
from django.urls import reverse
import json
from urllib.parse import parse_qs
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from users.models import Roles, Permisos, Usuarios, Rolespermisos


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
            return JsonResponse({'status': 'error', 'message': 'Usuario no Encontrado'})
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})