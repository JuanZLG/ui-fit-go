from django.shortcuts import render, redirect
from .models import Clientes, Municipios
from django.http import JsonResponse


def Home(request):
    clienteRegistrados = Clientes.objects.all()
    return render(request, "Home.html", {"clientes": clienteRegistrados})

# def Home(request):
#     clientes = Clientes.objects.all()  
#     context = {'clientes': clientes}  
#     return render(request, 'Plantilla.html', context)


# def Listica(request):
#     clientes = Clientes.objects.all()  
#     context = {'clientes': clientes} 
#     return render(request, 'Plantilla.html', context)



# def crear(request):
#     municipios = Municipios.objects.all()  
#     return render(request, 'PlantillaAgregar.html', {'municipios': municipios})

# def crear_cliente(request):
#     if request.method == 'POST':
#         documento = request.POST.get('iDocumento')
#         nombres = request.POST.get('iNombres')
#         apellidos = request.POST.get('iApellidos')
#         celular = request.POST.get('iCelular')
#         barrio = request.POST.get('iBarrio')
#         direccion = request.POST.get('iDireccion')
#         estado = request.POST.get('id_estado')
#         id_municipio = request.POST.get('id_municipio')
        
#         ## ACÁ CREO OTRAS PAGINAS SOLA PARA MOSTRAR ERRORES??
#         if not documento or not nombres or not apellidos or not celular or not barrio or not direccion:
#             return render(request, 'create.html', {'error': 'Todos los campos son obligatorios'})
#         try:
#             municipio = Municipios.objects.get(pk=id_municipio)
#         except Municipios.DoesNotExist:
#             return render(request, 'create.html', {'error': 'El municipio seleccionado no es válido'})
        
#         cliente = Clientes(documento=documento, nombres=nombres, apellidos=apellidos,
#                            celular=celular, barrio=barrio, direccion=direccion, estado=estado, id_municipio=municipio)
#         cliente.save()
#         return redirect('Home.html')  
#     else:
#         municipios = Municipios.objects.get(documento=documento)
#         return render(request, 'create.html', {"municipios":municipios}) 
#     return render(request, 'create.html')



def crear_cliente(request):
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
            return render(request, 'create.html', {'error': 'All fields are required'})
        
        try:
            municipio = Municipios.objects.get(pk=id_municipio)
        except Municipios.DoesNotExist:
            return render(request, 'create.html', {'error': 'The selected municipality is not valid'})
        
        cliente = Clientes(documento=documento, nombres=nombres, apellidos=apellidos,
                           celular=celular, barrio=barrio, direccion=direccion, estado=estado, id_municipio=municipio)
        cliente.save()
        return redirect('home')  # Assuming 'home' is the correct URL name
    else:
        municipios = Municipios.objects.all()  # Get all municipalities
        return render(request, 'create.html', {"municipios": municipios})




# def redirigir_editar_cliente(request, cliente_id):
#     cliente = Clientes.objects.get(id_cliente=cliente_id)
#     municipios = Municipios.objects.all()  
#     return render(request, 'PlantillaModificar.html', {'cliente': cliente, 'municipios': municipios})

# def editar_cliente(request, cliente_id):
#     cliente = Clientes.objects.get(id_cliente=cliente_id)

#     if request.method == 'POST':
#         documento = request.POST.get('iDocumento')
#         nombres = request.POST.get('iNombres')
#         apellidos = request.POST.get('iApellidos')
#         celular = request.POST.get('iCelular')
#         barrio = request.POST.get('iBarrio')
#         direccion = request.POST.get('iDireccion')
#         estado = request.POST.get('id_estado')
#         id_municipio = request.POST.get('id_municipio')

        
#         cliente.documento = documento
#         cliente.nombres = nombres
#         cliente.apellidos = apellidos
#         cliente.celular = celular
#         cliente.barrio = barrio
#         cliente.direccion = direccion
#         cliente.estado = estado
#         cliente.id_municipio = Municipios.objects.get(pk=id_municipio)
#         cliente.save()

#         return redirect('Lista')  

#     municipios = Municipios.objects.all()  
#     return render(request, 'PlantillaModificar.html', {'cliente': cliente, 'municipios': municipios})

# def cambiar_estado_cliente(request, cliente_id):
#     cliente = Clientes.objects.get(id_cliente=cliente_id)
    
#     if cliente.estado == 1: 
#         cliente.estado = 0
#     else:
#         cliente.estado = 1
    
#     cliente.save()
#     return redirect('Lista')  




