from django.urls import path
from . import views 

urlpatterns=[
    path('', views.Home, name='pedidos'),
    path('state_order/', views.cambiarEstadoPedido, name='cambiarEstadoPedido'),
    path('edit_order_home/<int:id_pedido>', views.editarPedidoHome, name='editarPedidoHome'),
    path('edit_order/', views.editarPedido, name='editarPedido'),
    path('details_order/', views.detalles_pedido, name='detallesPedido'),
]