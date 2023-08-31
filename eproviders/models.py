from django.db import models
from django.core.exceptions import ValidationError

class Proveedores(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre_proveedor = models.CharField(max_length=65)
    telefono = models.CharField(max_length=10)
    correo = models.CharField(max_length=65)
    estado = models.IntegerField(default=True)
    class Meta:
        managed = True
        db_table = 'proveedores'
    

# Clase META -> Proporciona metadatos y configuración específica para un modelo
# MANAGED -> Si django debe administra (crear, modificar, eliminar) la tabla en la base de datos (True) o si manualmente (False)