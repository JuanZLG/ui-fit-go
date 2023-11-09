from django.urls import path, include 
from . import views 
from .views import loginmio
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', loginmio.as_view(), name='login_view'),
    path('enviar-codigo/', views.enviar_codigo, name='enviar_codigo'),
    path('olvide-contrasena/', views.olvide_contrasena, name='olvide_contrasena'),
    path('verificar-codigo/', views.verificar_codigo, name='verificar_codigo'),
    path('restablecer-contrasena/', views.restablecer_contrasena, name='restablecer_contrasena'),
]
