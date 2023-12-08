from django.urls import path, include 
from . import views 

urlpatterns=[
    path('', views.Home, name='pedidos'),
    path('Estado_pedido/', views.cambiarEstadoPedido, name='cambiarEstadoPedido'),
    path('Editar_pedido/<int:id_pedido>', views.editarPedido, name='editarPedido'),

]

