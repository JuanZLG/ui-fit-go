from django.shortcuts import render, redirect
from .models import Clientes, Municipios, Departamentos
from django.http import JsonResponse

def lista_clientes(request):
    clientes = Clientes.objects.all().order_by('-estado')  
    context = {'clientes': clientes}  
    return render(request, 'customersHome.html', context)

def agregarCliente(request):
    municipios = Municipios.objects.all()  
    return render(request, 'createCustomer.html', {'municipios': municipios})

from eclients.models import Clientes, Municipios, Departamentos

def agregarClientePost(request):
    if request.method == 'POST':
        documento = request.POST.get('iDocumento')
        nombres = request.POST.get('iNombres')
        apellidos = request.POST.get('iApellidos')
        celular = request.POST.get('iCelular')
        barrio = request.POST.get('iBarrio')
        direccion = request.POST.get('iDireccion')
        estado = request.POST.get('id_estado')
        departamento_nombre = request.POST.get('nombre_departamento')
        municipio_nombre = request.POST.get('nombre_municipio')

        if not documento or not nombres or not apellidos or not celular or not barrio or not direccion:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios'})

        departamento = Departamentos.objects.filter(nombre_departamento=departamento_nombre).first()

        if not departamento:
            departamento = Departamentos.objects.create(nombre_departamento=departamento_nombre)

        municipio, created = Municipios.objects.get_or_create(
            nombre_municipio=municipio_nombre,
            id_departamento=departamento
        )

        cliente = Clientes(
            id_municipio=municipio,
            documento=documento,
            nombres=nombres,
            apellidos=apellidos,
            celular=celular,
            barrio=barrio,
            direccion=direccion,
            estado=estado,
        )
        cliente.save()

        # Devuelve un JSON con éxito
        return JsonResponse({'success': True, 'message': 'Cliente creado con éxito'})

    municipios = Municipios.objects.all()
    return render(request, 'createCustomer.html', {'municipios': municipios})













def redirigirEditar(request, cliente_id):
    cliente = Clientes.objects.get(id_cliente=cliente_id)
    municipios = Municipios.objects.all()  
    return render(request, 'editCustomer.html', {'cliente': cliente, 'municipios': municipios})

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Clientes, Municipios, Departamentos

def editarCliente(request, cliente_id):
    # Obtener el cliente existente o mostrar un error 404 si no se encuentra
    cliente = get_object_or_404(Clientes, id_cliente=cliente_id)

    if request.method == 'POST':
        documento = request.POST.get('iDocumento')
        nombres = request.POST.get('iNombres')
        apellidos = request.POST.get('iApellidos')
        celular = request.POST.get('iCelular')
        barrio = request.POST.get('iBarrio')
        direccion = request.POST.get('iDireccion')
        estado = request.POST.get('id_estado')
        departamento_nombre = request.POST.get('nombre_departamento')
        municipio_nombre = request.POST.get('nombre_municipio')

        if not documento or not nombres or not apellidos or not celular or not barrio or not direccion:
            # Devuelve un JSON con un mensaje de error
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios'})

        # Intenta obtener el departamento existente o el primero con el mismo nombre
        departamento = Departamentos.objects.filter(nombre_departamento=departamento_nombre).first()

        if not departamento:
            # Si no existe, crea uno nuevo
            departamento = Departamentos.objects.create(nombre_departamento=departamento_nombre)

        # Verifica si el municipio ya existe en la base de datos o créalo si no existe
        municipio, created = Municipios.objects.get_or_create(
            nombre_municipio=municipio_nombre,
            id_departamento=departamento
        )

        # Actualiza los campos del cliente existente con los valores recibidos
        cliente.id_municipio = municipio
        cliente.documento = documento
        cliente.nombres = nombres
        cliente.apellidos = apellidos
        cliente.celular = celular
        cliente.barrio = barrio
        cliente.direccion = direccion
        cliente.estado = estado
        cliente.save()

        # Devuelve un JSON con éxito
        return JsonResponse({'success': True, 'message': 'Cliente actualizado con éxito'})

    municipios = Municipios.objects.all()
    return render(request, 'editCustomer.html', {'cliente': cliente, 'municipios': municipios})




def cambiarEstado(request):
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






