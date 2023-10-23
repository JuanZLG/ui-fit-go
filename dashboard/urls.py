from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 


urlpatterns=[
    path('', views.Entrance, name="entrada"),
    path('dashboard/', views.Home, name='mydashboard'),
    path('guide/', views.UserGuide, name="guideser"),
    path('contar_clientes_activos/', views.contar_clientes_activos, name='contar_clientes_activps'),
    path('calcular_total_compras/', views.calcular_total_compras, name='calcular_total_compras'),
    path('calcular_total_ventas/', views.calcular_total_ventas, name='calcular_total_ventas'),
    path('obtener_datos_ventas_y_compras/', views.obtener_datos_ventas_y_compras, name='obtener_datos_ventas_y_compras'),
    path('obtener_top_productos/', views.obtener_top_productos, name='obtener_top_productos'),






]
