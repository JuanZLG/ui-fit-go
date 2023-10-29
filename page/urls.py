from django.urls import path, include 
from . import views 

urlpatterns=[
    path('', views.Home, name='pageHome'),
    path('Catalogo/', views.pageCatalog, name="pageCatalog"),
    # path('Detalles/', views.createUser, name="pageDetails"),

]

