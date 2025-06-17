from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
from django.core.management.utils import get_random_secret_key

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga variables de entorno desde .env
load_dotenv(BASE_DIR / '.env')

# Secret Key - lee de .env o genera una aleatoria en desarrollo
SECRET_KEY = os.getenv('SECRET_KEY', get_random_secret_key())

# Debug
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Hosts permitidos
ALLOWED_HOSTS = ['*']  # En producción, reemplaza '*' por tus dominios

# Aplicaciones instaladas
INSTALLED_APPS = [
    'fisiogestion',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs
ROOT_URLCONF = 'AppWeb.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# WSGI
WSGI_APPLICATION = 'AppWeb.wsgi.application'

# Base de datos
DATABASES = {
    'default': dj_database_url.config(
        default=f"mysql://{os.getenv('DB_USER','root')}:{os.getenv('KEYDB','')}@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','3306')}/{os.getenv('DB_NAME','fisiogestion')}"
    )
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
CSRF_TRUSTED_ORIGINS = ['https://fisiogestion-production.up.railway.app']

# Modelo de usuario
AUTH_USER_MODEL = 'fisiogestion.Usuario'

# Backends de autenticación
authentication_backends = [
    'django.contrib.auth.backends.ModelBackend',
]

# Redirecciones de login/logout
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Campo PK por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
