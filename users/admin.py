from django.contrib import admin
from .models import Usuarios

# Register your models here.

admin.site.register(Usuarios)

from .models import Rolespermisos

admin.site.register(Rolespermisos)
