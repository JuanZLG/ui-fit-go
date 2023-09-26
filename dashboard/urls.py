from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 


urlpatterns=[
<<<<<<< HEAD
    path('', views.Home, name="mydashboard"),
]
=======
    path('', views.Entrance, name="entrada"),
    path('dashboard/', views.Home, name='mydashboard')
]
>>>>>>> d86a451fe320dd7fc709af3a61f76e492cfc14c3
