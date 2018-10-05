import logging
import os
import socket
import sys
import warnings

from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

try:
    from netbox import configuration
except ImportError:
    raise ImproperlyConfigured(
        "Configuration file is not present. Please define netbox/netbox/configuration.py per the documentation."
    )

# Raise a deprecation warning for Python 2.x
if sys.version_info[0] < 3:
    warnings.warn(
        "Support for Python 2 will be removed in NetBox v2.5. Please consider migration to Python 3 at your earliest "
        "opportunity. Guidance is available in the documentation at http://netbox.readthedocs.io/.",
        DeprecationWarning
    )

VERSION = '2.4.7-dev'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import required configuration parameters
ALLOWED_HOSTS = DATABASE = SECRET_KEY = None
for setting in ['ALLOWED_HOSTS', 'DATABASE', 'SECRET_KEY']:
    try:
        globals()[setting] = getattr(configuration, setting)
    except AttributeError:
        raise ImproperlyConfigured(
            "Mandatory setting {} is missing from configuration.py.".format(setting)
        )

# Import optional configuration parameters
ADMINS = getattr(configuration, 'ADMINS', [])
BANNER_BOTTOM = getattr(configuration, 'BANNER_BOTTOM', '')
BANNER_LOGIN = getattr(configuration, 'BANNER_LOGIN', '')
BANNER_TOP = getattr(configuration, 'BANNER_TOP', '')
BASE_PATH = getattr(configuration, 'BASE_PATH', '')
if BASE_PATH:
    BASE_PATH = BASE_PATH.strip('/') + '/'  # Enforce trailing slash only
CHANGELOG_RETENTION = getattr(configuration, 'CHANGELOG_RETENTION', 90)
CORS_ORIGIN_ALLOW_ALL = getattr(configuration, 'CORS_ORIGIN_ALLOW_ALL', False)
CORS_ORIGIN_REGEX_WHITELIST = getattr(configuration, 'CORS_ORIGIN_REGEX_WHITELIST', [])
CORS_ORIGIN_WHITELIST = getattr(configuration, 'CORS_ORIGIN_WHITELIST', [])
DATE_FORMAT = getattr(configuration, 'DATE_FORMAT', 'N j, Y')
DATETIME_FORMAT = getattr(configuration, 'DATETIME_FORMAT', 'N j, Y g:i a')
DEBUG = getattr(configuration, 'DEBUG', False)
ENFORCE_GLOBAL_UNIQUE = getattr(configuration, 'ENFORCE_GLOBAL_UNIQUE', False)
EMAIL = getattr(configuration, 'EMAIL', {})
LOGGING = getattr(configuration, 'LOGGING', {})
LOGIN_REQUIRED = getattr(configuration, 'LOGIN_REQUIRED', False)
MAINTENANCE_MODE = getattr(configuration, 'MAINTENANCE_MODE', False)
MAX_PAGE_SIZE = getattr(configuration, 'MAX_PAGE_SIZE', 1000)
MEDIA_ROOT = getattr(configuration, 'MEDIA_ROOT', os.path.join(BASE_DIR, 'media')).rstrip('/')
NAPALM_USERNAME = getattr(configuration, 'NAPALM_USERNAME', '')
NAPALM_PASSWORD = getattr(configuration, 'NAPALM_PASSWORD', '')
NAPALM_TIMEOUT = getattr(configuration, 'NAPALM_TIMEOUT', 30)
NAPALM_ARGS = getattr(configuration, 'NAPALM_ARGS', {})
PAGINATE_COUNT = getattr(configuration, 'PAGINATE_COUNT', 50)
PREFER_IPV4 = getattr(configuration, 'PREFER_IPV4', False)
REPORTS_ROOT = getattr(configuration, 'REPORTS_ROOT', os.path.join(BASE_DIR, 'reports')).rstrip('/')
REDIS = getattr(configuration, 'REDIS', {})
SHORT_DATE_FORMAT = getattr(configuration, 'SHORT_DATE_FORMAT', 'Y-m-d')
SHORT_DATETIME_FORMAT = getattr(configuration, 'SHORT_DATETIME_FORMAT', 'Y-m-d H:i')
SHORT_TIME_FORMAT = getattr(configuration, 'SHORT_TIME_FORMAT', 'H:i:s')
TIME_FORMAT = getattr(configuration, 'TIME_FORMAT', 'g:i a')
TIME_ZONE = getattr(configuration, 'TIME_ZONE', 'UTC')
WEBHOOKS_ENABLED = getattr(configuration, 'WEBHOOKS_ENABLED', False)

CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

# Attempt to import LDAP configuration if it has been defined
LDAP_IGNORE_CERT_ERRORS = False
try:
    from netbox.ldap_config import *
    LDAP_CONFIGURED = True
except ImportError:
    LDAP_CONFIGURED = False

