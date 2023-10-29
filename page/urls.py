from django.urls import path, include 
from . import views 

urlpatterns=[
    path('', views.Home, name='pageHome'),
    path('Detalles/', views.pageDetails, name="pageDetails"),
    
]

