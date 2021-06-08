import importlib
import logging
import os
import platform
import re
import socket
import warnings
from urllib.parse import urlsplit

from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import URLValidator


#
# Environment setup
#

VERSION = '3.0-beta1'

# Hostname
HOSTNAME = platform.node()

# Set the base directory two levels up
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Validate Python version
if platform.python_version_tuple() < ('3', '7'):
    raise RuntimeError(
        f"NetBox requires Python 3.7 or higher (current: Python {platform.python_version()})"
    )


#
# Configuration import
#

# Import configuration parameters
try:
    from netbox import configuration
except ModuleNotFoundError as e:
    if getattr(e, 'name') == 'configuration':
        raise ImproperlyConfigured(
            "Configuration file is not present. Please define netbox/netbox/configuration.py per the documentation."
        )
    raise

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
ALLOWED_URL_SCHEMES = getattr(configuration, 'ALLOWED_URL_SCHEMES', (
    'file', 'ftp', 'ftps', 'http', 'https', 'irc', 'mailto', 'sftp', 'ssh', 'tel', 'telnet', 'tftp', 'vnc', 'xmpp',
))
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
CUSTOM_VALIDATORS = getattr(configuration, 'CUSTOM_VALIDATORS', {})
DATE_FORMAT = getattr(configuration, 'DATE_FORMAT', 'N j, Y')
DATETIME_FORMAT = getattr(configuration, 'DATETIME_FORMAT', 'N j, Y g:i a')
DEBUG = getattr(configuration, 'DEBUG', False)
DEVELOPER = getattr(configuration, 'DEVELOPER', False)
DOCS_ROOT = getattr(configuration, 'DOCS_ROOT', os.path.join(os.path.dirname(BASE_DIR), 'docs'))
EMAIL = getattr(configuration, 'EMAIL', {})
ENFORCE_GLOBAL_UNIQUE = getattr(configuration, 'ENFORCE_GLOBAL_UNIQUE', False)
EXEMPT_VIEW_PERMISSIONS = getattr(configuration, 'EXEMPT_VIEW_PERMISSIONS', [])
HTTP_PROXIES = getattr(configuration, 'HTTP_PROXIES', None)
INTERNAL_IPS = getattr(configuration, 'INTERNAL_IPS', ('127.0.0.1', '::1'))
LOGGING = getattr(configuration, 'LOGGING', {})
LOGIN_REQUIRED = getattr(configuration, 'LOGIN_REQUIRED', False)
LOGIN_TIMEOUT = getattr(configuration, 'LOGIN_TIMEOUT', None)
MAINTENANCE_MODE = getattr(configuration, 'MAINTENANCE_MODE', False)
MAPS_URL = getattr(configuration, 'MAPS_URL', 'https://maps.google.com/?q=')
MAX_PAGE_SIZE = getattr(configuration, 'MAX_PAGE_SIZE', 1000)
MEDIA_ROOT = getattr(configuration, 'MEDIA_ROOT', os.path.join(BASE_DIR, 'media')).rstrip('/')
METRICS_ENABLED = getattr(configuration, 'METRICS_ENABLED', False)
NAPALM_ARGS = getattr(configuration, 'NAPALM_ARGS', {})
NAPALM_PASSWORD = getattr(configuration, 'NAPALM_PASSWORD', '')
NAPALM_TIMEOUT = getattr(configuration, 'NAPALM_TIMEOUT', 30)
NAPALM_USERNAME = getattr(configuration, 'NAPALM_USERNAME', '')
PAGINATE_COUNT = getattr(configuration, 'PAGINATE_COUNT', 50)
PLUGINS = getattr(configuration, 'PLUGINS', [])
PLUGINS_CONFIG = getattr(configuration, 'PLUGINS_CONFIG', {})
PREFER_IPV4 = getattr(configuration, 'PREFER_IPV4', False)
RACK_ELEVATION_DEFAULT_UNIT_HEIGHT = getattr(configuration, 'RACK_ELEVATION_DEFAULT_UNIT_HEIGHT', 22)
RACK_ELEVATION_DEFAULT_UNIT_WIDTH = getattr(configuration, 'RACK_ELEVATION_DEFAULT_UNIT_WIDTH', 220)
REMOTE_AUTH_AUTO_CREATE_USER = getattr(configuration, 'REMOTE_AUTH_AUTO_CREATE_USER', False)
REMOTE_AUTH_BACKEND = getattr(configuration, 'REMOTE_AUTH_BACKEND', 'netbox.authentication.RemoteUserBackend')
REMOTE_AUTH_DEFAULT_GROUPS = getattr(configuration, 'REMOTE_AUTH_DEFAULT_GROUPS', [])
REMOTE_AUTH_DEFAULT_PERMISSIONS = getattr(configuration, 'REMOTE_AUTH_DEFAULT_PERMISSIONS', {})
REMOTE_AUTH_ENABLED = getattr(configuration, 'REMOTE_AUTH_ENABLED', False)
REMOTE_AUTH_HEADER = getattr(configuration, 'REMOTE_AUTH_HEADER', 'HTTP_REMOTE_USER')
RELEASE_CHECK_URL = getattr(configuration, 'RELEASE_CHECK_URL', None)
RELEASE_CHECK_TIMEOUT = getattr(configuration, 'RELEASE_CHECK_TIMEOUT', 24 * 3600)
REPORTS_ROOT = getattr(configuration, 'REPORTS_ROOT', os.path.join(BASE_DIR, 'reports')).rstrip('/')
RQ_DEFAULT_TIMEOUT = getattr(configuration, 'RQ_DEFAULT_TIMEOUT', 300)
SCRIPTS_ROOT = getattr(configuration, 'SCRIPTS_ROOT', os.path.join(BASE_DIR, 'scripts')).rstrip('/')
SESSION_FILE_PATH = getattr(configuration, 'SESSION_FILE_PATH', None)
SESSION_COOKIE_NAME = getattr(configuration, 'SESSION_COOKIE_NAME', 'sessionid')
SHORT_DATE_FORMAT = getattr(configuration, 'SHORT_DATE_FORMAT', 'Y-m-d')
SHORT_DATETIME_FORMAT = getattr(configuration, 'SHORT_DATETIME_FORMAT', 'Y-m-d H:i')
SHORT_TIME_FORMAT = getattr(configuration, 'SHORT_TIME_FORMAT', 'H:i:s')
STORAGE_BACKEND = getattr(configuration, 'STORAGE_BACKEND', None)
STORAGE_CONFIG = getattr(configuration, 'STORAGE_CONFIG', {})
TIME_FORMAT = getattr(configuration, 'TIME_FORMAT', 'g:i a')
TIME_ZONE = getattr(configuration, 'TIME_ZONE', 'UTC')

