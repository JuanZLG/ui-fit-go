from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='clientes'),

    
#     path('agregar/', views.agregar_cliente, name='agregar_cliente'),
#     path('agregar_post/', views.agregar_cliente_post, name='agregar_cliente_post'),
#     path('editar_cliente/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
# path('redirigir_editar_cliente/<int:cliente_id>/', views.redirigir_editar_cliente, name='redirigir_editar_cliente'),
# path('Home/cambiar_estado_cliente/<int:cliente_id>/', views.cambiar_estado_cliente, name='cambiar_estado_cliente'),




]
