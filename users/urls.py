from django.urls import path, include 
from . import views 

urlpatterns=[
    path('', views.Home, name='usuarios'),
    path('adduser', views.createUser, name="createAUser"),
    path('edituser/<int:id_usuario>/', views.editUser, name='editAUser'),
    path('Estado/', views.cambiarEstadoDeUsuario, name='cambiarEstadoDeUsuario'),
    path('Roles/', views.HomeRoles, name='HomeRoles'), 
    path('edit_rol/', views.edit_rol, name="edit_rol"),
    path('create_rol/', views.create_rol, name="create_rol"),
    path('obtener_datos/', views.obtener_datos, name='obtener_datos'),
    path('ver_detalles_usuario', views.verDetallesUsuario, name='ver_detalles_usuario'),
    path('rol_unico/', views.rol_unico, name='rol_unico'),
    path('email_unique/', views.email_unique, name='email_unique'),
    path('remove/', views.eliminar_rol, name='eliminarRol'),
    path('profile/', views.UserProfile, name="myProfile"),
    path('changepsw/', views.change_password, name='changepsw'),

]

