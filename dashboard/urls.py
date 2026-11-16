from django.urls import path
from . import views 

urlpatterns = [
    path('', views.Entrance, name="entrada"),
    path('dashboard/', views.Home, name='mydashboard'),
    path('guide/', views.UserGuide, name="guideser"),
    path('contar_clientes_activos/', views.contar_clientes_activos, name='contar_clientes_activos'),
    path('calcular_total_compras_y_ventas/', views.calcular_total_compras_y_ventas, name='calcular_total_compras_y_ventas'),
    path('obtener_datos_ventas_y_compras/', views.obtener_datos_ventas_y_compras, name='obtener_datos_ventas_y_compras'),
    path('obtener_todos_los_productos/', views.obtener_todos_los_productos, name='obtener_todos_los_productos'),
    path('obtener_margen_ganancia/', views.obtener_margen_ganancia, name='obtener_margen_ganancia'),
    path('resumen/', views.obtener_resumen, name='obtener_resumen'),
    path('inteligencia/', views.inteligencia_inventario, name='inteligencia_inventario'),
    path('orden_compra_sugerida/', views.orden_compra_sugerida_pdf, name='orden_compra_sugerida_pdf'),
    path('buscar/', views.buscar_global, name='buscar_global'),
    path('contar_pedidos_en_proceso/', views.contar_pedidos_en_proceso, name='contar_pedidos_en_proceso'),
    path('obtener_datos_categorias_productos/', views.obtener_datos_categorias_productos, name='obtener_datos_categorias_productos'),
]
