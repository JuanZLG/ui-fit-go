from django.db import models
from django.core.exceptions import ValidationError

class Proveedores(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre_proveedor = models.CharField(max_length=65)
    telefono = models.CharField(max_length=10)
    correo = models.CharField(max_length=65)
    direccion = models.CharField(max_length=50)
    informacion_adicional = models.TextField()
    tipo_documento = models.CharField(max_length=50)
    numero_documento_nit = models.CharField(max_length=50)
    estado = models.IntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'proveedores'