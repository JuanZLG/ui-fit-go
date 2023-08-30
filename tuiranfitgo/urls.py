
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/products', include('products.urls')),
    path('admin/eproviders', include('eproviders.urls')),  
]
