"""Tablas propias de la app (a diferencia del resto del proyecto, estas SÍ las gestiona Django).

Se crean con:  python manage.py migrate control
o a mano con control/sql/control_mysql.sql
"""
import json

from django.db import models
from django.utils import timezone


class RegistroAuditoria(models.Model):
    """Quién hizo qué y cuándo. Los registros no se editan ni se borran desde la aplicación."""
    fecha = models.DateTimeField(default=timezone.now, db_index=True)
    usuario_nombre = models.CharField(max_length=80, blank=True)
    usuario_correo = models.CharField(max_length=120, blank=True, db_index=True)
    rol_id = models.IntegerField(null=True, blank=True)
    ip = models.CharField(max_length=45, blank=True)
    accion = models.CharField(max_length=30, db_index=True)
    modulo = models.CharField(max_length=30, db_index=True)
    objeto = models.CharField(max_length=60, blank=True)
    objeto_id = models.CharField(max_length=40, blank=True)
    descripcion = models.CharField(max_length=300)
    cambios = models.TextField(blank=True)          # JSON: [{"campo": ..., "antes": ..., "despues": ...}]

    class Meta:
        ordering = ['-fecha', '-id']
        verbose_name = 'registro de auditoría'
        verbose_name_plural = 'registros de auditoría'

    def __str__(self):
        return f'{self.fecha:%Y-%m-%d %H:%M} {self.usuario_nombre} {self.accion} {self.objeto}'

    @property
    def cambios_lista(self):
        try:
            return json.loads(self.cambios) if self.cambios else []
        except ValueError:
            return []


class MetaVentas(models.Model):
    """Meta de ventas de un mes (una por año y mes)."""
    anio = models.PositiveSmallIntegerField()
    mes = models.PositiveSmallIntegerField()
    valor = models.BigIntegerField()
    definida_por = models.CharField(max_length=120, blank=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('anio', 'mes')
        verbose_name = 'meta de ventas'
        verbose_name_plural = 'metas de ventas'

    def __str__(self):
        return f'{self.anio}-{self.mes:02d}: {self.valor}'
