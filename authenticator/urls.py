from django.urls import path, include 
from . import views 
from .views import loginmio
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', loginmio.as_view(), name='login_view'),
    path('olvide-contrasena/', views.olvide_contrasena, name='olvide_contrasena'),
    path('olvide-contrasena-exito/', views.olvide_contrasena_exito, name='olvide_contrasena_exito'),
]
