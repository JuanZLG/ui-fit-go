from django.db import models

class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey('Categorias', models.DO_NOTHING, db_column='id_categoria')
    id_marca = models.ForeignKey('Marcas', models.DO_NOTHING, db_column='id_marca')
    nombre_producto = models.CharField(max_length=75)
    descripcion = models.CharField(max_length=1000)
    cantidad = models.PositiveIntegerField()
    fechaven = models.DateField()
    sabor = models.CharField(max_length=50)
    presentacion = models.CharField(max_length=45)
    precio = models.DecimalField(max_digits=10, decimal_places=3)
    estado = models.PositiveIntegerField(default=True)

    class Meta:
        managed = False
        db_table = 'productos'
    
class Categorias(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'categorias'
    

class Marcas(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'marcas'
