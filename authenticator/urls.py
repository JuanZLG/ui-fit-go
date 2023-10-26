from django.urls import path, include 
from . import views 
from .views import loginmio


urlpatterns = [
    path('', loginmio.as_view(), name='login_view'),
]
