import logging
import os
import platform
import socket
import warnings

from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured


#
# Environment setup
#

VERSION = '2.7.2-dev'

# Hostname
HOSTNAME = platform.node()

# Set the base directory two levels up
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Validate Python version
if platform.python_version_tuple() < ('3', '5'):
    raise RuntimeError(
        "NetBox requires Python 3.5 or higher (current: Python {})".format(platform.python_version())
    )
elif platform.python_version_tuple() < ('3', '6'):
    warnings.warn(
        "Python 3.6 or higher will be required starting with NetBox v2.8 (current: Python {})".format(
            platform.python_version()
        )
    )


#
# Configuration import
#

# Import configuration parameters
try:
    from netbox import configuration
except ImportError:
    raise ImproperlyConfigured(
        "Configuration file is not present. Please define netbox/netbox/configuration.py per the documentation."
    )

# Enforce required configuration parameters
for parameter in ['ALLOWED_HOSTS', 'DATABASE', 'SECRET_KEY', 'REDIS']:
    if not hasattr(configuration, parameter):
        raise ImproperlyConfigured(
            "Required parameter {} is missing from configuration.py.".format(parameter)
        )

# Set required parameters
ALLOWED_HOSTS = getattr(configuration, 'ALLOWED_HOSTS')
DATABASE = getattr(configuration, 'DATABASE')
REDIS = getattr(configuration, 'REDIS')
SECRET_KEY = getattr(configuration, 'SECRET_KEY')

# Set optional parameters
ADMINS = getattr(configuration, 'ADMINS', [])
BANNER_BOTTOM = getattr(configuration, 'BANNER_BOTTOM', '')
BANNER_LOGIN = getattr(configuration, 'BANNER_LOGIN', '')
BANNER_TOP = getattr(configuration, 'BANNER_TOP', '')
BASE_PATH = getattr(configuration, 'BASE_PATH', '')
if BASE_PATH:
    BASE_PATH = BASE_PATH.strip('/') + '/'  # Enforce trailing slash only
CACHE_TIMEOUT = getattr(configuration, 'CACHE_TIMEOUT', 900)
CHANGELOG_RETENTION = getattr(configuration, 'CHANGELOG_RETENTION', 90)
CORS_ORIGIN_ALLOW_ALL = getattr(configuration, 'CORS_ORIGIN_ALLOW_ALL', False)
CORS_ORIGIN_REGEX_WHITELIST = getattr(configuration, 'CORS_ORIGIN_REGEX_WHITELIST', [])
CORS_ORIGIN_WHITELIST = getattr(configuration, 'CORS_ORIGIN_WHITELIST', [])
DATE_FORMAT = getattr(configuration, 'DATE_FORMAT', 'N j, Y')
DATETIME_FORMAT = getattr(configuration, 'DATETIME_FORMAT', 'N j, Y g:i a')
DEBUG = getattr(configuration, 'DEBUG', False)
EMAIL = getattr(configuration, 'EMAIL', {})
ENFORCE_GLOBAL_UNIQUE = getattr(configuration, 'ENFORCE_GLOBAL_UNIQUE', False)
EXEMPT_VIEW_PERMISSIONS = getattr(configuration, 'EXEMPT_VIEW_PERMISSIONS', [])
LOGGING = getattr(configuration, 'LOGGING', {})
LOGIN_REQUIRED = getattr(configuration, 'LOGIN_REQUIRED', False)
LOGIN_TIMEOUT = getattr(configuration, 'LOGIN_TIMEOUT', None)
MAINTENANCE_MODE = getattr(configuration, 'MAINTENANCE_MODE', False)
MAX_PAGE_SIZE = getattr(configuration, 'MAX_PAGE_SIZE', 1000)
MEDIA_ROOT = getattr(configuration, 'MEDIA_ROOT', os.path.join(BASE_DIR, 'media')).rstrip('/')
STORAGE_BACKEND = getattr(configuration, 'STORAGE_BACKEND', None)
STORAGE_CONFIG = getattr(configuration, 'STORAGE_CONFIG', {})
METRICS_ENABLED = getattr(configuration, 'METRICS_ENABLED', False)
NAPALM_ARGS = getattr(configuration, 'NAPALM_ARGS', {})
NAPALM_PASSWORD = getattr(configuration, 'NAPALM_PASSWORD', '')
NAPALM_TIMEOUT = getattr(configuration, 'NAPALM_TIMEOUT', 30)
NAPALM_USERNAME = getattr(configuration, 'NAPALM_USERNAME', '')
PAGINATE_COUNT = getattr(configuration, 'PAGINATE_COUNT', 50)
PREFER_IPV4 = getattr(configuration, 'PREFER_IPV4', False)
REPORTS_ROOT = getattr(configuration, 'REPORTS_ROOT', os.path.join(BASE_DIR, 'reports')).rstrip('/')
SCRIPTS_ROOT = getattr(configuration, 'SCRIPTS_ROOT', os.path.join(BASE_DIR, 'scripts')).rstrip('/')
SESSION_FILE_PATH = getattr(configuration, 'SESSION_FILE_PATH', None)
SHORT_DATE_FORMAT = getattr(configuration, 'SHORT_DATE_FORMAT', 'Y-m-d')
SHORT_DATETIME_FORMAT = getattr(configuration, 'SHORT_DATETIME_FORMAT', 'Y-m-d H:i')
SHORT_TIME_FORMAT = getattr(configuration, 'SHORT_TIME_FORMAT', 'H:i:s')
TIME_FORMAT = getattr(configuration, 'TIME_FORMAT', 'g:i a')
TIME_ZONE = getattr(configuration, 'TIME_ZONE', 'UTC')


