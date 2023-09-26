<<<<<<< HEAD

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.generic import RedirectView
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', TemplateView.as_view(template_name='tgoEntrance.html'), name='Entrance'),
=======
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.views.generic import RedirectView

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', TemplateView.as_view(template_name='login.html'), name='login'),
>>>>>>> d86a451fe320dd7fc709af3a61f76e492cfc14c3
    path('admin/dashboard/', include('dashboard.urls')),
    path('admin/users/', include('users.urls')),
    path('admin/products/', include('products.urls')),
    path('admin/providers/', include('eproviders.urls')),  
    path('admin/clients/', include('customers.urls')),  
    path('admin/sales/', include('sales.urls')),  
<<<<<<< HEAD
    path('admin/purchases/', include('purchases.urls')),  
]

=======
    path('admin/purchases/', include('purchases.urls')),
    path('login/', LoginView.as_view(template_name='login.html', success_url='/dashboard/'), name='login_view'),
    path('entrada/', include('dashboard.urls')),
    path('logout/', LogoutView.as_view(), name='logout')
]





>>>>>>> d86a451fe320dd7fc709af3a61f76e492cfc14c3
