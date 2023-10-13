from django.db import models
from django.utils import timezone


class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    documento = models.CharField(max_length=25)
    nombres = models.CharField(max_length=60)
    apellidos = models.CharField(max_length=60)
    estado = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'clientes'

class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=75)
    cantidad = models.IntegerField()
    precio = models.FloatField()
    estado = models.IntegerField(default=1)  
    
    class Meta:
        managed = False
        db_table = 'productos'


class Detalleventa(models.Model):
    id_detalleventa = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey('Productos', models.DO_NOTHING, db_column='id_producto')
    id_venta = models.ForeignKey('Ventas', models.DO_NOTHING, db_column='id_venta')
    cantidad = models.IntegerField()
    precio_uni = models.FloatField()
    precio_tot = models.FloatField()
    estado = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'detalleventa'

class Ventas(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='id_cliente')
    fechareg = models.DateField(default=timezone.now)
    estado = models.IntegerField(default=1)
    totalVenta = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ventas'