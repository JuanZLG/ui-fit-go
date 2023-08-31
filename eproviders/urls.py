from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns = [
    path('', views.Home, name='proveedores'), 
    path('create/', views.crear_proveedor, name='create'), 

    # path('Editar/<int:id_proveedor>/', views.editar, name='Editar'),
    # path('Home/Estado/<int:id_proveedor>/', views.estado, name='Estado'),
]
