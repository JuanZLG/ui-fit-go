from django.shortcuts import render, redirect
from django.http import HttpResponse
from eproviders.forms import CrearProveedorForm
from .models import Proveedores


def Home(request):
    proveedores = Proveedores.objects.all().order_by('-estado')
    return render(request, 'providersHome.html', {"proveedores":proveedores})  # Enviar lista


# def registrar(request):
#     if request.method == 'POST':
#         nombre = request.POST['nombre']
#         telefono = request.POST['telefono']
#         correo = request.POST['correo']
#         estado = request.POST['estado']
#         proveedor = Proveedores.objects.create(nombre_proveedor=nombre, telefono=telefono, correo=correo, estado=estado)
#         return redirect('/Home')
#     return render(request, 'Registrar.html')

def crear_proveedor(request):
    if request.method == 'POST':
        form = CrearProveedorForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre_proveedor']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']
            estado = form.cleaned_data['estado']  
            proveedor = Proveedores(nombre_proveedor=nombre, telefono=telefono, correo=correo, estado=estado)
            proveedor.save()
            
            return HttpResponse('El proveedor ha sido registrado: ' + proveedor.nombre_proveedor)
    else:
        form = CrearProveedorForm()
    
    return render(request, 'create.html', {'form': form})


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

