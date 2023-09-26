from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns=[
    path('', views.Home, name='productos'), 
    path('addproduct/', views.createProduct, name="createAProduct"),
    path('createcategory/', views.crear_categoria, name='create_category'),
    # path('producto_unico/', views.producto_unico, name='producto_unico'),
    path('editproduct/<int:id_producto>/', views.editProduct, name='editAProduct'),
    path('Estado/', views.cambiarEstadoDeProducto, name='cambiarEstadoDeProducto'),
    path('details/', views.verDetallesProducto, name='verDetalleDeProducto'),
    path('categories/', views.catHome, name="categorias"),
    path('brands/', views.brandHome, name="marcas")
]
