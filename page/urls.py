from django.urls import path, include 
from . import views 

urlpatterns=[
    path('', views.Home, name='pageHome'),
    path('Detalles/', views.pageDetails, name="pageDetails"),
    path('mas_vendidos/', views.mas_vendidos, name="mas_vendidos"),
    path('Detalles/=', views.filter_products, name="filter_products"),
    path('Detalles/?', views.search_products, name="search_products"),
    path('añadir_pedido/<int:id_producto>/', views.añadir_pedido, name='añadir_pedido'),
    path('ver_pedido/', views.ver_pedido, name='pageOrder'),

]

