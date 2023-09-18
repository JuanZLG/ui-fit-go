from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns=[
    path('', views.Home, name='productos'), 
    path('addproduct/', views.createProduct, name="createAProduct"),
    path('editproduct/<int:producto_id>/', views.editProduct, name='editAProduct'),
    path('Estado/', views.cambiarEstadoDeProducto, name='cambiarEstadoDeProducto'),
]
