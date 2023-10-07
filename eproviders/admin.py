from django.contrib import admin
from .models import Proveedores
from django.contrib.auth.models import User

# admin.site.unregister(User)  # Desregistra el modelo User de la interfaz de administración

# Register your models here. Registrar modelo para administrar
admin.site.register(Proveedores)