# Validate update repo URL and timeout
if RELEASE_CHECK_URL:
    validator = URLValidator(
        message=(
            "RELEASE_CHECK_URL must be a valid API URL. Example: "
            "https://api.github.com/repos/netbox-community/netbox"
        )
    )
    try:
        validator(RELEASE_CHECK_URL)
    except ValidationError as err:
        raise ImproperlyConfigured(str(err))

# Enforce a minimum cache timeout for update checks
if RELEASE_CHECK_TIMEOUT < 3600:
    raise ImproperlyConfigured("RELEASE_CHECK_TIMEOUT has to be at least 3600 seconds (1 hour)")


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
        except ModuleNotFoundError as e:
            if getattr(e, 'name') == 'storages':
                raise ImproperlyConfigured(
                    f"STORAGE_BACKEND is set to {STORAGE_BACKEND} but django-storages is not present. It can be "
                    f"installed by running 'pip install django-storages'."
                )
            raise e

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

# Background task queuing
if 'tasks' not in REDIS:
    raise ImproperlyConfigured(
        "REDIS section in configuration.py is missing the 'tasks' subsection."
    )
TASKS_REDIS = REDIS['tasks']
TASKS_REDIS_HOST = TASKS_REDIS.get('HOST', 'localhost')
TASKS_REDIS_PORT = TASKS_REDIS.get('PORT', 6379)
TASKS_REDIS_SENTINELS = TASKS_REDIS.get('SENTINELS', [])
TASKS_REDIS_USING_SENTINEL = all([
    isinstance(TASKS_REDIS_SENTINELS, (list, tuple)),
    len(TASKS_REDIS_SENTINELS) > 0
])
TASKS_REDIS_SENTINEL_SERVICE = TASKS_REDIS.get('SENTINEL_SERVICE', 'default')
TASKS_REDIS_SENTINEL_TIMEOUT = TASKS_REDIS.get('SENTINEL_TIMEOUT', 10)
TASKS_REDIS_PASSWORD = TASKS_REDIS.get('PASSWORD', '')
TASKS_REDIS_DATABASE = TASKS_REDIS.get('DATABASE', 0)
TASKS_REDIS_SSL = TASKS_REDIS.get('SSL', False)
TASKS_REDIS_SKIP_TLS_VERIFY = TASKS_REDIS.get('INSECURE_SKIP_TLS_VERIFY', False)

