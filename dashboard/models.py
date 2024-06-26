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