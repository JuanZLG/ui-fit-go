from django.db import models

# Create your models here.

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='id_rol')
    correo = models.CharField(max_length=60)
    nombre_usuario = models.CharField(max_length=60)
    contrasena = models.CharField(max_length=250)
    estado = models.IntegerField(default=1)
    
 
    class Meta:
        managed = False
        db_table = 'usuarios'
        
class Permisos(models.Model):
    id_permiso = models.AutoField(primary_key=True)
    clientes = models.IntegerField() 
    usuarios = models.IntegerField()
    proveedores = models.IntegerField()
    productos = models.IntegerField()
    compras = models.IntegerField()
    ventas = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'permisos'

        
class Rolespermisos(models.Model):
    id_rolespermisos = models.AutoField(primary_key=True)
    id_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='id_rol')
    id_permiso = models.ForeignKey('Permisos', models.DO_NOTHING, db_column='id_permiso')

    class Meta:
        managed = False
        db_table = 'rolespermisos'

class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'roles'