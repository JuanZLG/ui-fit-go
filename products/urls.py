from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 


urlpatterns=[
    path('', views.Home, name='productos'), 
    path('addproduct/', views.createProduct, name="createProducts"),
    # path('Editar/', views.editar_proveedor, name='editarProveedor'),
    path('Estado/', views.cambiarEstadoDeProducto, name='cambiarEstadoDeProducto'),
]
