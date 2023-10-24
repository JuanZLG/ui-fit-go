from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
# from django.contrib.auth import authenticate, login
# from django.shortcuts import render, redirect
# from django.urls import reverse_lazy
# from django.views import View


# ------------------------------- Intento del 13 de Octubre, errores de relative_name -----------------------------------------

# class CustomUserManager(BaseUserManager):
#     def create_user(self, correo, contrasena, **extra_fields):
#         if not correo:
#             raise ValueError('El correo electrónico es un campo obligatorio.')
#         user = self.model(correo=correo, **extra_fields)
#         user.set_password(contrasena)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, correo, contrasena, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         return self.create_user(correo, contrasena, **extra_fields)

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

# class Usuarios(AbstractUser):
#     correo = models.CharField(max_length=60, unique=True)
#     nombre_usuario = models.CharField(max_length=60)
#     id_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='id_rol', related_name='usuarios_set')
#     estado = models.IntegerField(default=1)
#     contrasena = models.CharField(max_length=50)
    
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     USERNAME_FIELD = 'correo'
#     PASSWORD_FIELD = 'contrasena'

#     def __str__(self):
#         return self.correo, self.contrasena

#     roles = models.ManyToManyField('Roles', related_name='roldeusuario', blank=True)
#     custom_permissions = models.ManyToManyField('Permisos', related_name='permisosdeusuario', blank=True)
    
    
# ---------------------------------Modelo Provisional----------------------------------

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='id_rol')
    correo = models.CharField(max_length=60)
    nombre_usuario = models.CharField(max_length=60)
    contrasena = models.CharField(max_length=50)
    estado = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'usuarios'

# -----------------------------Intento del 18 de Octubre, mismos errores -----------------------------------------

# class CustomUserManager(UserManager):
#     def _create_user(self, email, password, **extra_fields):
#         if not email:
#             raise ValueError("No has proporcionado un correo válido.")
        
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
        
#         return user
    
#     def create_user(self, email=None, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', False)
#         extra_fields.setdefault('is_superuser', False)
        
#         return self._create_user(email, password, **extra_fields)

# class Usuarios(AbstractBaseUser, PermissionsMixin):
#     id_usuario = models.AutoField(primary_key=True)
#     id_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='id_rol')
#     correo = models.CharField(max_length=60)
#     nombre_usuario = models.CharField(max_length=60)
#     contrasena = models.CharField(max_length=50)
#     estado = models.IntegerField(default=1)
#     is_superuser=models.BooleanField(default=False)
#     is_staff=models.BooleanField(default=False)
    
#     object = CustomUserManager()
    
#     USERNAME_FIELD = 'correo'
#     EMAIL_FIELD = 'correo'
#     REQUIRED_FIELDS=[]
    
#     class Meta:
#         verbose_name= 'Usuarios'



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

        
