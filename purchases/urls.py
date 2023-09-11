from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='purchases'),
    path('create/', views.crear_compra, name='crear_compra'),
    path('buscar_proveedores/', views.buscar_proveedores, name='buscar_proveedores'),
    path('validar_producto/', views.validar_producto, name='validar_producto'),
    path('obtener_precio/', views.obtener_precio, name='obtener_precio_producto'),
    path('detalles_compra/<int:compra_id>/', views.detalles_compra, name='detalles_compra'),
    path('validar_proveedor/', views.validar_proveedor, name='validar_proveedor'),

    path('cambiarEstado/', views.cambiarEstado, name='cambiar_estado_compra'),
]