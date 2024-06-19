from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='purchases'),
    path('createPurchase/', views.crear_compra, name='crear_compra'),
    path('buscar_proveedores/', views.buscar_proveedor, name='buscar_proveedores'),
    path('detalles_compra/<int:compra_id>/', views.detalles_compra, name='detalles_compra'),
    path('obtener_detalles_compra/<int:compra_id>/', views.obtener_detalles_compra, name='obtener_detalles_compra'),
    path('generar_factura/<int:compra_id>/', views.generar_factura_pdf, name='generar_factura_pdf'),    
    path('generar_informe_pdf/', views.generar_informe_pdf, name='generar_informe_pdf'),
    path('cambiarEstado/', views.cambiarEstado, name='cambiarEstadoCompra'),
]