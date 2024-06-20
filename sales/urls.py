from django.urls import path
from . import views 

urlpatterns = [
    path('', views.Home, name='ventas'),
    path('create/', views.crear_venta, name='crear_venta'),
    path('buscar_cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('buscar_productos/', views.buscar_productos, name='buscar_productos'),
    path('verificar_stock/', views.verificar_stock, name='verificar_stock'),
    path('cambiarEstado/', views.cambiarEstado, name='cambiarEstadoVentas'),
    path('detalles_venta/', views.detalles_venta, name='verDetallesVenta'),
    path('cargar_pedidos/', views.cargar_pedidos, name='cargar_pedidos'),
    path('agregarDetalleATabla/', views.agregarDetalleATabla, name='agregarDetalleATabla'),
    path('generar_factura/<int:venta_id>/', views.generar_factura_pdf_venta, name='generar_factura_pdf_venta'),
    path('generar_informe_pdf_ventas/', views.generar_informe_pdf_ventas, name='generar_informe_pdf_ventas'),
]