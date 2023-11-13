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
    fechaven = models.DateTimeField()
    sabor = models.CharField(max_length=50)
    presentacion = models.CharField(max_length=45)
    estado = models.IntegerField(default=1)
    precio = models.FloatField()
    precio_pub = models.FloatField()
    
    iProductImg = models.BinaryField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'productos'

class Detalleventa(models.Model):
    id_detalleventa = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey('Productos', models.DO_NOTHING, db_column='id_producto')
    id_venta = models.ForeignKey('Ventas', models.DO_NOTHING, db_column='id_venta')
    cantidad = models.IntegerField()
    precio_compra = models.FloatField()
    precio_venta = models.FloatField()
    descuentoProducto = models.CharField(max_length=255)
    totalProductoDescuento = models.CharField(max_length=255)
    margenGanancia = models.FloatField()    
    precio_tot = models.FloatField()    
    estado = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'detalleventa'

class Ventas(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='id_cliente')
    fechareg = models.DateField(default=timezone.now)
    descuentoVenta = models.CharField(max_length=255)
    totalVentaDescuento = models.CharField(max_length=255)
    totalVenta = models.FloatField()
    margenGanancia = models.FloatField()    
    estado = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'ventas'
