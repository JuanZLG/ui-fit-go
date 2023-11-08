
from django.db import models
from django.utils import timezone
from products.models import Productos

class Notification(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Marcas(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'marcas'
        app_label = 'tuiranfitgo'


class Categorias(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'categorias'
        app_label = 'tuiranfitgo'

class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(Categorias, models.DO_NOTHING, db_column='id_categoria')
    id_marca = models.ForeignKey(Marcas, models.DO_NOTHING, db_column='id_marca')
    nombre_producto = models.CharField(max_length=75)
    descripcion = models.CharField(max_length=400)
    cantidad = models.IntegerField()
    fechaven = models.DateTimeField()
    sabor = models.CharField(max_length=50)
    presentacion = models.CharField(max_length=45)
    estado = models.IntegerField(default=1)
    precio = models.FloatField()
    
    iProductImg = models.ImageField(upload_to="landingproducts/products", null=True, blank=True)
    iInfoImg = models.ImageField(upload_to="landingproducts/nutritiondex", null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'productos'
        app_label = 'tuiranfitgo'
        
from django.db import models
from django.utils import timezone
from products.models import Productos

class Notification(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
