from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Proveedores


def Home(request):
    proveedores = Proveedores.objects.all()
    return render(request, 'providersHome.html', {"proveedores":proveedores}) 

def crear_proveedor(request):
    if request.method == 'POST':
        nombre = request.POST['nombre_proveedor']
        telefono = request.POST['telefono']
        correo = request.POST['correo']
        proveedor = Proveedores.objects.create(nombre_proveedor=nombre, telefono=telefono, correo=correo)
        return JsonResponse({'success': True})

from django.views.decorators.csrf import csrf_exempt

import json
from urllib.parse import parse_qs
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Proveedores

@csrf_exempt
def editar_proveedor(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor_id')
        form_data = request.POST.get('formData')
        form_data_dict = parse_qs(form_data)

        nombre_proveedor = form_data_dict.get('nombre_proveedor', [''])[0]
        telefono = form_data_dict.get('telefono', [''])[0]
        correo = form_data_dict.get('correo', [''])[0]

        Proveedores.objects.filter(id_proveedor=proveedor_id).update(
            nombre_proveedor=nombre_proveedor,
            telefono=telefono,
            correo=correo,
        )

        response_data = {'success': True}
        return JsonResponse(response_data)



from django.http import JsonResponse

# @csrf_exempt
# def editar_proveedor(request):
#     if request.method == 'POST':
#         id_proveedor = request.POST.get('proveedor_id')
#         nombre_proveedor = request.POST.get('nombre_proveedor')
#         telefono = request.POST.get('telefono')
#         correo = request.POST.get('correo')

#         try:
#             proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
#         except Proveedores.DoesNotExist:
#             response_data = {'success': False, 'message': 'Proveedor no encontrado'}
#             return JsonResponse(response_data, status=404)

#         # Actualiza los datos del proveedor
#         proveedor.nombre_proveedor = nombre_proveedor
#         proveedor.telefono = telefono
#         proveedor.correo = correo
#         proveedor.save()

#         response_data = {'success': True, 'message': 'Proveedor actualizado correctamente'}
#         return JsonResponse(response_data)

#     # Manejar otras solicitudes, como GET, si es necesario
#     return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)



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
                # Si el proveedor se encuentra, puedes devolver sus detalles en formato JSON
                data = {
                    'nombre_proveedor': proveedor.nombre_proveedor,
                    'telefono': proveedor.telefono,
                    'correo': proveedor.correo,
                    'estado': proveedor.estado,
                }
                return JsonResponse({'success': data})
            except Proveedores.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Proveedor no encontrado'})
        else:
            return JsonResponse({'status': 'error', 'message': 'ID de proveedor no proporcionado'})
    
    return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})



# def verDetallesProveedor(request):
#     if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         id_proveedor = request.GET.get('proveedor_id')
#         try:
#             proveedor = Proveedores.objects.get(id_proveedor=id_proveedor)
#             return JsonResponse({'success': proveedor})
#         except Proveedores.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Proveedor no encontrado'})
        
#     return JsonResponse({'status': 'error', 'message': 'Solicitud inválida'})



