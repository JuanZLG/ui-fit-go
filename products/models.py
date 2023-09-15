from sre_parse import CATEGORIES
from django.db import models



class Marcas(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'marcas'


class Categorias(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'categorias'

class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(Categorias, models.DO_NOTHING, db_column='id_categoria')
    id_marca = models.ForeignKey(Marcas, models.DO_NOTHING, db_column='id_marca')
    nombre_producto = models.CharField(max_length=75)
    descripcion = models.CharField(max_length=400)
    cantidad = models.IntegerField()
    fechaven = models.DateField()
    sabor = models.CharField(max_length=50)
    presentacion = models.CharField(max_length=45)
    estado = models.IntegerField(default=1)
    precio = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'productos'
