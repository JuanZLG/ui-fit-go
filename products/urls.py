from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 

urlpatterns=[
    path('', views.Home, name='productos'), 
    path('addproduct/', views.createProduct, name="createAProduct"),
    path('createcategory/', views.crear_categoria, name='create_category'),
    # path('editcategory/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('createbrand/', views.crear_marca, name='create_brand'),
    path('removecategory/<int:id_categoria>/', views.eliminar_categoria, name='borrarCategoria'),
    path('editproduct/<int:id_producto>/', views.editProduct, name='editAProduct'),
    path('Estado/', views.cambiarEstadoDeProducto, name='cambiarEstadoDeProducto'),
    path('details/', views.verDetallesProducto, name='verDetalleDeProducto'),
    path('categories/', views.catHome, name="categorias"),
    path('brands/', views.brandHome, name="marcas")
]
