from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Proveedores


def Home(request):
    proveedores = Proveedores.objects.all()
    return render(request, 'providersHome.html', {"proveedores":proveedores})  # Enviar lista

def crear_proveedor(request):
    if request.method == 'POST':
        nombre = request.POST['nombre_proveedor']
        telefono = request.POST['telefono']
        correo = request.POST['correo']
        proveedor = Proveedores.objects.create(nombre_proveedor=nombre, telefono=telefono, correo=correo)
        return JsonResponse({'success': True})
    return render(request, 'createProvider.html')

def editar_proveedor(request, id_proveedor):
    if request.method == 'POST':
        nombre = request.POST['nombre_proveedor']
        telefono = request.POST['telefono']
        correo = request.POST['correo']
        estado = request.POST['estado']
        Proveedores.objects.filter(id_proveedor=id_proveedor).update(
            nombre_proveedor=nombre,
            telefono=telefono,
            correo=correo,
            estado=estado
        )
        response_data = {'success': True}
        return JsonResponse(response_data)    
    proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
    return render(request, 'editProvider.html', {"proveedor":proveedor}) 

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

