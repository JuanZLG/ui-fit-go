from pathlib import Path
import os
from django.urls import reverse_lazy
from datetime import timedelta
from django.conf import settings    

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p-q-5)!3*c#&12)htxwxd_5kbk89m52#n14a=sniyklxz4!qw7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'products',
    'eproviders',
    'customers',
    'purchases',
    'sales',
    'users',
    'dashboard',
    'page',
    'authenticator',
    'rest_framework',
    'tuiranfitgo'
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tuiranfitgo.urls'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
}

SECRET_KEY = 'ClaveSuperSecretaJamasLaVeraNadie'


JWT_PAYLOAD_HANDLER = 'authenticator.utils.custom_jwt_payload_handler'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'products', 'templates'),
                 os.path.join(BASE_DIR, 'eproviders', 'templates'),
                 os.path.join(BASE_DIR, 'customers', 'templates'),
                 os.path.join(BASE_DIR, 'tuiranfitgo', 'templates'),
                 os.path.join(BASE_DIR, 'sales', 'templates'),
                 os.path.join(BASE_DIR, 'purchases', 'templates'),
                 os.path.join(BASE_DIR, 'dashboard', 'templates'),
                 os.path.join(BASE_DIR, 'users', 'templates'),
                 os.path.join(BASE_DIR, 'page', 'templates'),
                 os.path.join(BASE_DIR, 'authenticator', 'templates')
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tuiranfitgo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME':'tuiranfitx',
        'USER': 'root',
        'PASSWORD': 'monitoc10',
        'PORT': '3306'
    }
}

# Configura el motor de sesión en 'file'
SESSION_ENGINE = 'django.contrib.sessions.backends.file'

# Especifica la ubicación donde se almacenarán los archivos de sesión
SESSION_FILE_PATH = os.path.join(BASE_DIR, 'session_data')


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True

# LOGIN_REDIRECT_URL = 'entrada'

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': timedelta(days=1),
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'authenticator.auth.custom_get_username',
}

# AUTH_USER_MODEL = 'authenticator.Usuarios'

# AUTHENTICATION_BACKENDS = [
#     'users.backends.CustomAuthBackend',
#     'django.contrib.auth.backends.ModelBackend',
# ]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'tuiranfitgo', 'static'), 
    os.path.join(BASE_DIR, 'sales', 'static'),
    os.path.join(BASE_DIR, 'eproviders', 'static'),
    os.path.join(BASE_DIR, 'users', 'static'),
    os.path.join(BASE_DIR, 'dashboard', 'static'),
    os.path.join(BASE_DIR, 'page', 'static'),
    os.path.join(BASE_DIR, 'products', 'static'),
    os.path.join(BASE_DIR, 'authenticator', 'static')
]

# Ruta en el sistema de archivos donde se guardarán los archivos subidos
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL base para servir archivos de medios (archivos subidos por los usuarios)
MEDIA_URL = '/media/'

CORS_ALLOW_ALL_ORIGINS = True

# Default primary key field typeF
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# settings.py
BASE_URL = 'http://www.tu-sitio.com/'  





EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' 
EMAIL_PORT = 587  
EMAIL_USE_TLS = True 
EMAIL_HOST_USER = 'juanmartinezciro657@gmail.com' 
EMAIL_HOST_PASSWORD = 'kckj mlib zwaf anhh' 

