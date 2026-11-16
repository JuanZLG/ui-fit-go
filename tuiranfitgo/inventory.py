"""Reglas de inventario compartidas por ventas, compras, pedidos y tienda.

Todas las apps definen su propia versión del modelo ``Productos`` (misma tabla),
por eso estas funciones reciben la clase del modelo como primer argumento.

Las operaciones de stock usan UPDATE atómico con F() y una condición, de modo que
dos ventas simultáneas nunca pueden dejar el inventario en negativo.
"""
from django.db.models import F


class StockError(Exception):
    """El inventario no permite realizar la operación."""


class DatosInvalidos(ValueError):
    """Los datos recibidos del cliente no son válidos."""


def entero_positivo(valor, campo="cantidad"):
    """Convierte ``valor`` a un entero > 0 o lanza DatosInvalidos."""
    if isinstance(valor, bool):
        raise DatosInvalidos(f"El campo «{campo}» no es válido.")
    try:
        numero = float(str(valor).strip())
    except (TypeError, ValueError):
        raise DatosInvalidos(f"El campo «{campo}» debe ser un número entero.")
    if numero != int(numero) or int(numero) <= 0:
        raise DatosInvalidos(f"El campo «{campo}» debe ser un número entero mayor que cero.")
    return int(numero)


def entero_no_negativo(valor, campo="cantidad"):
    """Entero >= 0 (el stock puede ser 0)."""
    if isinstance(valor, bool):
        raise DatosInvalidos(f"El campo «{campo}» no es válido.")
    try:
        numero = float(str(valor).strip())
    except (TypeError, ValueError):
        raise DatosInvalidos(f"El campo «{campo}» debe ser un número entero.")
    if numero != int(numero) or int(numero) < 0:
        raise DatosInvalidos(f"El campo «{campo}» debe ser un entero igual o mayor que cero.")
    return int(numero)


def numero_no_negativo(valor, campo="valor"):
    """Convierte ``valor`` a float >= 0 o lanza DatosInvalidos."""
    if isinstance(valor, bool):
        raise DatosInvalidos(f"El campo «{campo}» no es válido.")
    try:
        numero = float(str(valor).strip())
    except (TypeError, ValueError):
        raise DatosInvalidos(f"El campo «{campo}» debe ser numérico.")
    if numero != numero or numero < 0 or numero == float("inf"):
        raise DatosInvalidos(f"El campo «{campo}» no puede ser negativo.")
    return numero


def descontar_stock(Producto, id_producto, cantidad):
    """Resta ``cantidad`` del inventario si hay suficiente y el producto está activo."""
    actualizados = Producto.objects.filter(
        pk=id_producto, estado=1, cantidad__gte=cantidad
    ).update(cantidad=F("cantidad") - cantidad)
    if actualizados:
        return
    producto = Producto.objects.filter(pk=id_producto).first()
    if producto is None:
        raise StockError("El producto no existe.")
    if producto.estado != 1:
        raise StockError(f"«{producto.nombre_producto}» está inactivo y no se puede vender.")
    raise StockError(
        f"Stock insuficiente de «{producto.nombre_producto}»: "
        f"hay {max(producto.cantidad, 0)} disponible(s) y se solicitaron {cantidad}."
    )


def reponer_stock(Producto, id_producto, cantidad):
    """Suma ``cantidad`` al inventario."""
    Producto.objects.filter(pk=id_producto).update(cantidad=F("cantidad") + cantidad)


def quitar_stock_compra(Producto, id_producto, cantidad):
    """Resta stock al anular una compra; no permite dejarlo en negativo."""
    actualizados = Producto.objects.filter(
        pk=id_producto, cantidad__gte=cantidad
    ).update(cantidad=F("cantidad") - cantidad)
    if not actualizados:
        producto = Producto.objects.filter(pk=id_producto).first()
        nombre = producto.nombre_producto if producto else "el producto"
        raise StockError(
            f"No es posible anular la compra: el stock de «{nombre}» quedaría negativo."
        )


def nombre_imagen(valor):
    """Devuelve la ruta de una imagen sin importar cómo llegó (bytes, str o FieldFile)."""
    if not valor:
        return ""
    if isinstance(valor, (bytes, bytearray, memoryview)):
        return bytes(valor).decode("utf-8", "ignore")
    if isinstance(valor, str):
        return valor
    return getattr(valor, "name", "") or ""
