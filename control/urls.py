from django.urls import path

from . import views

urlpatterns = [
    path('', views.auditoria, name='auditoria'),
    path('reciente/', views.actividad_reciente, name='auditoria_reciente'),
    path('meta/', views.meta_actual, name='meta_ventas'),
    path('meta/guardar/', views.guardar_meta, name='guardar_meta'),
]
