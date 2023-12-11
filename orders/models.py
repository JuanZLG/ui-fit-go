from django.db import models
from django.utils import timezone


        
        
class Pedidos(models.Model):
    ESTADO_CHOICES = [
        ('cancelado', 'Cancelado'),
        ('en proceso', 'En Proceso'),
        ('confirmado', 'Confirmado'),
    ]
    id_pedido = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey('Ventas', models.DO_NOTHING, db_column='id_venta')
    id_cliente = models.ForeignKey('Clientes', models.DO_NOTHING, db_column='id_cliente')
    fecha_pedido = models.DateField(default=timezone.now)
    total_pedido = models.FloatField()
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES)
    class Meta:
        managed = False
        db_table = 'pedidos'

class DetallePedido(models.Model):
    id_detallepedido = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey('Pedidos', models.DO_NOTHING, db_column='id_pedido')
    id_producto = models.ForeignKey('Productos', models.DO_NOTHING, db_column='id_producto')
    sabor = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    precio_uni = models.FloatField()
    precio_tot = models.FloatField()
    class Meta:
        managed = False
        db_table = 'detallepedido'


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
    sabor = models.CharField(max_length=50)
    presentacion = models.CharField(max_length=45)
    precio_pub = models.FloatField()
    iProductImg = models.BinaryField(null=True, blank=True)
    estado = models.IntegerField(default=1)

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
    descuentoVenta = models.CharField(max_length=255)
    totalVentaDescuento = models.CharField(max_length=255)
    totalVenta = models.FloatField()
    estado = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'ventas'
