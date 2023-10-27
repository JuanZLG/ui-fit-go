from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('Brutality/', include('page.urls')),
    path('', include('authenticator.urls')),
    path('admin/home/', include('dashboard.urls')),
    path('admin/users/', include('users.urls')),
    path('admin/products/', include('products.urls')),
    path('admin/providers/', include('eproviders.urls')),  
    path('admin/clients/', include('customers.urls')),  
    path('admin/sales/', include('sales.urls')),  
    path('admin/purchases/', include('purchases.urls')),
    path('error/', views.error_view, name="initerror")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


