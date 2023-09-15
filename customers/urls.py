from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name= 'Clientes'),
    
    path('agregar/', views.agregarCliente, name='agregarCliente'),
    path('agregarClientes/', views.agregarClientePost, name='agregarClientes'),
    path('editarCliente/<int:cliente_id>/', views.editarCliente, name='editarCliente'),
    path('ver_detalles_cliente/', views.verDetallesCliente, name='ver_detalles_cliente'),



    path('cambiarEstado/', views.cambiarEstado, name='cambiarEstadoClientes'),




]