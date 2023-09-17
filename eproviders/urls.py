from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns = [
    path('', views.Home, name='proveedores'), 
    path('Crear/', views.crearProveedor, name='crearProveedor'), 
    path('Editar/<int:id_proveedor>', views.editarProveedor, name='editarProveedor'),
    path('Estado/', views.cambiarEstadoProveedor, name='cambiarEstadoProveedor'),
    path('Detalles/', views.verDetallesProveedor, name='verDetallesProveedor')
]
