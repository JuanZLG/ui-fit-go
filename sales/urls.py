from django.urls import path, include 
from . import views 

urlpatterns = [
    path('', views.Home, name='ventas'),
    path('create/', views.crear_venta, name='crear_venta'),
    path('buscar_documentos/', views.buscar_documentos, name='buscar_documentos'),
    path('buscar_productos/', views.buscar_productos, name='buscar_productos'),
    path('obtener_precio/', views.obtener_precio, name='obtener_precio_producto'),
    path('verVenta/<int:venta_id>/', views.detalles_venta, name='verVenta'),
    path('cambiarEstado/', views.cambiarEstado, name='cambiarEstado'),

]
