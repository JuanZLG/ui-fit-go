# Generated by Django 4.2.6 on 2023-11-06 22:37

from django.db import migrations, models
import django.utils.timezone


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
            name='Detalleventa',
            fields=[
                ('id_detalleventa', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField()),
                ('precio_uni', models.FloatField()),
                ('precio_tot', models.FloatField()),
                ('estado', models.IntegerField(default=1)),
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
            name='Productos',
            fields=[
                ('id_producto', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_producto', models.CharField(max_length=75)),
                ('descripcion', models.CharField(max_length=400)),
                ('cantidad', models.IntegerField()),
                ('sabor', models.CharField(max_length=50)),
                ('presentacion', models.CharField(max_length=45)),
                ('estado', models.IntegerField(default=1)),
                ('precio', models.FloatField()),
                ('iProductImg', models.ImageField(blank=True, null=True, upload_to='landingproducts/products')),
                ('iInfoImg', models.ImageField(blank=True, null=True, upload_to='landingproducts/nutritiondex')),
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
                ('fechareg', models.DateField(default=django.utils.timezone.now)),
                ('estado', models.IntegerField(default=1)),
                ('totalVenta', models.FloatField()),
            ],
            options={
                'db_table': 'ventas',
                'managed': False,
            },
        ),
    ]