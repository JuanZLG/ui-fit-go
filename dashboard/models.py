from django.db import models

class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    documento = models.CharField(max_length=25)
    nombres = models.CharField(max_length=60)
    apellidos = models.CharField(max_length=60)
    estado = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'clientes'

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone

class Categorias(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'categorias'


class Compras(models.Model):
    id_compra = models.AutoField(primary_key=True)
    id_proveedor = models.ForeignKey('Proveedores', models.DO_NOTHING, db_column='id_proveedor')
    fechareg = models.DateField(default=timezone.now)
    estado = models.IntegerField(default=1) 
    totalCompra = models.FloatField()


    class Meta:
        managed = False
        db_table = 'compras'


class Detallecompra(models.Model):
    id_detallecompra = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey('Productos', models.DO_NOTHING, db_column='id_producto')
    id_compra = models.ForeignKey(Compras, models.DO_NOTHING, db_column='id_compra')
    cantidad = models.IntegerField()
    precio_uni = models.FloatField()
    precio_tot = models.FloatField()
    estado = models.IntegerField(default=1)


    class Meta:
        managed = False
        db_table = 'detallecompra'


class Marcas(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'marcas'








class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(Categorias, models.DO_NOTHING, db_column='id_categoria')
    id_marca = models.ForeignKey(Marcas, models.DO_NOTHING, db_column='id_marca')
    nombre_producto = models.CharField(max_length=75)
    descripcion = models.CharField(max_length=1000)
    cantidad = models.IntegerField()
    fechaven = models.DateTimeField()
    sabor = models.CharField(max_length=50)
    presentacion = models.CharField(max_length=45)
    estado = models.IntegerField()
    precio = models.FloatField()


    class Meta:
        managed = False
        db_table = 'productos'


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
        managed = False
        db_table = 'proveedores'




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



                