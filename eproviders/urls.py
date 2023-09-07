from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns = [
    path('', views.Home, name='proveedores'), 
    path('create/', views.crear_proveedor, name='crear_proveedor'), 
    path('edit/<int:id_proveedor>', views.editar_proveedor, name='editar_proveedor'),
    path('status/', views.estado_ajax, name='estado_ajax'),

]
