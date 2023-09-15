from django.urls import path, include 
from . import views 

urlpatterns=[
    path('', views.Home, name='usuarios'),
    path('Estado/', views.cambiarEstadoDeUsuario, name='cambiarEstadoDeUsuario'),
]