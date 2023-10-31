from django.urls import path, include 
from . import views 

urlpatterns=[
    path('', views.Home, name='pageHome'),
    path('Detalles/', views.pageDetails, name="pageDetails"),
    path('Detalles/=', views.filter_products, name="filter_products"),
    path('Detalles/?', views.search_products, name="search_products"),
]

