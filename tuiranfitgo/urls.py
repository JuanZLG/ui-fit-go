from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', include('dashboard.urls')),
    path('admin/users/', include('users.urls')),
    path('admin/products/', include('products.urls')),
    path('admin/providers/', include('eproviders.urls')),  
    path('admin/clients/', include('customers.urls')),  
    path('admin/sales/', include('sales.urls')),  
    path('admin/purchases/', include('purchases.urls')),
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    path('login/', LoginView.as_view(template_name='login.html', success_url='/dashboard/'), name='login_view'),
    path('mydashboard/', include('dashboard.urls')),
    path('logout/', LogoutView.as_view(), name='logout')
]





