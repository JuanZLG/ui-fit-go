from django.urls import path, include 
from . import views 
# from django.contrib.auth import views as auth_views

urlpatterns=[
    path('', views.Home, name='usuarios'),
    path('adduser', views.createUser, name="createAUser"),
    path('edituser/<int:id_usuario>/', views.editUser, name='editAUser'),
    path('Estado/', views.cambiarEstadoDeUsuario, name='cambiarEstadoDeUsuario'),
    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('logout/', views.logout_view, name='logout'),
]


