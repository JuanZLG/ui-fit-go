from django.urls import path, include 
from . import views 

urlpatterns = [
    path('', views.Home, name='ventas'),
    path('create/', views.crear_venta, name='create'),
    path('buscar_documentos/', views.buscar_documentos, name='buscar_documentos'),
    path('buscar_productos/', views.buscar_productos, name='buscar_productos'),
    path('obtener_precio/', views.obtener_precio, name='obtener_precio_producto'),
]
