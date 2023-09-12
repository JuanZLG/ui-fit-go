from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name= 'lista_clientes'),
    
    path('agregar/', views.agregarCliente, name='agregarCliente'),
    path('agregarClientes/', views.agregarClientePost, name='agregarClientes'),
    path('editarCliente/<int:cliente_id>/', views.editarCliente, name='editarCliente'),
    path('verCliente/<int:cliente_id>/', views.ver_cliente, name='verCliente'),


    path('cambiarEstado/', views.cambiarEstado, name='cambiarEstadoClientes'),




]