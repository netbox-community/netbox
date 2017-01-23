import logging
import os
import socket

from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

try:
    from netbox import configuration
except ImportError:
    raise ImproperlyConfigured("Configuration file is not present. Please define netbox/netbox/configuration.py per "
                               "the documentation.")


VERSION = '1.8.3-dev'

# Import local configuration
for setting in ['ALLOWED_HOSTS', 'DATABASE', 'SECRET_KEY']:
    try:
        globals()[setting] = getattr(configuration, setting)
    except AttributeError:
        raise ImproperlyConfigured("Mandatory setting {} is missing from configuration.py. Please define it per the "
                                   "documentation.".format(setting))

# Default configurations
ADMINS = getattr(configuration, 'ADMINS', [])
DEBUG = getattr(configuration, 'DEBUG', False)
EMAIL = getattr(configuration, 'EMAIL', {})
LOGIN_REQUIRED = getattr(configuration, 'LOGIN_REQUIRED', False)
BASE_PATH = getattr(configuration, 'BASE_PATH', '')
if BASE_PATH:
    BASE_PATH = BASE_PATH.strip('/') + '/'  # Enforce trailing slash only
MAINTENANCE_MODE = getattr(configuration, 'MAINTENANCE_MODE', False)
PAGINATE_COUNT = getattr(configuration, 'PAGINATE_COUNT', 50)
NETBOX_USERNAME = getattr(configuration, 'NETBOX_USERNAME', '')
NETBOX_PASSWORD = getattr(configuration, 'NETBOX_PASSWORD', '')
TIME_ZONE = getattr(configuration, 'TIME_ZONE', 'UTC')
DATE_FORMAT = getattr(configuration, 'DATE_FORMAT', 'N j, Y')
SHORT_DATE_FORMAT = getattr(configuration, 'SHORT_DATE_FORMAT', 'Y-m-d')
TIME_FORMAT = getattr(configuration, 'TIME_FORMAT', 'g:i a')
SHORT_TIME_FORMAT = getattr(configuration, 'SHORT_TIME_FORMAT', 'H:i:s')
DATETIME_FORMAT = getattr(configuration, 'DATETIME_FORMAT', 'N j, Y g:i a')
SHORT_DATETIME_FORMAT = getattr(configuration, 'SHORT_DATETIME_FORMAT', 'Y-m-d H:i')
BANNER_TOP = getattr(configuration, 'BANNER_TOP', False)
BANNER_BOTTOM = getattr(configuration, 'BANNER_BOTTOM', False)
PREFER_IPV4 = getattr(configuration, 'PREFER_IPV4', False)
ENFORCE_GLOBAL_UNIQUE = getattr(configuration, 'ENFORCE_GLOBAL_UNIQUE', False)
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
        logger = logging.getLogger('django_auth_ldap')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
    except ImportError:
        raise ImproperlyConfigured("LDAP authentication has been configured, but django-auth-ldap is not installed. "
                                   "You can remove netbox/ldap_config.py to disable LDAP.")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
configuration.DATABASE.update({'ENGINE': 'django.db.backends.postgresql'})
DATABASES = {
    'default': configuration.DATABASE,
}

# Email
EMAIL_HOST = EMAIL.get('SERVER')
EMAIL_PORT = EMAIL.get('PORT', 25)
EMAIL_HOST_USER = EMAIL.get('USERNAME')
EMAIL_HOST_PASSWORD = EMAIL.get('PASSWORD')
EMAIL_TIMEOUT = EMAIL.get('TIMEOUT', 10)
SERVER_EMAIL = EMAIL.get('FROM_EMAIL')
EMAIL_SUBJECT_PREFIX = '[NetBox] '

# Installed applications
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'debug_toolbar',
    'django_tables2',
    'rest_framework',
    'rest_framework_swagger',
    'circuits',
    'dcim',
    'ipam',
    'extras',
    'secrets',
    'tenancy',
    'users',
    'utilities',
)

# Middleware
MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'utilities.middleware.LoginRequiredMiddleware',
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
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_ROOT = BASE_DIR + '/static/'
STATIC_URL = '/{}static/'.format(BASE_PATH)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "project-static"),
)

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

# Django REST framework
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}
if LOGIN_REQUIRED:
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ('rest_framework.permissions.IsAuthenticated',)

# Swagger settings (API docs)
SWAGGER_SETTINGS = {
    'base_path': '{}/{}api/docs'.format(ALLOWED_HOSTS[0], BASE_PATH),
}

# Django debug toolbar
INTERNAL_IPS = (
    '127.0.0.1',
    '::1',
)


try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'
