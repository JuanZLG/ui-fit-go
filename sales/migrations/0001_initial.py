# Generated by Django 4.2.4 on 2023-09-05 19:32

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
            name='Productos',
            fields=[
                ('id_producto', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_producto', models.CharField(max_length=75)),
                ('descripcion', models.CharField(max_length=400)),
                ('cantidad', models.IntegerField()),
                ('sabor', models.CharField(max_length=50)),
                ('tamaño', models.CharField(max_length=45)),
                ('estado', models.IntegerField()),
                ('precio', models.DecimalField(decimal_places=3, max_digits=10)),
            ],
            options={
                'db_table': 'productos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Ventas',
            fields=[
                ('id_venta', models.AutoField(primary_key=True, serialize=False)),
                ('fechareg', models.DateTimeField()),
                ('estado', models.IntegerField()),
            ],
            options={
                'db_table': 'ventas',
                'managed': False,
            },
        ),
    ]
