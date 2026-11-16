"""Contraseñas con bcrypt (60 caracteres: caben en la columna existente).

Compatibilidad: las cuentas antiguas guardan la contraseña en texto plano. Al iniciar
sesión con éxito se vuelven a guardar con hash automáticamente.
"""
import re
import secrets
import string

import bcrypt

_BCRYPT_RE = re.compile(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$")

REGLA_CONTRASENA = "La contraseña debe tener al menos 8 caracteres, una mayúscula y un número."


def esta_hasheada(valor):
    return bool(valor) and bool(_BCRYPT_RE.match(valor))


def hashear(contrasena):
    return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("ascii")


def verificar(contrasena, guardada):
    """True si ``contrasena`` coincide con la guardada (hash o texto plano heredado)."""
    if not contrasena or not guardada:
        return False
    if esta_hasheada(guardada):
        try:
            return bcrypt.checkpw(contrasena.encode("utf-8"), guardada.encode("ascii"))
        except ValueError:
            return False
    return secrets.compare_digest(contrasena.encode("utf-8"), guardada.encode("utf-8"))


def es_valida(contrasena):
    return bool(contrasena) and bool(re.fullmatch(r"(?=.*[A-Z])(?=.*\d).{8,}", contrasena))


def generar_temporal(longitud=10):
    """Contraseña temporal aleatoria (con mayúscula y número)."""
    alfabeto = string.ascii_letters + string.digits
    while True:
        valor = "".join(secrets.choice(alfabeto) for _ in range(longitud))
        if es_valida(valor):
            return valor
