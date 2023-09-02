from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Proveedores


def Home(request):
    proveedores = Proveedores.objects.all()
    return render(request, 'providersHome.html', {"proveedores":proveedores})  # Enviar lista


# def crear_proveedor(request):
#     if request.method == 'POST':
#         nombre = request.POST['nombre']
#         telefono = request.POST['telefono']
#         correo = request.POST['correo']
#         estado = request.POST['estado']
#         proveedor = Proveedores.objects.create(nombre_proveedor=nombre, telefono=telefono, correo=correo, estado=estado)
#         return redirect('proveedores')
#     return render(request, 'create.html')

from django.http import JsonResponse

def crear_proveedor(request):
    if request.method == 'POST':
        nombre = request.POST['nombre_proveedor']
        telefono = request.POST['telefono']
        correo = request.POST['correo']

        # Validaciones de campo requerido
        errors = {}
        if not nombre:
            errors['nombre_proveedor'] = 'El campo Nombre es requerido.'
        if not telefono:
            errors['telefono'] = 'El campo Teléfono es requerido.'
        if not correo:
            errors['correo'] = 'El campo Correo es requerido.'

        if errors:
            # Devuelve una respuesta JSON con los errores
            return JsonResponse({'success': False, 'errors': errors})
        else:
            # Si no hay errores, realiza el proceso de creación del proveedor
            # y devuelve una respuesta JSON de éxito
            # (debes agregar aquí la lógica para crear el proveedor)
            proveedor = Proveedores.objects.create(nombre_proveedor=nombre, telefono=telefono, correo=correo)

            return JsonResponse({'success': True})

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