#
# Database
#

# Only PostgreSQL is supported
if METRICS_ENABLED:
    DATABASE.update({
        'ENGINE': 'django_prometheus.db.backends.postgresql'
    })
else:
    DATABASE.update({
        'ENGINE': 'django.db.backends.postgresql'
    })

DATABASES = {
    'default': DATABASE,
}


#
# Media storage
#

if STORAGE_BACKEND is not None:
    DEFAULT_FILE_STORAGE = STORAGE_BACKEND

    # django-storages
    if STORAGE_BACKEND.startswith('storages.'):

        try:
            import storages.utils
        except ImportError:
            raise ImproperlyConfigured(
                "STORAGE_BACKEND is set to {} but django-storages is not present. It can be installed by running 'pip "
                "install django-storages'.".format(STORAGE_BACKEND)
            )

        # Monkey-patch django-storages to fetch settings from STORAGE_CONFIG
        def _setting(name, default=None):
            if name in STORAGE_CONFIG:
                return STORAGE_CONFIG[name]
            return globals().get(name, default)
        storages.utils.setting = _setting

if STORAGE_CONFIG and STORAGE_BACKEND is None:
    warnings.warn(
        "STORAGE_CONFIG has been set in configuration.py but STORAGE_BACKEND is not defined. STORAGE_CONFIG will be "
        "ignored."
    )


#
# Redis
#

if 'webhooks' not in REDIS:
    raise ImproperlyConfigured(
        "REDIS section in configuration.py is missing webhooks subsection."
    )
if 'caching' not in REDIS:
    raise ImproperlyConfigured(
        "REDIS section in configuration.py is missing caching subsection."
    )

WEBHOOKS_REDIS = REDIS.get('webhooks', {})
WEBHOOKS_REDIS_HOST = WEBHOOKS_REDIS.get('HOST', 'localhost')
WEBHOOKS_REDIS_PORT = WEBHOOKS_REDIS.get('PORT', 6379)
WEBHOOKS_REDIS_PASSWORD = WEBHOOKS_REDIS.get('PASSWORD', '')
WEBHOOKS_REDIS_DATABASE = WEBHOOKS_REDIS.get('DATABASE', 0)
WEBHOOKS_REDIS_DEFAULT_TIMEOUT = WEBHOOKS_REDIS.get('DEFAULT_TIMEOUT', 300)
WEBHOOKS_REDIS_SSL = WEBHOOKS_REDIS.get('SSL', False)

CACHING_REDIS = REDIS.get('caching', {})
CACHING_REDIS_HOST = WEBHOOKS_REDIS.get('HOST', 'localhost')
CACHING_REDIS_PORT = WEBHOOKS_REDIS.get('PORT', 6379)
CACHING_REDIS_PASSWORD = WEBHOOKS_REDIS.get('PASSWORD', '')
CACHING_REDIS_DATABASE = WEBHOOKS_REDIS.get('DATABASE', 0)
CACHING_REDIS_DEFAULT_TIMEOUT = WEBHOOKS_REDIS.get('DEFAULT_TIMEOUT', 300)
CACHING_REDIS_SSL = WEBHOOKS_REDIS.get('SSL', False)


#
# Sessions
#

if LOGIN_TIMEOUT is not None:
    # Django default is 1209600 seconds (14 days)
    SESSION_COOKIE_AGE = LOGIN_TIMEOUT
if SESSION_FILE_PATH is not None:
    SESSION_ENGINE = 'django.contrib.sessions.backends.file'


#
# Email
#

EMAIL_HOST = EMAIL.get('SERVER')
EMAIL_PORT = EMAIL.get('PORT', 25)
EMAIL_HOST_USER = EMAIL.get('USERNAME')
EMAIL_HOST_PASSWORD = EMAIL.get('PASSWORD')
EMAIL_TIMEOUT = EMAIL.get('TIMEOUT', 10)
SERVER_EMAIL = EMAIL.get('FROM_EMAIL')
EMAIL_SUBJECT_PREFIX = '[NetBox] '


