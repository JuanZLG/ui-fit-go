from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Proveedores


def Home(request):
    proveedores = Proveedores.objects.all()
    return render(request, 'providersHome.html', {"proveedores":proveedores})  # Enviar lista
# .order_by('-estado')

# def crear_proveedor(request):
#     if request.method == 'POST':
#         nombre = request.POST['nombre']
#         telefono = request.POST['telefono']
#         correo = request.POST['correo']
#         estado = request.POST['estado']
#         proveedor = Proveedores.objects.create(nombre_proveedor=nombre, telefono=telefono, correo=correo, estado=estado)
#         return redirect('proveedores')
#     return render(request, 'create.html')

from django.contrib import messages

def crear_proveedor(request):
    if request.method == 'POST':
        nombre = request.POST['nombre_proveedor']
        telefono = request.POST['telefono']
        correo = request.POST['correo']

        if not nombre or not telefono or not correo:
            messages.error(request, 'Todos los campos son requeridos.')
        elif not telefono.isdigit() or len(telefono) not in [8, 10]:
            messages.error(request, 'Número de teléfono inválido.')
        else:
            proveedor = Proveedores.objects.create(nombre_proveedor=nombre, telefono=telefono, correo=correo)
            messages.success(request, 'El proveedor ha sido registrado: ' + proveedor.nombre_proveedor)
            return redirect('proveedores')

    return render(request, 'createProvider.html')

# def editar_proveedor(request, id_proveedor):
#     if request.method == 'POST':
#         nombre = request.POST['nombre']
#         telefono = request.POST['telefono']
#         correo = request.POST['correo']
#         estado = request.POST['estado']     
#         proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
#         proveedor.nombre_proveedor = nombre
#         proveedor.telefono = telefono
#         proveedor.correo = correo
#         proveedor.estado = estado
#         proveedor.save()
#         return redirect('/Home')
#     else:
#         proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
#         return render(request, 'Editar.html', {"proveedor":proveedor}) 



# def estado_proveedor(request, id_proveedor):
#     proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
    
#     if proveedor.estado == 1:
#         proveedor.estado = 0
#     else:
#         proveedor.estado = 1
#     proveedor.save()
#     return redirect('providersHome')  # O redirige a donde quieras




def estado_ajax(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_proveedor = request.GET.get('proveedor_id')
        nuevo_estado = request.GET.get('nuevo_estado')
        
        try:
            proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
            proveedor.estado = int(nuevo_estado)
            proveedor.save()
            
            return JsonResponse({'status': 'success'})
        except Proveedores.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Proveedor no encontrado'})
        
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})

