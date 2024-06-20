from django.urls import path, include  
from . import views 
urlpatterns=[
    path('', views.Entrance, name="entrada"),
    path('dashboard/', views.Home, name='mydashboard'),
    path('guide/', views.UserGuide, name="guideser"),
    path('contar_clientes_activos/', views.contar_clientes_activos, name='contar_clientes_activos'),
    path('calcular_total_compras_y_ventas/', views.calcular_total_compras_y_ventas, name='calcular_total_compras_y_ventas'),
    path('obtener_datos_ventas_y_compras/', views.obtener_datos_ventas_y_compras, name='obtener_datos_ventas_y_compras'),
    path('obtener_todos_los_productos/', views.obtener_todos_los_productos, name='obtener_todos_los_productos'),
    path('obtener_margen_ganancia/', views.obtener_margen_ganancia, name='obtener_margen_ganancia'),
    path('contar_pedidos_en_proceso/', views.contar_pedidos_en_proceso, name='contar_pedidos_en_proceso'),
    path('obtener_usuarios_registrados/', views.obtener_usuarios_registrados, name='obtener_usuarios_registrados'),
    path('obtener_numero_proveedores/', views.obtener_numero_proveedores, name='obtener_numero_proveedores'),
    path('obtener_cantidad_productos/', views.obtener_cantidad_productos, name='obtener_cantidad_productos'),  
    path('obtener_ventas_hechas/', views.obtener_ventas_hechas, name='obtener_ventas_hechas'),
    path('obtener_ventas_productos/', views.obtener_ventas_productos, name='obtener_ventas_productos'),
     path('obtener-ventas-por-producto/', views.obtener_ventas_por_producto, name='obtener_ventas_por_producto'),
]