from django.db import models


class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    id_municipio = models.ForeignKey('Municipios', models.DO_NOTHING, db_column='id_municipio')
    documento = models.CharField(max_length=25)
    nombres = models.CharField(max_length=60)
    apellidos = models.CharField(max_length=60)
    celular = models.CharField(max_length=10)
    barrio = models.CharField(max_length=40)
    direccion = models.CharField(max_length=50)
    estado = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'clientes'



class Detalleventa(models.Model):
    id_detalleventa = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey('Productos', models.DO_NOTHING, db_column='id_producto')
    id_venta = models.ForeignKey('Ventas', models.DO_NOTHING, db_column='id_venta')
    cantidad = models.IntegerField()
    precio_uni = models.DecimalField(max_digits=10, decimal_places=0)
    precio_tot = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'detalleventa'


class Ventas(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='id_cliente')
    fechareg = models.DateTimeField()
    estado = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ventas'
