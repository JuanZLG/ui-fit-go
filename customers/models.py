from django.db import models

from django.db import models
class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    id_municipio = models.ForeignKey('Municipios', models.CASCADE, db_column='id_municipio')
    documento = models.CharField(max_length=25)
    nombres = models.CharField(max_length=60)
    apellidos = models.CharField(max_length=60)
    celular = models.CharField(max_length=15)
    barrio = models.CharField(max_length=40)
    direccion = models.CharField(max_length=50)
    estado = models.BooleanField()
    correo = models.EmailField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'clientes'

class Departamentos(models.Model):
    id_departamento = models.AutoField(primary_key=True)
    nombre_departamento = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'departamentos'

class Municipios(models.Model):
    id_municipio = models.AutoField(primary_key=True)
    id_departamento = models.ForeignKey(Departamentos, models.DO_NOTHING, db_column='id_departamento')
    nombre_municipio = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'municipios'