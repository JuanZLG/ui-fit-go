from django.urls import path, include 
from . import views 
from django.contrib.auth import views as auth_views
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('', views.Home, name='usuarios'),
    path('adduser', views.createUser, name="createAUser"),
    path('edituser/<int:id_usuario>/', views.editUser, name='editAUser'),
    path('Estado/', views.cambiarEstadoDeUsuario, name='cambiarEstadoDeUsuario'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('Roles/', views.HomeRoles, name='HomeRoles'), 
    path('action-rol/', views.accion_rol, name="accion_rol"),
    path('obtener_datos/', views.obtener_datos, name='obtener_datos'),
    path('ver_detalles_usuario', views.verDetallesUsuario, name='ver_detalles_usuario'),
    path('rol_unico/', views.rol_unico, name='rol_unico'),
    path('remove/', views.eliminar_rol, name='eliminarRol'),
]

