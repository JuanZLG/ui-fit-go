from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns = [
    path('', views.Home, name='proveedores'), 
    path('create/', views.crear_proveedor, name='create'), 

    # path('edit/<int:id_proveedor>/', views.editar_proveedor, name='Editar'),
    # path('status/<int:id_proveedor>/', views.estado_proveedor, name='Estado'),
    path('ajax/', views.estado_ajax, name='estado_ajax'),

]
