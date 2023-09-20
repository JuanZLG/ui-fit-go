from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns=[
    path('', views.Home, name='productos'), 
    path('addproduct/', views.createProduct, name="createAProduct"),
    path('editproduct/<int:id_producto>/', views.editProduct, name='editAProduct'),
    path('Estado/', views.cambiarEstadoDeProducto, name='cambiarEstadoDeProducto'),
    path('details/', views.verDetallesProducto, name='verDetallesProducto'),
    path('categories/', views.catHome, name="categorias"),
    path('brands', views.brandHome, name="marcas")
]
