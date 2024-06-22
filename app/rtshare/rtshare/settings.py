import os.path
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev').lower()

if ENVIRONMENT == 'dev':
    ENVIRONMENT_COLOR = 'gray'
elif ENVIRONMENT == 'test':
    ENVIRONMENT_COLOR = 'orange'
elif ENVIRONMENT == 'ci':
    ENVIRONMENT_COLOR = 'red'
else:
    ENVIRONMENT_COLOR = 'red'


SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = (ENVIRONMENT == 'dev')

if not DEBUG:
    ALLOWED_HOSTS = [
        '.starsweep.space',
    ]
else:
    ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'django_extensions',
    'django.contrib.humanize',
    'daphne',
    'rest_framework',
    'rest_framework.authtoken',
    'django.contrib.staticfiles',
    'django_bootstrap5',
    'django_eventstream',
    'storages',
    'adrf',

    'public',
    'telescope',
    'observations',
    'analysis',
    'users',
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

AUTHENTICATION_BACKENDS = [
    'rtshare.authentication_backends.TokenAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

if not DEBUG:
    MIDDLEWARE.insert(0, "django_grip.GripMiddleware")
    GRIP_URL = os.environ['GRIP_URL']

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

STORAGES = {
    'remote': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'endpoint_url': os.environ['LINODE_BUCKET_URL'],
            'bucket_name': os.environ['LINODE_BUCKET_NAME'],
            'access_key': os.environ['LINODE_BUCKET_ACCESS_KEY'],
            'secret_key': os.environ['LINODE_BUCKET_SECRET_KEY'],
            'addressing_style': 'virtual',
            'default_acl': 'public-read',
        },
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
}

ROOT_URLCONF = 'rtshare.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
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

ASGI_APPLICATION = 'rtshare.asgi.application'

EVENTSTREAM_STORAGE_CLASS = 'django_eventstream.storage.DjangoModelStorage'
EVENTSTREAM_CHANNELMANAGER_CLASS = 'telescope.channels.TelescopeChannelManager'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Security

# SECURE_HSTS_SECONDS = 518400
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_HTTPONLY = True

if not DEBUG:
    # SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True

if not DEBUG:
    # See notes at https://docs.djangoproject.com/en/1.10/ref/settings/
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    CONN_MAX_AGE = 10
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['DATABASE_NAME'],
            'USER': os.environ['POSTGRES_USER'],
            'PASSWORD': os.environ['POSTGRES_PASSWORD'],
            'HOST': os.environ['POSTGRES_HOST'],
            'PORT': '5432',
        }
    }

# Caches

if CACHE_URL := os.environ.get('CACHE_URL', None):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
            'LOCATION': CACHE_URL,
        }
    }

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Sending Email

EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'noreply@starsweep.space',
)
EMAIL_TIMEOUT = 10

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]
STATIC_ROOT = os.environ['STATIC_ROOT']


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ['MEDIA_ROOT']

# Logger Settings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

try:
    CELERY_BROKER_URL = os.environ['CELERY_BROKER_URL']
except KeyError:
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES = True

CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ('json',)
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

if time_limit := os.environ.get('CELERY_TASK_SOFT_TIME_LIMIT', None):
    CELERYD_TASK_SOFT_TIME_LIMIT = int(time_limit)

if time_limit := os.environ.get('CELERY_TASK_TIME_LIMIT', None):
    CELERYD_TASK_TIME_LIMIT = int(time_limit)
