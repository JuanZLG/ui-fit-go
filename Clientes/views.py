from django.shortcuts import render, redirect
from .models import Clientes, Municipios
from django.http import JsonResponse


# def home(request):
#     clienteRegistrados = Clientes.objects.all()
#     return render(request, "Plantilla.html", {"clientes": clienteRegistrados})


# def Listica(request):
#     clientes = Clientes.objects.all()  
#     context = {'clientes': clientes} 
#     return render(request, 'Plantilla.html', context)


def lista_clientes(request):
    clientes = Clientes.objects.all().order_by('-estado')  
    context = {'clientes': clientes}  
    return render(request, 'Plantilla.html', context)

def agregar_cliente(request):
    municipios = Municipios.objects.all()  
    return render(request, 'PlantillaAgregar.html', {'municipios': municipios})






def agregar_cliente_post(request):
    if request.method == 'POST':
        documento = request.POST.get('iDocumento')
        nombres = request.POST.get('iNombres')
        apellidos = request.POST.get('iApellidos')
        celular = request.POST.get('iCelular')
        barrio = request.POST.get('iBarrio')
        direccion = request.POST.get('iDireccion')
        estado = request.POST.get('id_estado')
        id_municipio = request.POST.get('id_municipio')
        
        if not documento or not nombres or not apellidos or not celular or not barrio or not direccion:
            return render(request, 'PlantillaAgregar.html', {'error': 'Todos los campos son obligatorios'})
        
        try:
            municipio = Municipios.objects.get(pk=id_municipio)
        except Municipios.DoesNotExist:
            return render(request, 'PlantillaAgregar.html', {'error': 'El municipio seleccionado no es válido'})
        
        cliente = Clientes(documento=documento, nombres=nombres, apellidos=apellidos,
                           celular=celular, barrio=barrio, direccion=direccion, estado=estado, id_municipio=municipio)
        cliente.save()
        
        return redirect('lista_clientes')  
    
    municipios = Municipios.objects.all()  
    return render(request, 'PlantillaAgregar.html', {'municipios': municipios})




def redirigir_editar_cliente(request, cliente_id):
    cliente = Clientes.objects.get(id_cliente=cliente_id)
    municipios = Municipios.objects.all()  
    return render(request, 'PlantillaModificar.html', {'cliente': cliente, 'municipios': municipios})

def editar_cliente(request, cliente_id):
    cliente = Clientes.objects.get(id_cliente=cliente_id)

    if request.method == 'POST':
        documento = request.POST.get('iDocumento')
        nombres = request.POST.get('iNombres')
        apellidos = request.POST.get('iApellidos')
        celular = request.POST.get('iCelular')
        barrio = request.POST.get('iBarrio')
        direccion = request.POST.get('iDireccion')
        estado = request.POST.get('id_estado')
        id_municipio = request.POST.get('id_municipio')

        
        cliente.documento = documento
        cliente.nombres = nombres
        cliente.apellidos = apellidos
        cliente.celular = celular
        cliente.barrio = barrio
        cliente.direccion = direccion
        cliente.estado = estado
        cliente.id_municipio = Municipios.objects.get(pk=id_municipio)
        cliente.save()

        return redirect('lista_clientes')  

    municipios = Municipios.objects.all()  
    return render(request, 'PlantillaModificar.html', {'cliente': cliente, 'municipios': municipios})



def cambiar_estado_cliente_ajax(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cliente_id = request.GET.get('cliente_id')
        nuevo_estado = request.GET.get('nuevo_estado')
        
        try:
            cliente = Clientes.objects.get(id_cliente=cliente_id)
            cliente.estado = int(nuevo_estado)
            cliente.save()
            
            return JsonResponse({'status': 'success'})
        except Clientes.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cliente no encontrado'})
        
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})