#
# Django
#

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'cacheops',
    'corsheaders',
    'debug_toolbar',
    'django_filters',
    'django_rq',
    'django_tables2',
    'django_prometheus',
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

# Middleware
MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
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
    'django_prometheus.middleware.PrometheusAfterMiddleware',
)

ROOT_URLCONF = 'netbox.urls'

TEMPLATES_DIR = BASE_DIR + '/templates'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

# Authentication
AUTHENTICATION_BACKENDS = [
    'utilities.auth_backends.ViewExemptModelBackend',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_TZ = True

# WSGI
WSGI_APPLICATION = 'netbox.wsgi.application'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR + '/static'
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

CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS


#
# LDAP authentication (optional)
#

try:
    from netbox import ldap_config as LDAP_CONFIG
except ImportError:
    LDAP_CONFIG = None

if LDAP_CONFIG is not None:

    # Check that django_auth_ldap is installed
    try:
        import ldap
        import django_auth_ldap
    except ImportError:
        raise ImproperlyConfigured(
            "LDAP authentication has been configured, but django-auth-ldap is not installed. Remove "
            "netbox/ldap_config.py to disable LDAP."
        )

    # Required configuration parameters
    try:
        AUTH_LDAP_SERVER_URI = getattr(LDAP_CONFIG, 'AUTH_LDAP_SERVER_URI')
    except AttributeError:
        raise ImproperlyConfigured(
            "Required parameter AUTH_LDAP_SERVER_URI is missing from ldap_config.py."
        )

    # Optional configuration parameters
    AUTH_LDAP_ALWAYS_UPDATE_USER = getattr(LDAP_CONFIG, 'AUTH_LDAP_ALWAYS_UPDATE_USER', True)
    AUTH_LDAP_AUTHORIZE_ALL_USERS = getattr(LDAP_CONFIG, 'AUTH_LDAP_AUTHORIZE_ALL_USERS', False)
    AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = getattr(LDAP_CONFIG, 'AUTH_LDAP_BIND_AS_AUTHENTICATING_USER', False)
    AUTH_LDAP_BIND_DN = getattr(LDAP_CONFIG, 'AUTH_LDAP_BIND_DN', '')
    AUTH_LDAP_BIND_PASSWORD = getattr(LDAP_CONFIG, 'AUTH_LDAP_BIND_PASSWORD', '')
    AUTH_LDAP_CACHE_TIMEOUT = getattr(LDAP_CONFIG, 'AUTH_LDAP_CACHE_TIMEOUT', 0)
    AUTH_LDAP_CONNECTION_OPTIONS = getattr(LDAP_CONFIG, 'AUTH_LDAP_CONNECTION_OPTIONS', {})
    AUTH_LDAP_DENY_GROUP = getattr(LDAP_CONFIG, 'AUTH_LDAP_DENY_GROUP', None)
    AUTH_LDAP_FIND_GROUP_PERMS = getattr(LDAP_CONFIG, 'AUTH_LDAP_FIND_GROUP_PERMS', False)
    AUTH_LDAP_GLOBAL_OPTIONS = getattr(LDAP_CONFIG, 'AUTH_LDAP_GLOBAL_OPTIONS', {})
    AUTH_LDAP_GROUP_SEARCH = getattr(LDAP_CONFIG, 'AUTH_LDAP_GROUP_SEARCH', None)
    AUTH_LDAP_GROUP_TYPE = getattr(LDAP_CONFIG, 'AUTH_LDAP_GROUP_TYPE', None)
    AUTH_LDAP_MIRROR_GROUPS = getattr(LDAP_CONFIG, 'AUTH_LDAP_MIRROR_GROUPS', None)
    AUTH_LDAP_MIRROR_GROUPS_EXCEPT = getattr(LDAP_CONFIG, 'AUTH_LDAP_MIRROR_GROUPS_EXCEPT', None)
    AUTH_LDAP_PERMIT_EMPTY_PASSWORD = getattr(LDAP_CONFIG, 'AUTH_LDAP_PERMIT_EMPTY_PASSWORD', False)
    AUTH_LDAP_REQUIRE_GROUP = getattr(LDAP_CONFIG, 'AUTH_LDAP_REQUIRE_GROUP', None)
    AUTH_LDAP_NO_NEW_USERS = getattr(LDAP_CONFIG, 'AUTH_LDAP_NO_NEW_USERS', False)
    AUTH_LDAP_START_TLS = getattr(LDAP_CONFIG, 'AUTH_LDAP_START_TLS', False)
    AUTH_LDAP_USER_QUERY_FIELD = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_QUERY_FIELD', None)
    AUTH_LDAP_USER_ATTRLIST = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_ATTRLIST', None)
    AUTH_LDAP_USER_ATTR_MAP = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_ATTR_MAP', {})
    AUTH_LDAP_USER_DN_TEMPLATE = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_DN_TEMPLATE', None)
    AUTH_LDAP_USER_FLAGS_BY_GROUP = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_FLAGS_BY_GROUP', {})
    AUTH_LDAP_USER_SEARCH = getattr(LDAP_CONFIG, 'AUTH_LDAP_USER_SEARCH', None)

    # Optionally disable strict certificate checking
    if getattr(LDAP_CONFIG, 'LDAP_IGNORE_CERT_ERRORS', False):
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    # Prepend LDAPBackend to the authentication backends list
    AUTHENTICATION_BACKENDS.insert(0, 'django_auth_ldap.backend.LDAPBackend')

    # Enable logging for django_auth_ldap
    ldap_logger = logging.getLogger('django_auth_ldap')
    ldap_logger.addHandler(logging.StreamHandler())
    ldap_logger.setLevel(logging.DEBUG)


#
# Caching
#

if CACHING_REDIS_SSL:
    REDIS_CACHE_CON_STRING = 'rediss://'
else:
    REDIS_CACHE_CON_STRING = 'redis://'

if CACHING_REDIS_PASSWORD:
    REDIS_CACHE_CON_STRING = '{}:{}@'.format(REDIS_CACHE_CON_STRING, CACHING_REDIS_PASSWORD)

REDIS_CACHE_CON_STRING = '{}{}:{}/{}'.format(
    REDIS_CACHE_CON_STRING,
    CACHING_REDIS_HOST,
    CACHING_REDIS_PORT,
    CACHING_REDIS_DATABASE
)

if not CACHE_TIMEOUT:
    CACHEOPS_ENABLED = False
else:
    CACHEOPS_ENABLED = True

CACHEOPS_REDIS = REDIS_CACHE_CON_STRING
CACHEOPS_DEFAULTS = {
    'timeout': CACHE_TIMEOUT
}
CACHEOPS = {
    'auth.user': {'ops': 'get', 'timeout': 60 * 15},
    'auth.*': {'ops': ('fetch', 'get')},
    'auth.permission': {'ops': 'all'},
    'circuits.*': {'ops': 'all'},
    'dcim.*': {'ops': 'all'},
    'ipam.*': {'ops': 'all'},
    'extras.*': {'ops': 'all'},
    'secrets.*': {'ops': 'all'},
    'users.*': {'ops': 'all'},
    'tenancy.*': {'ops': 'all'},
    'virtualization.*': {'ops': 'all'},
}
CACHEOPS_DEGRADE_ON_FAILURE = True


#
# Django Prometheus
#

PROMETHEUS_EXPORT_MIGRATIONS = False


#
# Django filters
#

FILTERS_NULL_CHOICE_LABEL = 'None'
FILTERS_NULL_CHOICE_VALUE = 'null'


#
# Django REST framework (API)
#

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


#
# drf_yasg (OpenAPI/Swagger)
#

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'utilities.custom_inspectors.NetBoxSwaggerAutoSchema',
    'DEFAULT_FIELD_INSPECTORS': [
        'utilities.custom_inspectors.NullableBooleanFieldInspector',
        'utilities.custom_inspectors.CustomChoiceFieldInspector',
        'utilities.custom_inspectors.TagListFieldInspector',
        'utilities.custom_inspectors.SerializedPKRelatedFieldInspector',
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.ReferencingSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.SerializerMethodFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
    'DEFAULT_FILTER_INSPECTORS': [
        'utilities.custom_inspectors.IdInFilterInspector',
        'drf_yasg.inspectors.CoreAPICompatInspector',
    ],
    'DEFAULT_MODEL_DEPTH': 1,
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


#
# Django RQ (Webhooks backend)
#

RQ_QUEUES = {
    'default': {
        'HOST': WEBHOOKS_REDIS_HOST,
        'PORT': WEBHOOKS_REDIS_PORT,
        'DB': WEBHOOKS_REDIS_DATABASE,
        'PASSWORD': WEBHOOKS_REDIS_PASSWORD,
        'DEFAULT_TIMEOUT': WEBHOOKS_REDIS_DEFAULT_TIMEOUT,
        'SSL': WEBHOOKS_REDIS_SSL,
    }
}


#
# Django debug toolbar
#

INTERNAL_IPS = (
    '127.0.0.1',
    '::1',
)


#
# NetBox internal settings
#

# Secrets
SECRETS_MIN_PUBKEY_SIZE = 2048

# Pagination
PER_PAGE_DEFAULTS = [
    25, 50, 100, 250, 500, 1000
]
if PAGINATE_COUNT not in PER_PAGE_DEFAULTS:
    PER_PAGE_DEFAULTS.append(PAGINATE_COUNT)
    PER_PAGE_DEFAULTS = sorted(PER_PAGE_DEFAULTS)
