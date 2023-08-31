from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name= 'lista_clientes'),
    
    path('agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('agregar_post/', views.agregar_cliente_post, name='agregar_cliente_post'),
    path('editar_cliente/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),

    path('redirigir_editar_cliente/<int:cliente_id>/', views.redirigir_editar_cliente, name='redirigir_editar_cliente'),
    path('cambiar_estado_cliente_ajax/', views.cambiar_estado_cliente_ajax, name='cambiar_estado_cliente_ajax'),




]