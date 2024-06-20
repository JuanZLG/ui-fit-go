from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Permisos',
            fields=[
                ('id_permiso', models.AutoField(primary_key=True, serialize=False)),
                ('clientes', models.IntegerField()),
                ('usuarios', models.IntegerField()),
                ('proveedores', models.IntegerField()),
                ('productos', models.IntegerField()),
                ('compras', models.IntegerField()),
                ('ventas', models.IntegerField()),
            ],
            options={
                'db_table': 'permisos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('id_rol', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_rol', models.CharField(max_length=40)),
            ],
            options={
                'db_table': 'roles',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Rolespermisos',
            fields=[
                ('id_rolespermisos', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'rolespermisos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Usuarios',
            fields=[
                ('id_usuario', models.AutoField(primary_key=True, serialize=False)),
                ('correo', models.CharField(max_length=60)),
                ('nombre_usuario', models.CharField(max_length=60)),
                ('contrasena', models.CharField(max_length=50)),
                ('estado', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'usuarios',
                'managed': False,
            },
        ),
    ]