# Caching
if 'caching' not in REDIS:
    raise ImproperlyConfigured(
        "REDIS section in configuration.py is missing caching subsection."
    )
CACHING_REDIS = REDIS['caching']
CACHING_REDIS_HOST = CACHING_REDIS.get('HOST', 'localhost')
CACHING_REDIS_PORT = CACHING_REDIS.get('PORT', 6379)
CACHING_REDIS_SENTINELS = CACHING_REDIS.get('SENTINELS', [])
CACHING_REDIS_USING_SENTINEL = all([
    isinstance(CACHING_REDIS_SENTINELS, (list, tuple)),
    len(CACHING_REDIS_SENTINELS) > 0
])
CACHING_REDIS_SENTINEL_SERVICE = CACHING_REDIS.get('SENTINEL_SERVICE', 'default')
CACHING_REDIS_PASSWORD = CACHING_REDIS.get('PASSWORD', '')
CACHING_REDIS_DATABASE = CACHING_REDIS.get('DATABASE', 0)
CACHING_REDIS_SSL = CACHING_REDIS.get('SSL', False)
CACHING_REDIS_SKIP_TLS_VERIFY = CACHING_REDIS.get('INSECURE_SKIP_TLS_VERIFY', False)


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
EMAIL_HOST_USER = EMAIL.get('USERNAME')
EMAIL_HOST_PASSWORD = EMAIL.get('PASSWORD')
EMAIL_PORT = EMAIL.get('PORT', 25)
EMAIL_SSL_CERTFILE = EMAIL.get('SSL_CERTFILE')
EMAIL_SSL_KEYFILE = EMAIL.get('SSL_KEYFILE')
EMAIL_SUBJECT_PREFIX = '[NetBox] '
EMAIL_USE_SSL = EMAIL.get('USE_SSL', False)
EMAIL_USE_TLS = EMAIL.get('USE_TLS', False)
EMAIL_TIMEOUT = EMAIL.get('TIMEOUT', 10)
SERVER_EMAIL = EMAIL.get('FROM_EMAIL')


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
    'graphiql_debug_toolbar',
    'django_filters',
    'django_tables2',
    'django_prometheus',
    'graphene_django',
    'mptt',
    'rest_framework',
    'taggit',
    'timezone_field',
    'circuits',
    'dcim',
    'ipam',
    'extras',
    'tenancy',
    'users',
    'utilities',
    'virtualization',
    'django_rq',  # Must come after extras to allow overriding management commands
    'drf_yasg',
]

