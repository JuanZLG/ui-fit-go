
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.generic import RedirectView
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/', permanent=True)),
    path('admin/', TemplateView.as_view(template_name='baseInterface.html'), name='base-interface'),
    path('admin/products/', include('products.urls')),
    path('admin/providers/', include('eproviders.urls')),  
    # path('admin/clients/', include('eclients.urls')),  

]
