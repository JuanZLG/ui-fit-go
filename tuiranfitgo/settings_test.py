"""Ajustes para pytest: base SQLite en memoria (no requiere MySQL) y correo simulado."""
import tempfile

from .settings import *  # noqa: F401,F403

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
MEDIA_ROOT = tempfile.mkdtemp(prefix='tuiranfit_media_')
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
