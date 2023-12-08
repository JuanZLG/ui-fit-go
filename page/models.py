from django.db import models
from django.utils import timezone

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
    
    iProductImg = models.ImageField(upload_to="landingproducts/products", null=True, blank=True)
    iInfoImg = models.ImageField(upload_to="landingproducts/nutritiondex", null=True, blank=True)

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
    fechareg = models.DateField(default=timezone.now)
    estado = models.IntegerField(default=1)
    totalVenta = models.FloatField()
    class Meta:
        managed = False
        db_table = 'ventas'


class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    id_municipio = models.ForeignKey('Municipios', models.DO_NOTHING, db_column='id_municipio')
    documento = models.CharField(max_length=25, unique=True)  
    nombres = models.CharField(max_length=60)
    apellidos = models.CharField(max_length=60)
    celular = models.CharField(max_length=15)
    barrio = models.CharField(max_length=40)
    direccion = models.CharField(max_length=50)
    estado = models.IntegerField(default=1)
    correo = models.CharField(max_length=60)

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
    presentacion = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    precio_uni = models.FloatField()
    precio_tot = models.FloatField()
    class Meta:
        managed = False
        db_table = 'detallepedido'



