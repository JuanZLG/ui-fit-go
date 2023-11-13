from django.urls import path, include 
from . import views 
from .views import loginmio
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', loginmio.as_view(), name='login_view'),
    path('verificar-correo/', views.verificar_correo, name='verificar_correo'),
    path('verificar-codigo/', views.verificar_codigo, name='verificar_codigo'),
    path('restablecer-contrasena/', views.restablecer_contrasena, name='restablecer_contrasena'),
]
