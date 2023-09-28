# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser

class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=37)

    class Meta:
        managed = False
        db_table = 'roles'

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='id_rol')
    correo = models.CharField(max_length=60)
    nombre_usuario = models.CharField(max_length=60)
    contrasena = models.CharField(max_length=50)
    estado = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarios'
    
    
    # user_permissions = models.ManyToManyField(
    #     Permisos,
    #     verbose_name=('user permissions'),
    #     blank=True,
    #     related_name='usuarios',
    #     related_query_name='usuario',
    # )

class Permisos(models.Model):
    id_permiso = models.AutoField(primary_key=True)
    nombre_permiso = models.CharField(max_length=37)

    class Meta:
        managed = False
        db_table = 'permisos'


class Rolespermisos(models.Model):
    id_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='id_rol')
    id_permiso = models.ForeignKey('Permisos', models.DO_NOTHING, db_column='id_permiso')

    class Meta:
        managed = False
        db_table = 'rolespermisos'
