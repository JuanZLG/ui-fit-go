from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from urllib.parse import parse_qs
from django.views.decorators.http import require_POST
from .models import Proveedores


def Home(request):
    proveedores = Proveedores.objects.all()
    return render(request, 'providersHome.html', {"proveedores":proveedores}) 


def crearProveedor(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_proveedor')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo')
        direccion = request.POST.get('direccion')
        informacion_adicional = request.POST.get('informacion')
        tipo_documento = request.POST.get('tipoIdentificacion')
        numero_documento_nit = request.POST.get('identificacion')

        Proveedores.objects.create(
            nombre_proveedor=nombre,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
            informacion_adicional=informacion_adicional,
            tipo_documento=tipo_documento,
            numero_documento_nit=numero_documento_nit
        )
        return JsonResponse({'success': True})
    return render(request, 'createProvider.html')

def proveedor_unico(request):
    proveedor = request.GET.get("proveedor", "")
    proveedor_existe = Proveedores.objects.filter(nombre_proveedor=proveedor).exists()
    return JsonResponse({"existe": proveedor_existe})


def editarProveedor(request, id_proveedor):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_proveedor')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo')
        direccion = request.POST.get('direccion')
        informacion_adicional = request.POST.get('informacion')
        tipo_documento = request.POST.get('tipoIdentificacion')
        numero_documento_nit = request.POST.get('identificacion')
        Proveedores.objects.filter(id_proveedor=id_proveedor).update(
            nombre_proveedor=nombre,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
            informacion_adicional=informacion_adicional,
            tipo_documento=tipo_documento,
            numero_documento_nit=numero_documento_nit
        )
        response_data = {'success': True}
        return JsonResponse(response_data)    
    proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
    return render(request, 'editProvider.html', {"proveedor":proveedor}) 



def cambiarEstadoProveedor(request):
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



def verDetallesProveedor(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id_proveedor = request.GET.get('proveedor_id')
        
        if id_proveedor:
            try:
                proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)

                data = {
                    'nombre_proveedor': proveedor.nombre_proveedor,
                    'telefono': proveedor.telefono,
                    'correo': proveedor.correo,
                    'estado': proveedor.estado,
                    'direccion': proveedor.direccion,
                    'tipo': proveedor.tipo_documento,
                    'identificacion': proveedor.numero_documento_nit,
                    'informacion': proveedor.informacion_adicional,
                }
                return JsonResponse({'success': data})
            except Proveedores.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Proveedor no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de proveedor no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})

