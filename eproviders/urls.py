from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns = [
    path('', views.Home, name='proveedores'), 
    path('Crear/', views.crear_proveedor, name='crear_proveedor'), 
    path('Editar/', views.editar_proveedor, name='editarProveedor'),
    path('Estado/', views.cambiarEstadoProveedor, name='cambiarEstadoProveedor'),
    path('Detalles/', views.verDetallesProveedor, name='verDetallesProveedor')
]
