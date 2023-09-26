from django.urls import path, include 
from . import views 

urlpatterns=[
    path('', views.Home, name='usuarios'),
    path('Estado/', views.cambiarEstadoDeUsuario, name='cambiarEstadoDeUsuario'),
<<<<<<< HEAD
=======
    path('logout/', views.logout_view, name='logout'),
>>>>>>> d86a451fe320dd7fc709af3a61f76e492cfc14c3
]