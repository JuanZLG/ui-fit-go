from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name= 'Clientes'),
    path('agregar/', views.agregarCliente, name='agregarCliente'),
    path('agregarClientes/', views.agregarClientePost, name='agregarClientes'),
    path('editarCliente/<int:cliente_id>/', views.editarCliente, name='editarCliente'),
    path('ver_detalles_cliente/', views.verDetallesCliente, name='ver_detalles_cliente'),
<<<<<<< HEAD


    path('verificar_documento/', views.verificar_documento, name='verificar_documento'),

    path('cambiarEstado/', views.cambiarEstado, name='cambiarEstadoClientes'),




=======
    path('verificar_documento/', views.verificar_documento, name='verificar_documento'),
    path('cambiarEstado/', views.cambiarEstado, name='cambiarEstadoClientes'),
>>>>>>> d86a451fe320dd7fc709af3a61f76e492cfc14c3
]