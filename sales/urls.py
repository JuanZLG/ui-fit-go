from django.urls import path, include 
from . import views 

urlpatterns = [
    path('', views.Home, name='ventas'),
    path('create/', views.crear_venta, name='crear_venta'),
    path('buscar_documentos/', views.buscar_documentos, name='buscar_documentos'),
    path('buscar_cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('buscar_productos/', views.buscar_productos, name='buscar_productos'),
    path('validar_cantidad/', views.validar_cantidad, name='validar_cantidad'),
    path('validar_productos/', views.validar_producto, name='validar_producto'),
    path('existencia_producto/', views.existencia_producto, name='existencia_producto'),
    path('validar_cliente/', views.validar_cliente, name='validar_cliente'),
    path('Edit/<int:id_venta>', views.editar_venta, name='editarVenta'),
    path('obtener_precio/', views.obtener_precio, name='obtener_precio_producto'),
    path('cambiarEstado/', views.cambiarEstado, name='cambiarEstadoVentas'),
    path('detalles_venta/', views.detalles_venta, name='verDetallesVenta')

]