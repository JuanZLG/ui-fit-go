from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from .models import Clientes, Municipios, Departamentos
from django.http import JsonResponse
from django.shortcuts import render
from django.db import IntegrityError
from django.conf import settings
from tuiranfitgo.views import jwt_cookie_required, module_access_required

@jwt_cookie_required
@module_access_required('clientes')
def lista_clientes(request):
    clientes = Clientes.objects.all()
    context = {'clientes': clientes}  
    return render(request, 'customersHome.html', context)

@jwt_cookie_required
@module_access_required('clientes')
def ver_cliente(request, cliente_id):
    cliente = get_object_or_404(Clientes, id_cliente=cliente_id)
    cliente_data = {
        'documento': cliente.documento,
        'nombres': cliente.nombres,
        'apellidos': cliente.apellidos,
        'celular': cliente.celular,
    }
    return JsonResponse({'cliente': cliente_data})

@jwt_cookie_required
@module_access_required('clientes')
def agregarCliente(request):
    municipios = Municipios.objects.all()  
    return render(request, 'createCustomer.html', {'municipios': municipios})

@jwt_cookie_required
@module_access_required('clientes')
def agregarClientePost(request):
    if request.method == 'POST':
        documento = request.POST.get('iDocumento')
        nombres = request.POST.get('iNombres')
        apellidos = request.POST.get('iApellidos')
        celular = request.POST.get('iCelular')
        barrio = request.POST.get('iBarrio')
        direccion = request.POST.get('iDireccion')
        departamento_nombre = request.POST.get('nombre_departamento')
        municipio_nombre = request.POST.get('nombre_municipio')

        if not documento or not nombres or not apellidos or not celular or not barrio or not direccion:
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios'})

        try:
            departamento = Departamentos.objects.get(nombre_departamento=departamento_nombre)
        except Departamentos.DoesNotExist:
            departamento = Departamentos.objects.create(nombre_departamento=departamento_nombre)

        try:
            municipio = Municipios.objects.get(
                nombre_municipio=municipio_nombre,
                id_departamento=departamento
            )
        except Municipios.DoesNotExist:
            municipio = Municipios.objects.create(
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
            estado=1,
        )

        try:
            cliente.save()
            return JsonResponse({'success': True, 'message': 'Cliente creado con éxito'})
        except IntegrityError as e:
            return JsonResponse({'success': False, 'message': 'Error: El documento ya está registrado en la base de datos.'})

    municipios = Municipios.objects.all()
    return render(request, 'createCustomer.html', {'municipios': municipios})

@jwt_cookie_required
@module_access_required('clientes')
def redirigirEditar(request, cliente_id):
    cliente = Clientes.objects.get(id_cliente=cliente_id)
    municipios = Municipios.objects.all()  
    return render(request, 'editCustomer.html', {'cliente': cliente, 'municipios': municipios})

@jwt_cookie_required
@module_access_required('clientes')
def editarCliente(request, cliente_id):
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
            return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios'})

        try:
            departamento, created = Departamentos.objects.get_or_create(nombre_departamento=departamento_nombre)

            municipio, created = Municipios.objects.get_or_create(nombre_municipio=municipio_nombre, id_departamento=departamento)
        except:
            return JsonResponse({'success': False, 'message': 'Error al crear departamento o municipio'})

        cliente.id_municipio = municipio
        cliente.documento = documento
        cliente.nombres = nombres
        cliente.apellidos = apellidos
        cliente.celular = celular
        cliente.barrio = barrio
        cliente.direccion = direccion
        cliente.id_estado = estado
        cliente.save()

        return JsonResponse({'success': True, 'message': 'Cliente actualizado con éxito'})

    return render(request, 'editCustomer.html', {'cliente': cliente, 'departamento_registrado': cliente.id_municipio.id_departamento.nombre_departamento, 'municipio_registrado': cliente.id_municipio.nombre_municipio})

@jwt_cookie_required
@module_access_required('clientes')
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

@jwt_cookie_required
@module_access_required('clientes')
def verDetallesCliente(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_cliente = request.GET.get('cliente_id')
        
        if id_cliente:
            try:
                cliente = Clientes.objects.get(id_cliente=id_cliente)
                data = {
                    'nombres': cliente.nombres,
                    'apellidos': cliente.apellidos,
                    'documento': cliente.documento,
                    'celular': cliente.celular,
                    'barrio': cliente.barrio,
                    'direccion': cliente.direccion,
                    'estado': cliente.estado,
                    'municipio': cliente.id_municipio.nombre_municipio,
                    'departamento': cliente.id_municipio.id_departamento.nombre_departamento,
                }
                return JsonResponse({'success': data})
            except Clientes.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Cliente no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de cliente no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})

@module_access_required('clientes')
def validar_documento(request):
    documento = request.GET.get('documento', '')

    cliente_existente = Clientes.objects.filter(documento=documento).exists()

    return JsonResponse({'existe': cliente_existente})

