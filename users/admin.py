from django.contrib import admin
from .models import Usuarios

admin.site.register(Usuarios)

from .models import Rolespermisos

admin.site.register(Rolespermisos)
