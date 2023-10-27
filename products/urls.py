from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)