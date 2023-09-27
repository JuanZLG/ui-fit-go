from django.urls import path, include  # Funciones de manejo de rutas y urls
from . import views 


urlpatterns=[
    path('', views.Entrance, name="entrada"),
    path('dashboard/', views.Home, name='mydashboard')
]