# Middleware
MIDDLEWARE = [
    'graphiql_debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'netbox.middleware.ExceptionHandlingMiddleware',
    'netbox.middleware.RemoteUserMiddleware',
    'netbox.middleware.LoginRequiredMiddleware',
    'netbox.middleware.APIVersionMiddleware',
    'netbox.middleware.ObjectChangeMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

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
                'netbox.context_processors.settings_and_registry',
            ],
        },
    },
]

# Set up authentication backends
AUTHENTICATION_BACKENDS = [
    REMOTE_AUTH_BACKEND,
    'netbox.authentication.ObjectPermissionBackend',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_TZ = True

# WSGI
WSGI_APPLICATION = 'netbox.wsgi.application'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR + '/static'
STATIC_URL = '/{}static/'.format(BASE_PATH)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "project-static", "dist"),
    os.path.join(BASE_DIR, "project-static", "img"),
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

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Exclude potentially sensitive models from wildcard view exemption. These may still be exempted
# by specifying the model individually in the EXEMPT_VIEW_PERMISSIONS configuration parameter.
EXEMPT_EXCLUDE_MODELS = (
    ('auth', 'group'),
    ('auth', 'user'),
    ('users', 'objectpermission'),
)

#
# Caching
#
if CACHING_REDIS_USING_SENTINEL:
    CACHEOPS_SENTINEL = {
        'locations': CACHING_REDIS_SENTINELS,
        'service_name': CACHING_REDIS_SENTINEL_SERVICE,
        'db': CACHING_REDIS_DATABASE,
        'password': CACHING_REDIS_PASSWORD,
    }
else:
    CACHEOPS_REDIS = {
        'host': CACHING_REDIS_HOST,
        'port': CACHING_REDIS_PORT,
        'db': CACHING_REDIS_DATABASE,
        'password': CACHING_REDIS_PASSWORD,
        'ssl': CACHING_REDIS_SSL,
        'ssl_cert_reqs': None if CACHING_REDIS_SKIP_TLS_VERIFY else 'required',
    }

if not CACHE_TIMEOUT:
    CACHEOPS_ENABLED = False
else:
    CACHEOPS_ENABLED = True


CACHEOPS_DEFAULTS = {
    'timeout': CACHE_TIMEOUT
}
CACHEOPS = {
    'auth.user': {'ops': 'get', 'timeout': 60 * 15},
    'auth.*': {'ops': ('fetch', 'get')},
    'auth.permission': {'ops': 'all'},
    'circuits.*': {'ops': 'all'},
    'dcim.inventoryitem': None,  # MPTT models are exempt due to raw SQL
    'dcim.region': None,  # MPTT models are exempt due to raw SQL
    'dcim.location': None,  # MPTT models are exempt due to raw SQL
    'dcim.*': {'ops': 'all'},
    'ipam.*': {'ops': 'all'},
    'extras.*': {'ops': 'all'},
    'users.*': {'ops': 'all'},
    'tenancy.tenantgroup': None,  # MPTT models are exempt due to raw SQL
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

REST_FRAMEWORK_VERSION = VERSION.rsplit('.', 1)[0]  # Use major.minor as API version
REST_FRAMEWORK = {
    'ALLOWED_VERSIONS': [REST_FRAMEWORK_VERSION],
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'netbox.api.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_METADATA_CLASS': 'netbox.api.metadata.BulkOperationMetadata',
    'DEFAULT_PAGINATION_CLASS': 'netbox.api.pagination.OptionalLimitOffsetPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'netbox.api.authentication.TokenPermissions',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'netbox.api.renderers.FormlessBrowsableAPIRenderer',
    ),
    'DEFAULT_VERSION': REST_FRAMEWORK_VERSION,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'PAGE_SIZE': PAGINATE_COUNT,
    'SCHEMA_COERCE_METHOD_NAMES': {
        # Default mappings
        'retrieve': 'read',
        'destroy': 'delete',
        # Custom operations
        'bulk_destroy': 'bulk_delete',
    },
    'VIEW_NAME_FUNCTION': 'utilities.api.get_view_name',
}


