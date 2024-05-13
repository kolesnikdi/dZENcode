import os
import redis
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta
from rest_framework.settings import api_settings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True

RUN_FROM_LOCAL = False

HOST = os.environ.get('HOST_NAME')

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # libraries
    'rest_framework',
    'django_filters',
    'phonenumber_field',
    'knox',
    'django_user_agents',
    # applications
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'spa_application.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'spa_application.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}

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

LANGUAGE_CODE = 'en'
# TODO relocate to DB
LANGUAGES = [
    ('en', 'English'),
    ('uk', 'Ukrainian'),
]
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'knox.auth.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

REST_KNOX = {
    'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=24),
    'USER_SERIALIZER': 'registration.serializers.WebMenuUserSerializer',  # displays all data in the view
    'TOKEN_LIMIT_PER_USER': 1,
    'AUTO_REFRESH': True,
    'MIN_REFRESH_INTERVAL': 11 * 60 * 60,
    'EXPIRY_DATETIME_FORMAT': api_settings.DATETIME_FORMAT,
}

# email settings
EMAIL_HOST = os.environ.get('EMAIL_HOST') # TODO relocate to DB
EMAIL_PORT = 2525
EMAIL_USE_SSL = True

# Caches / Redis settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis_app:6379/0',
        'TIMEOUT': 300,  # default timeout for all chash
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'web_frm',
    },
}
CACHE_TIMEOUT = {
    '2fa': {
        'Email':  60 * 5, },
}

""" Redis settings to use Redis db directly."""
REDIS_CONNECTION = redis.StrictRedis(host='redis_app', port=6379, db=3)

""" all user-agents will store in Redis """
USER_AGENTS_CACHE = 'default'

# Celery settings
timezone = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERYD_TIME_LIMIT = 30 * 60
CELERY_broker_url = 'redis://redis_app:6379/1'
result_backend = 'redis://redis_app:6379/2'

if RUN_FROM_LOCAL:
    DATABASES["default"]["HOST"] = 'localhost'
    DATABASES["default"]["PORT"] = '5433'
    CACHES["default"]['LOCATION'] = 'redis://localhost:6379/0'
    CELERY_broker_url = ('redis://localhost:6379/1')
    result_backend = 'redis://localhost:6379/2'
