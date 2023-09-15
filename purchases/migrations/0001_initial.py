# Generated by Django 4.2.4 on 2023-09-14 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categorias',
            fields=[
                ('id_categoria', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_categoria', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'categorias',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Clientes',
            fields=[
                ('id_cliente', models.AutoField(primary_key=True, serialize=False)),
                ('documento', models.CharField(max_length=25)),
                ('nombres', models.CharField(max_length=60)),
                ('apellidos', models.CharField(max_length=60)),
                ('celular', models.CharField(max_length=10)),
                ('barrio', models.CharField(max_length=40)),
                ('direccion', models.CharField(max_length=50)),
                ('estado', models.IntegerField()),
            ],
            options={
                'db_table': 'clientes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Compras',
            fields=[
                ('id_compra', models.AutoField(primary_key=True, serialize=False)),
                ('fechareg', models.DateTimeField(auto_now_add=True)),
                ('estado', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'compras',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Departamentos',
            fields=[
                ('id_departamento', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_departamento', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'departamentos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Detallecompra',
            fields=[
                ('id_detallecompra', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField()),
                ('precio_uni', models.DecimalField(decimal_places=0, max_digits=10)),
                ('precio_tot', models.DecimalField(decimal_places=0, max_digits=10)),
            ],
            options={
                'db_table': 'detallecompra',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Detalleventa',
            fields=[
                ('id_detalleventa', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField()),
                ('precio_uni', models.DecimalField(decimal_places=0, max_digits=10)),
                ('precio_tot', models.DecimalField(decimal_places=0, max_digits=10)),
            ],
            options={
                'db_table': 'detalleventa',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Marcas',
            fields=[
                ('id_marca', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_marca', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'marcas',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Municipios',
            fields=[
                ('id_municipio', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_municipio', models.CharField(max_length=60)),
            ],
            options={
                'db_table': 'municipios',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Permisos',
            fields=[
                ('id_permiso', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_permiso', models.CharField(max_length=37)),
            ],
            options={
                'db_table': 'permisos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Productos',
            fields=[
                ('id_producto', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_producto', models.CharField(max_length=75)),
                ('descripcion', models.CharField(max_length=1000)),
                ('cantidad', models.IntegerField()),
                ('fechaven', models.DateTimeField()),
                ('sabor', models.CharField(max_length=50)),
                ('presentacion', models.CharField(max_length=45)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('estado', models.IntegerField()),
            ],
            options={
                'db_table': 'productos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Proveedores',
            fields=[
                ('id_proveedor', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_proveedor', models.CharField(max_length=65)),
                ('telefono', models.CharField(max_length=10)),
                ('correo', models.CharField(max_length=65)),
                ('estado', models.IntegerField()),
            ],
            options={
                'db_table': 'proveedores',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('id_rol', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_rol', models.CharField(max_length=37)),
            ],
            options={
                'db_table': 'roles',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Rolespermisos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('contrasena', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'usuarios',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Ventas',
            fields=[
                ('id_venta', models.AutoField(primary_key=True, serialize=False)),
                ('fechareg', models.DateTimeField()),
                ('estado', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ventas',
                'managed': False,
            },
        ),
    ]