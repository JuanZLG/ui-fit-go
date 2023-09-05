
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.generic import RedirectView
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('admin', include('dashboard.urls')),
    path('admin/products/', include('products.urls')),
    path('admin/providers/', include('eproviders.urls')),  
    path('admin/clients/', include('customers.urls')),  
    path('admin/sales/', include('sales.urls')),  
]