#
# drf_yasg (OpenAPI/Swagger)
#

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'utilities.custom_inspectors.NetBoxSwaggerAutoSchema',
    'DEFAULT_FIELD_INSPECTORS': [
        'utilities.custom_inspectors.CustomFieldsDataFieldInspector',
        'utilities.custom_inspectors.JSONFieldInspector',
        'utilities.custom_inspectors.NullableBooleanFieldInspector',
        'utilities.custom_inspectors.ChoiceFieldInspector',
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
        'drf_yasg.inspectors.CoreAPICompatInspector',
    ],
    'DEFAULT_INFO': 'netbox.urls.openapi_info',
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

if TASKS_REDIS_USING_SENTINEL:
    RQ_PARAMS = {
        'SENTINELS': TASKS_REDIS_SENTINELS,
        'MASTER_NAME': TASKS_REDIS_SENTINEL_SERVICE,
        'DB': TASKS_REDIS_DATABASE,
        'PASSWORD': TASKS_REDIS_PASSWORD,
        'SOCKET_TIMEOUT': None,
        'CONNECTION_KWARGS': {
            'socket_connect_timeout': TASKS_REDIS_SENTINEL_TIMEOUT
        },
    }
else:
    RQ_PARAMS = {
        'HOST': TASKS_REDIS_HOST,
        'PORT': TASKS_REDIS_PORT,
        'DB': TASKS_REDIS_DATABASE,
        'PASSWORD': TASKS_REDIS_PASSWORD,
        'SSL': TASKS_REDIS_SSL,
        'SSL_CERT_REQS': None if TASKS_REDIS_SKIP_TLS_VERIFY else 'required',
        'DEFAULT_TIMEOUT': RQ_DEFAULT_TIMEOUT,
    }

RQ_QUEUES = {
    'default': RQ_PARAMS,  # Webhooks
    'check_releases': RQ_PARAMS,
}


#
# NetBox internal settings
#

# Pagination
PER_PAGE_DEFAULTS = [
    25, 50, 100, 250, 500, 1000
]
if PAGINATE_COUNT not in PER_PAGE_DEFAULTS:
    PER_PAGE_DEFAULTS.append(PAGINATE_COUNT)
    PER_PAGE_DEFAULTS = sorted(PER_PAGE_DEFAULTS)


#
# Plugins
#

for plugin_name in PLUGINS:

    # Import plugin module
    try:
        plugin = importlib.import_module(plugin_name)
    except ModuleNotFoundError as e:
        if getattr(e, 'name') == plugin_name:
            raise ImproperlyConfigured(
                "Unable to import plugin {}: Module not found. Check that the plugin module has been installed within the "
                "correct Python environment.".format(plugin_name)
            )
        raise e

    # Determine plugin config and add to INSTALLED_APPS.
    try:
        plugin_config = plugin.config
        INSTALLED_APPS.append("{}.{}".format(plugin_config.__module__, plugin_config.__name__))
    except AttributeError:
        raise ImproperlyConfigured(
            "Plugin {} does not provide a 'config' variable. This should be defined in the plugin's __init__.py file "
            "and point to the PluginConfig subclass.".format(plugin_name)
        )

    # Validate user-provided configuration settings and assign defaults
    if plugin_name not in PLUGINS_CONFIG:
        PLUGINS_CONFIG[plugin_name] = {}
    plugin_config.validate(PLUGINS_CONFIG[plugin_name], VERSION)

    # Add middleware
    plugin_middleware = plugin_config.middleware
    if plugin_middleware and type(plugin_middleware) in (list, tuple):
        MIDDLEWARE.extend(plugin_middleware)

    # Apply cacheops config
    if type(plugin_config.caching_config) is not dict:
        raise ImproperlyConfigured(
            "Plugin {} caching_config must be a dictionary.".format(plugin_name)
        )
    CACHEOPS.update({
        "{}.{}".format(plugin_name, key): value for key, value in plugin_config.caching_config.items()
    })
