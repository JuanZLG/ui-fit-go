from django.urls import path
from . import views
from django.conf import settings


urlpatterns=[
    path('', views.Home, name='productos'), 
    path('addproduct/', views.createProduct, name="createAProduct"),
    path('createcategory/', views.crear_categoria, name='create_category'),
    path('createbrand/', views.crear_marca, name='create_brand'),
    path('removebrand/', views.eliminar_marca, name='borrarMarca'),
    path('removecategory/', views.eliminar_categoria, name='borrarCategoria'),
    path('editproduct/<int:id_producto>/', views.editProduct, name='editAProduct'),
    path('Estado/', views.cambiarEstadoDeProducto, name='cambiarEstadoDeProducto'),
    path('details/', views.verDetallesProducto, name='verDetalleDeProducto'),
    path('categories/', views.catHome, name="categorias"),
    path('brands/', views.brandHome, name="marcas")
]