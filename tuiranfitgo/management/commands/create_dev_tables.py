"""Crea en la base actual las tablas de los modelos ``managed = False``.

En produccion esas tablas ya existen en MySQL (los modelos salieron de
``inspectdb``). Este comando permite levantar un entorno de desarrollo o de
pruebas desde cero, por ejemplo con ``DB_ENGINE=sqlite``.

Uso:  python manage.py migrate && python manage.py create_dev_tables
"""
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Crea las tablas de los modelos no gestionados (managed=False) que aun no existan."

    def handle(self, *args, **options):
        existentes = set(connection.introspection.table_names())
        modelos = [
            m for m in apps.get_models(include_auto_created=False)
            if not m._meta.managed and not m._meta.proxy
        ]
        creadas = []
        with connection.schema_editor() as editor:
            for modelo in modelos:
                tabla = modelo._meta.db_table
                if tabla in existentes:
                    continue
                editor.create_model(modelo)
                existentes.add(tabla)
                creadas.append(tabla)
        if creadas:
            self.stdout.write(self.style.SUCCESS(f"Tablas creadas ({len(creadas)}): {', '.join(creadas)}"))
        else:
            self.stdout.write("No habia tablas por crear.")
