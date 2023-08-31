from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Proveedores


def Home(request):
    proveedores = Proveedores.objects.all().order_by('-estado')
    return render(request, 'providersHome.html', {"proveedores":proveedores})  # Enviar lista


def crear_proveedor(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        telefono = request.POST['telefono']
        correo = request.POST['correo']
        estado = request.POST['estado']
        proveedor = Proveedores.objects.create(nombre_proveedor=nombre, telefono=telefono, correo=correo, estado=estado)
        return redirect('proveedores')
    return render(request, 'create.html')


def editar(request, id_proveedor):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        telefono = request.POST['telefono']
        correo = request.POST['correo']
        estado = request.POST['estado']     
        proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
        proveedor.nombre_proveedor = nombre
        proveedor.telefono = telefono
        proveedor.correo = correo
        proveedor.estado = estado
        proveedor.save()
        return redirect('/Home')
    else:
        proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
        return render(request, 'Editar.html', {"proveedor":proveedor}) 



# def Estado(request, id_proveedor):
#     proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
    
#     if proveedor.estado == 1:
#         proveedor.estado = 0
#     else:
#         proveedor.estado = 1
    
#     proveedor.save()
#     return redirect('/Home')  # O redirige a donde quieras

