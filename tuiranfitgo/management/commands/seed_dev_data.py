"""Carga datos de ejemplo para desarrollo (usuario admin, catalogo, ventas...).

Uso:
    python manage.py migrate
    python manage.py create_dev_tables
    python manage.py seed_dev_data

Usuario de prueba:  admin@tuiranfit.test  /  admin123
Es idempotente: si ya hay usuarios no vuelve a cargar nada.
NO usar contra la base de produccion.
"""
import random
import re
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from authenticator.security import hashear
from customers.models import Clientes, Departamentos, Municipios
from eproviders.models import Proveedores
from products.models import Categorias, Marcas, Productos
from purchases.models import Compras, Detallecompra
from sales.models import DetallePedido, Detalleventa, Pedidos, Ventas
from ._seed_images import (RED, RED_BRIGHT, RED_DEEP, guardar_imagen_producto,
                           guardar_tabla_nutricional)
from users.models import Permisos, Roles, Rolespermisos, Usuarios


class Command(BaseCommand):
    help = "Carga datos de ejemplo para desarrollo local."

    @transaction.atomic
    def handle(self, *args, **options):
        if Usuarios.objects.exists():
            self.stdout.write("Ya hay datos, no se carga nada.")
            return

        rnd = random.Random(7)
        from control import contexto
        contexto.fijar(silencio=True)         # la carga masiva no se audita
        ahora = timezone.now()

        # --- Roles, permisos y usuarios ---
        admin = Roles.objects.create(nombre_rol="Administrador")
        Roles.objects.create(nombre_rol="Vendedor")
        permisos = Permisos.objects.create(
            clientes=1, usuarios=1, proveedores=1, productos=1, compras=1, ventas=1
        )
        Rolespermisos.objects.create(id_rol=admin, id_permiso=permisos)
        Usuarios.objects.create(
            id_rol=admin, correo="admin@tuiranfit.test",
            nombre_usuario="Admin", contrasena=hashear("admin123"), estado=1,
        )

        # --- Catalogo ---
        categorias = [Categorias.objects.create(nombre_categoria=n) for n in
                      ("Proteinas", "Creatinas", "Pre-entrenos", "Aminoacidos", "Accesorios")]
        marcas = [Marcas.objects.create(nombre_marca=n) for n in
                  ("Optimum Nutrition", "MuscleTech", "Dymatize", "BSN", "Universal")]
        catalogo = [
            ("Whey Gold Standard 5lb", 0, 0, "Chocolate", "5 lb", 18, 185000, 239000),
            ("ISO100 Hydrolyzed 3lb", 0, 2, "Vainilla", "3 lb", 9, 160000, 210000),
            ("Creatina Monohidratada 300g", 1, 1, "Sin sabor", "300 g", 24, 62000, 89000),
            ("NO-Xplode Pre-Workout", 2, 3, "Fruit Punch", "30 serv", 4, 98000, 135000),
            ("BCAA 2:1:1 Powder", 3, 4, "Sandia", "400 g", 12, 54000, 79000),
            ("Mass Tech Extreme 2000", 0, 1, "Fresa", "6 lb", 3, 175000, 229000),
            ("Glutamina Micronizada", 3, 0, "Sin sabor", "300 g", 15, 58000, 82000),
            ("Shaker Pro 700ml", 4, 4, "N/A", "1 und", 40, 12000, 24000),
            ("Cinturon Lumbar Cuero", 4, 4, "N/A", "1 und", 7, 55000, 89000),
            ("C4 Original Pre-Workout", 2, 4, "Blue Raspberry", "30 serv", 2, 88000, 125000),
            ("Proteina Vegana Plant 2lb", 0, 4, "Vainilla", "2 lb", 11, 120000, 169000),
            ("Pre-entreno Agotado Demo", 2, 3, "Limon", "30 serv", 0, 90000, 129000),
        ]
        acentos = [RED, RED_BRIGHT, RED_DEEP]
        productos = []
        for i, (nom, c, m, sab, pres, cant, costo, pub) in enumerate(catalogo):
            slug = re.sub(r"[^a-z0-9]+", "-", nom.lower()).strip("-")
            forma = "shaker" if "shaker" in nom.lower() else "cinturon" if "cinturon" in nom.lower() else "envase"
            foto = guardar_imagen_producto(slug, nom, marcas[m].nombre_marca, pres, forma, acentos[i % 3])
            tabla = guardar_tabla_nutricional(slug, nom, pres)
            productos.append(Productos.objects.create(
                id_categoria=categorias[c], id_marca=marcas[m], nombre_producto=nom,
                descripcion=f"{nom}. Suplemento de alta calidad para tu entrenamiento.",
                cantidad=cant, fechaven=ahora + timedelta(days={4: 25, 6: 70}.get(i, 180 + i * 20)), sabor=sab,
                presentacion=pres, estado=1, precio=costo, precio_pub=pub,
                iProductImg=foto, iInfoImg=tabla,
            ))

        # --- Geografia, clientes y proveedores ---
        depto = Departamentos.objects.create(nombre_departamento="Cundinamarca")
        municipios = [Municipios.objects.create(id_departamento=depto, nombre_municipio=n)
                      for n in ("Bogota", "Soacha", "Chia")]
        nombres = [("Laura", "Gomez"), ("Carlos", "Rojas"), ("Valentina", "Pardo"),
                   ("Andres", "Mejia"), ("Camila", "Torres"), ("Santiago", "Ruiz")]
        clientes = []
        for i, (n, a) in enumerate(nombres):
            clientes.append(Clientes.objects.create(
                id_municipio=municipios[i % 3], documento=str(1000200300 + i), nombres=n,
                apellidos=a, celular=f"31{rnd.randint(10000000, 99999999)}",
                barrio="Centro", direccion=f"Calle {10 + i} # {i + 3}-20", estado=True,
                correo=f"{n.lower()}@correo.test",
            ))
        proveedores = [Proveedores.objects.create(
            nombre_proveedor=n, telefono=f"60{rnd.randint(10000000, 99999999)}"[:10],
            correo=f"ventas@{n.split()[0].lower()}.test", direccion="Zona Industrial",
            informacion_adicional="Proveedor de ejemplo", tipo_documento="NIT",
            numero_documento_nit=f"900{rnd.randint(100000, 999999)}-1", estado=1,
        ) for n in ("NutriImport SAS", "FitDistribuciones", "Sport Supply Colombia", "ProLife Ltda")]

        # --- Compras ---
        for i, prov in enumerate(proveedores):
            compra = Compras.objects.create(
                id_proveedor_id=prov.pk, fechareg=(ahora - timedelta(days=3 + i * 28)).date(),
                estado=1, totalCompra=0,
            )
            total = 0
            for prod in rnd.sample(productos, 3):
                cant = rnd.randint(5, 20)
                sub = cant * prod.precio
                total += sub
                Detallecompra.objects.create(
                    id_producto_id=prod.pk, id_compra=compra, cantidad=cant,
                    precio_uni=prod.precio, precio_tot=sub, estado=1,
                )
            compra.totalCompra = total
            compra.save()

        # --- Ventas de los ultimos 6 meses (el cinturon nunca se vende: ejemplo de capital sin rotacion) ---
        vendibles = [p for p in productos if 'Cinturon' not in p.nombre_producto]
        ventas = []
        for i in range(16):
            dias = rnd.randint(0, 14) if i < 6 else rnd.randint(15, 170)  # algunas ventas del mes actual
            total = costo_total = 0
            venta = Ventas.objects.create(
                id_cliente_id=rnd.choice(clientes).pk, fechareg=(ahora - timedelta(days=dias)).date(),
                descuentoVenta="0", totalVentaDescuento="0", totalVenta=0,
                margenGanancia=0, estado=1,
            )
            for prod in rnd.sample(vendibles, rnd.randint(1, 3)):
                cant = rnd.randint(1, 3)
                sub = cant * prod.precio_pub
                total += sub
                costo_total += cant * prod.precio
                Detalleventa.objects.create(
                    id_producto_id=prod.pk, id_venta=venta, cantidad=cant,
                    precio_compra=prod.precio, precio_venta=prod.precio_pub,
                    descuentoProducto="0", totalProductoDescuento=str(sub),
                    margenGanancia=sub - cant * prod.precio, precio_tot=sub, estado=1,
                )
            venta.totalVenta = total
            venta.totalVentaDescuento = str(total)
            venta.margenGanancia = total - costo_total
            venta.save()
            ventas.append(venta)

        for venta, estado in zip(ventas[:3], ("en proceso", "confirmado", "cancelado")):
            pedido = Pedidos.objects.create(
                id_venta=venta, id_cliente_id=venta.id_cliente_id, total_pedido=venta.totalVenta,
                estado=estado,
            )
            for d in Detalleventa.objects.filter(id_venta=venta)[:2]:
                DetallePedido.objects.create(
                    id_pedido=pedido, id_producto_id=d.id_producto_id, sabor='Original',
                    cantidad=d.cantidad, precio_uni=d.precio_venta, precio_tot=d.precio_tot,
                )

        contexto.limpiar()

        # --- Meta del mes e historial de ejemplo para la auditoria ---
        from control.models import MetaVentas, RegistroAuditoria
        hoy = timezone.localdate()
        MetaVentas.objects.create(anio=hoy.year, mes=hoy.month, valor=5_000_000, definida_por='Admin')
        ejemplos = [
            (5, 'login', 'seguridad', 'Inició sesión (admin@tuiranfit.test)', '', ''),
            (22, 'crear', 'productos', 'Creó producto «Proteina Vegana Plant 2lb»', 'Producto', ''),
            (47, 'editar', 'productos', 'Editó producto «Whey Gold Standard 5lb»: Existencias, Precio al público', 'Producto',
             '[{"campo": "Existencias", "antes": "12", "despues": "18"}, {"campo": "Precio al público", "antes": "$229.000", "despues": "$239.000"}]'),
            (95, 'crear', 'ventas', 'Registró la venta #000012 de Valentina Pardo por $878.000', 'Venta', ''),
            (180, 'anular', 'ventas', 'Anuló la venta #000009 (el inventario se ajustó)', 'Venta',
             '[{"campo": "Estado", "antes": "Activa", "despues": "Anulada"}]'),
            (300, 'exportar', 'ventas', 'Generó el informe de ventas del 01/10/2026 al 31/10/2026 (14 ventas)', '', ''),
        ]
        for minutos, accion, modulo, texto, objeto, cambios in ejemplos:
            RegistroAuditoria.objects.create(
                fecha=timezone.now() - timedelta(minutes=minutos), usuario_nombre='Admin', usuario_correo='admin@tuiranfit.test',
                rol_id=admin.id_rol, ip='127.0.0.1', accion=accion, modulo=modulo, objeto=objeto, descripcion=texto, cambios=cambios)

        self.stdout.write(self.style.SUCCESS(
            "Datos de ejemplo cargados. Usuario: admin@tuiranfit.test / admin123"
        ))
