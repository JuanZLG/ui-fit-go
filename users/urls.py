from django.urls import path, include 
from . import views 

urlpatterns=[
    path('', views.Home, name='usuarios'),
    path('adduser/', views.createUser, name="createUser"),
    path('Estado/', views.cambiarEstadoDeUsuario, name='cambiarEstadoDeUsuario'),
]