from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns = [
    path('', views.Home, name='proveedores'), 
    path('Crear/', views.crearProveedor, name='crearProveedor'), 
    path('proveedor_unico/', views.proveedor_unico, name='proveedor_unico'),
    path('proveedor_unico_edit/', views.proveedor_unico_edit, name='proveedor_unico_edit'),
    path('Editar/<int:id_proveedor>', views.editarProveedor, name='editarProveedor'),
    path('Estado/', views.cambiarEstadoProveedor, name='cambiarEstadoProveedor'),
    path('Detalles/', views.verDetallesProveedor, name='verDetallesProveedor')
]
