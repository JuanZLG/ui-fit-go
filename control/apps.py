from django.apps import AppConfig


class ControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control'
    verbose_name = 'Control y auditoría'

    def ready(self):
        from . import auditoria
        auditoria.conectar_senales()