# LDAP configuration (optional)
if LDAP_CONFIGURED:
    try:
        import ldap
        import django_auth_ldap
        # Prepend LDAPBackend to the default ModelBackend
        AUTHENTICATION_BACKENDS = [
            'django_auth_ldap.backend.LDAPBackend',
            'django.contrib.auth.backends.ModelBackend',
        ]
        # Optionally disable strict certificate checking
        if LDAP_IGNORE_CERT_ERRORS:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        # Enable logging for django_auth_ldap
        ldap_logger = logging.getLogger('django_auth_ldap')
        ldap_logger.addHandler(logging.StreamHandler())
        ldap_logger.setLevel(logging.DEBUG)
    except ImportError:
        raise ImproperlyConfigured(
            "LDAP authentication has been configured, but django-auth-ldap is not installed. You can remove "
            "netbox/ldap_config.py to disable LDAP."
        )

# Database
configuration.DATABASE.update({'ENGINE': 'django.db.backends.postgresql'})
DATABASES = {
    'default': configuration.DATABASE,
}

# Redis
REDIS_HOST = REDIS.get('HOST', 'localhost')
REDIS_PORT = REDIS.get('PORT', 6379)
REDIS_PASSWORD = REDIS.get('PASSWORD', '')
REDIS_DATABASE = REDIS.get('DATABASE', 0)
REDIS_DEFAULT_TIMEOUT = REDIS.get('DEFAULT_TIMEOUT', 300)

# Email
EMAIL_HOST = EMAIL.get('SERVER')
EMAIL_PORT = EMAIL.get('PORT', 25)
EMAIL_HOST_USER = EMAIL.get('USERNAME')
EMAIL_HOST_PASSWORD = EMAIL.get('PASSWORD')
EMAIL_TIMEOUT = EMAIL.get('TIMEOUT', 10)
SERVER_EMAIL = EMAIL.get('FROM_EMAIL')
EMAIL_SUBJECT_PREFIX = '[NetBox] '

# Installed applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'corsheaders',
    'debug_toolbar',
    'django_filters',
    'django_tables2',
    'mptt',
    'rest_framework',
    'taggit',
    'taggit_serializer',
    'timezone_field',
    'circuits',
    'dcim',
    'ipam',
    'extras',
    'secrets',
    'tenancy',
    'users',
    'utilities',
    'virtualization',
    'drf_yasg',
]

# Only load django-rq if the webhook backend is enabled
if WEBHOOKS_ENABLED:
    INSTALLED_APPS.append('django_rq')

# Middleware
MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'utilities.middleware.ExceptionHandlingMiddleware',
    'utilities.middleware.LoginRequiredMiddleware',
    'utilities.middleware.APIVersionMiddleware',
    'extras.middleware.ObjectChangeMiddleware',
)

ROOT_URLCONF = 'netbox.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'utilities.context_processors.settings',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'netbox.wsgi.application'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR + '/static/'
STATIC_URL = '/{}static/'.format(BASE_PATH)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "project-static"),
)

# Media
MEDIA_URL = '/{}media/'.format(BASE_PATH)

# Disable default limit of 1000 fields per request. Needed for bulk deletion of objects. (Added in Django 1.10.)
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Authentication URLs
LOGIN_URL = '/{}login/'.format(BASE_PATH)

# Secrets
SECRETS_MIN_PUBKEY_SIZE = 2048

# Django filters
FILTERS_NULL_CHOICE_LABEL = 'None'
FILTERS_NULL_CHOICE_VALUE = '0'  # Must be a string

# Django REST framework (API)
REST_FRAMEWORK_VERSION = VERSION[0:3]  # Use major.minor as API version
REST_FRAMEWORK = {
    'ALLOWED_VERSIONS': [REST_FRAMEWORK_VERSION],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'netbox.api.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'netbox.api.OptionalLimitOffsetPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'netbox.api.TokenPermissions',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'netbox.api.FormlessBrowsableAPIRenderer',
    ),
    'DEFAULT_VERSION': REST_FRAMEWORK_VERSION,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'PAGE_SIZE': PAGINATE_COUNT,
    'VIEW_NAME_FUNCTION': 'netbox.api.get_view_name',
}

# Django RQ (Webhooks backend)
RQ_QUEUES = {
    'default': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': REDIS_DATABASE,
        'PASSWORD': REDIS_PASSWORD,
        'DEFAULT_TIMEOUT': REDIS_DEFAULT_TIMEOUT,
    }
}

# drf_yasg settings for Swagger
SWAGGER_SETTINGS = {
    'DEFAULT_FIELD_INSPECTORS': [
        'utilities.custom_inspectors.NullableBooleanFieldInspector',
        'utilities.custom_inspectors.CustomChoiceFieldInspector',
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.ReferencingSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
    'DEFAULT_FILTER_INSPECTORS': [
        'utilities.custom_inspectors.IdInFilterInspector',
        'drf_yasg.inspectors.CoreAPICompatInspector',
    ],
    'DEFAULT_PAGINATOR_INSPECTORS': [
        'utilities.custom_inspectors.NullablePaginatorInspector',
        'drf_yasg.inspectors.DjangoRestResponsePagination',
        'drf_yasg.inspectors.CoreAPICompatInspector',
    ],
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },
    'VALIDATOR_URL': None,
}


# Django debug toolbar
INTERNAL_IPS = (
    '127.0.0.1',
    '::1',
)


try:
    HOSTNAME = socket.gethostname()
except Exception:
    HOSTNAME = 'localhost'
