"""
Django settings for concesionaria project.
Automóviles Santillán - Catálogo de Vehículos
"""

import os
from pathlib import Path
from urllib.parse import urlparse

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde archivo .env
def load_env_file(filepath):
    if not filepath.exists():
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k, v = k.strip(), v.strip().strip("'\"")
            if k not in os.environ:
                os.environ[k] = v

load_env_file(BASE_DIR / '.env')

# Soporte para django-environ con fallback transparente
try:
    import environ
    env = environ.Env(
        DEBUG=(bool, True),
        SECRET_KEY=(str, 'django-insecure-santillan-change-in-production-key-xyz123'),
        ALLOWED_HOSTS=(list, ['*']),
    )
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        environ.Env.read_env(env_file)
    HAS_ENVIRON = True
except ImportError:
    HAS_ENVIRON = False
    env = None

# Configuración básica
if HAS_ENVIRON:
    SECRET_KEY = env('SECRET_KEY')
    DEBUG = env('DEBUG')
    ALLOWED_HOSTS = env('ALLOWED_HOSTS')
else:
    SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-santillan-change-in-production-key-xyz123')
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1')
    ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '*').split(',') if h.strip()]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones del proyecto
    'catalogo.apps.CatalogoConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'concesionaria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'concesionaria.wsgi.application'


# Base de datos: PostgreSQL configurado según requerimientos
# Permite toggle de conveniencia USE_SQLITE=True en .env si PostgreSQL local no está activo
USE_SQLITE = os.getenv('USE_SQLITE', 'False').lower() in ('true', '1')

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        f"postgres://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'santillan_db')}"
    )

    if HAS_ENVIRON:
        DATABASES = {
            'default': env.db_url_config(DATABASE_URL, engine='django.db.backends.postgresql')
        }
    else:
        parsed = urlparse(DATABASE_URL)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': parsed.path.lstrip('/') or os.getenv('DB_NAME', 'santillan_db'),
                'USER': parsed.username or os.getenv('DB_USER', 'postgres'),
                'PASSWORD': parsed.password or os.getenv('DB_PASSWORD', 'postgres'),
                'HOST': parsed.hostname or os.getenv('DB_HOST', 'localhost'),
                'PORT': parsed.port or int(os.getenv('DB_PORT', '5432')),
            }
        }


# Password validation
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
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Subida de fotos de vehículos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
