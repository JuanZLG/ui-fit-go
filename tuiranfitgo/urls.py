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
    # path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('', include('authenticator.urls')),
    path('Brutality/', include('page.urls')),
    path('admin/home/', include('dashboard.urls')),
    path('admin/users/', include('users.urls')),
    path('admin/products/', include('products.urls')),
    path('admin/providers/', include('eproviders.urls')),  
    path('admin/clients/', include('customers.urls')),  
    path('admin/sales/', include('sales.urls')),  
    path('admin/purchases/', include('purchases.urls')),
    path('error/', views.error_view, name="initerror"),
    path('unauthorized/', views.mixin_view, name="mixint"),
    path('logout/', views.logout_view, name='logout'),
    path('verificar-notificaciones/', views.verificar_notificaciones, name='verificar_notificaciones'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)