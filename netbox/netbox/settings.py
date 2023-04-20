import hashlib
import importlib
import importlib.util
import os
import platform
import sys
import warnings
from urllib.parse import urlsplit

import django
import sentry_sdk
from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import URLValidator
from django.utils.encoding import force_str
from extras.plugins import PluginConfig
from sentry_sdk.integrations.django import DjangoIntegration

from netbox.config import PARAMS
from netbox.constants import RQ_QUEUE_DEFAULT, RQ_QUEUE_HIGH, RQ_QUEUE_LOW


#
# Environment setup
#

VERSION = '3.4.9-dev'

# Hostname
HOSTNAME = platform.node()

# Set the base directory two levels up
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Validate Python version
if sys.version_info < (3, 8):
    raise RuntimeError(
        f"NetBox requires Python 3.8 or later. (Currently installed: Python {platform.python_version()})"
    )

DEFAULT_SENTRY_DSN = 'https://198cf560b29d4054ab8e583a1d10ea58@o1242133.ingest.sentry.io/6396485'

#
# Configuration import
#

# Import configuration parameters
config_path = os.getenv('NETBOX_CONFIGURATION', 'netbox.configuration')
try:
    configuration = importlib.import_module(config_path)
except ModuleNotFoundError as e:
    if getattr(e, 'name') == config_path:
        raise ImproperlyConfigured(
            f"Specified configuration module ({config_path}) not found. Please define netbox/netbox/configuration.py "
            f"per the documentation, or specify an alternate module in the NETBOX_CONFIGURATION environment variable."
        )
    raise

# Enforce required configuration parameters
for parameter in ['ALLOWED_HOSTS', 'DATABASE', 'SECRET_KEY', 'REDIS']:
    if not hasattr(configuration, parameter):
        raise ImproperlyConfigured(f"Required parameter {parameter} is missing from configuration.")

# Set required parameters
ALLOWED_HOSTS = getattr(configuration, 'ALLOWED_HOSTS')
DATABASE = getattr(configuration, 'DATABASE')
REDIS = getattr(configuration, 'REDIS')
SECRET_KEY = getattr(configuration, 'SECRET_KEY')

# Calculate a unique deployment ID from the secret key
DEPLOYMENT_ID = hashlib.sha256(SECRET_KEY.encode('utf-8')).hexdigest()[:16]

# Set static config parameters
ADMINS = getattr(configuration, 'ADMINS', [])
ALLOW_TOKEN_RETRIEVAL = getattr(configuration, 'ALLOW_TOKEN_RETRIEVAL', True)
AUTH_PASSWORD_VALIDATORS = getattr(configuration, 'AUTH_PASSWORD_VALIDATORS', [])
BASE_PATH = getattr(configuration, 'BASE_PATH', '')
if BASE_PATH:
    BASE_PATH = BASE_PATH.strip('/') + '/'  # Enforce trailing slash only
CSRF_COOKIE_PATH = LANGUAGE_COOKIE_PATH = SESSION_COOKIE_PATH = f'/{BASE_PATH.rstrip("/")}'
CORS_ORIGIN_ALLOW_ALL = getattr(configuration, 'CORS_ORIGIN_ALLOW_ALL', False)
CORS_ORIGIN_REGEX_WHITELIST = getattr(configuration, 'CORS_ORIGIN_REGEX_WHITELIST', [])
CORS_ORIGIN_WHITELIST = getattr(configuration, 'CORS_ORIGIN_WHITELIST', [])
CSRF_COOKIE_NAME = getattr(configuration, 'CSRF_COOKIE_NAME', 'csrftoken')
CSRF_TRUSTED_ORIGINS = getattr(configuration, 'CSRF_TRUSTED_ORIGINS', [])
DATE_FORMAT = getattr(configuration, 'DATE_FORMAT', 'N j, Y')
DATETIME_FORMAT = getattr(configuration, 'DATETIME_FORMAT', 'N j, Y g:i a')
DEBUG = getattr(configuration, 'DEBUG', False)
DEVELOPER = getattr(configuration, 'DEVELOPER', False)
DOCS_ROOT = getattr(configuration, 'DOCS_ROOT', os.path.join(os.path.dirname(BASE_DIR), 'docs'))
EMAIL = getattr(configuration, 'EMAIL', {})
EXEMPT_VIEW_PERMISSIONS = getattr(configuration, 'EXEMPT_VIEW_PERMISSIONS', [])
FIELD_CHOICES = getattr(configuration, 'FIELD_CHOICES', {})
FILE_UPLOAD_MAX_MEMORY_SIZE = getattr(configuration, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 2621440)
HTTP_PROXIES = getattr(configuration, 'HTTP_PROXIES', None)
INTERNAL_IPS = getattr(configuration, 'INTERNAL_IPS', ('127.0.0.1', '::1'))
JINJA2_FILTERS = getattr(configuration, 'JINJA2_FILTERS', {})
LANGUAGE_CODE = getattr(configuration, 'DEFAULT_LANGUAGE', 'en-us')
LOGGING = getattr(configuration, 'LOGGING', {})
LOGIN_PERSISTENCE = getattr(configuration, 'LOGIN_PERSISTENCE', False)
LOGIN_REQUIRED = getattr(configuration, 'LOGIN_REQUIRED', False)
LOGIN_TIMEOUT = getattr(configuration, 'LOGIN_TIMEOUT', None)
LOGOUT_REDIRECT_URL = getattr(configuration, 'LOGOUT_REDIRECT_URL', 'home')
MEDIA_ROOT = getattr(configuration, 'MEDIA_ROOT', os.path.join(BASE_DIR, 'media')).rstrip('/')
METRICS_ENABLED = getattr(configuration, 'METRICS_ENABLED', False)
PLUGINS = getattr(configuration, 'PLUGINS', [])
PLUGINS_CONFIG = getattr(configuration, 'PLUGINS_CONFIG', {})
QUEUE_MAPPINGS = getattr(configuration, 'QUEUE_MAPPINGS', {})
RELEASE_CHECK_URL = getattr(configuration, 'RELEASE_CHECK_URL', None)
REMOTE_AUTH_AUTO_CREATE_USER = getattr(configuration, 'REMOTE_AUTH_AUTO_CREATE_USER', False)
REMOTE_AUTH_BACKEND = getattr(configuration, 'REMOTE_AUTH_BACKEND', 'netbox.authentication.RemoteUserBackend')
REMOTE_AUTH_DEFAULT_GROUPS = getattr(configuration, 'REMOTE_AUTH_DEFAULT_GROUPS', [])
REMOTE_AUTH_DEFAULT_PERMISSIONS = getattr(configuration, 'REMOTE_AUTH_DEFAULT_PERMISSIONS', {})
REMOTE_AUTH_ENABLED = getattr(configuration, 'REMOTE_AUTH_ENABLED', False)
REMOTE_AUTH_HEADER = getattr(configuration, 'REMOTE_AUTH_HEADER', 'HTTP_REMOTE_USER')
REMOTE_AUTH_USER_FIRST_NAME = getattr(configuration, 'REMOTE_AUTH_USER_FIRST_NAME', 'HTTP_REMOTE_USER_FIRST_NAME')
REMOTE_AUTH_USER_LAST_NAME = getattr(configuration, 'REMOTE_AUTH_USER_LAST_NAME', 'HTTP_REMOTE_USER_LAST_NAME')
REMOTE_AUTH_USER_EMAIL = getattr(configuration, 'REMOTE_AUTH_USER_EMAIL', 'HTTP_REMOTE_USER_EMAIL')
REMOTE_AUTH_GROUP_HEADER = getattr(configuration, 'REMOTE_AUTH_GROUP_HEADER', 'HTTP_REMOTE_USER_GROUP')
REMOTE_AUTH_GROUP_SYNC_ENABLED = getattr(configuration, 'REMOTE_AUTH_GROUP_SYNC_ENABLED', False)
REMOTE_AUTH_SUPERUSER_GROUPS = getattr(configuration, 'REMOTE_AUTH_SUPERUSER_GROUPS', [])
REMOTE_AUTH_SUPERUSERS = getattr(configuration, 'REMOTE_AUTH_SUPERUSERS', [])
REMOTE_AUTH_STAFF_GROUPS = getattr(configuration, 'REMOTE_AUTH_STAFF_GROUPS', [])
REMOTE_AUTH_STAFF_USERS = getattr(configuration, 'REMOTE_AUTH_STAFF_USERS', [])
REMOTE_AUTH_GROUP_SEPARATOR = getattr(configuration, 'REMOTE_AUTH_GROUP_SEPARATOR', '|')
REPORTS_ROOT = getattr(configuration, 'REPORTS_ROOT', os.path.join(BASE_DIR, 'reports')).rstrip('/')
RQ_DEFAULT_TIMEOUT = getattr(configuration, 'RQ_DEFAULT_TIMEOUT', 300)
SCRIPTS_ROOT = getattr(configuration, 'SCRIPTS_ROOT', os.path.join(BASE_DIR, 'scripts')).rstrip('/')
SEARCH_BACKEND = getattr(configuration, 'SEARCH_BACKEND', 'netbox.search.backends.CachedValueSearchBackend')
SENTRY_DSN = getattr(configuration, 'SENTRY_DSN', DEFAULT_SENTRY_DSN)
SENTRY_ENABLED = getattr(configuration, 'SENTRY_ENABLED', False)
SENTRY_SAMPLE_RATE = getattr(configuration, 'SENTRY_SAMPLE_RATE', 1.0)
SENTRY_TRACES_SAMPLE_RATE = getattr(configuration, 'SENTRY_TRACES_SAMPLE_RATE', 0)
SENTRY_TAGS = getattr(configuration, 'SENTRY_TAGS', {})
SESSION_FILE_PATH = getattr(configuration, 'SESSION_FILE_PATH', None)
SESSION_COOKIE_NAME = getattr(configuration, 'SESSION_COOKIE_NAME', 'sessionid')
SHORT_DATE_FORMAT = getattr(configuration, 'SHORT_DATE_FORMAT', 'Y-m-d')
SHORT_DATETIME_FORMAT = getattr(configuration, 'SHORT_DATETIME_FORMAT', 'Y-m-d H:i')
SHORT_TIME_FORMAT = getattr(configuration, 'SHORT_TIME_FORMAT', 'H:i:s')
STORAGE_BACKEND = getattr(configuration, 'STORAGE_BACKEND', None)
STORAGE_CONFIG = getattr(configuration, 'STORAGE_CONFIG', {})
TIME_FORMAT = getattr(configuration, 'TIME_FORMAT', 'g:i a')
TIME_ZONE = getattr(configuration, 'TIME_ZONE', 'UTC')
ENABLE_LOCALIZATION = getattr(configuration, 'ENABLE_LOCALIZATION', False)

# Check for hard-coded dynamic config parameters
for param in PARAMS:
    if hasattr(configuration, param.name):
        globals()[param.name] = getattr(configuration, param.name)

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
            import storages.utils  # type: ignore
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
TASKS_REDIS_USERNAME = TASKS_REDIS.get('USERNAME', '')
TASKS_REDIS_PASSWORD = TASKS_REDIS.get('PASSWORD', '')
TASKS_REDIS_DATABASE = TASKS_REDIS.get('DATABASE', 0)
TASKS_REDIS_SSL = TASKS_REDIS.get('SSL', False)
TASKS_REDIS_SKIP_TLS_VERIFY = TASKS_REDIS.get('INSECURE_SKIP_TLS_VERIFY', False)
TASKS_REDIS_CA_CERT_PATH = TASKS_REDIS.get('CA_CERT_PATH', False)

# Caching
if 'caching' not in REDIS:
    raise ImproperlyConfigured(
        "REDIS section in configuration.py is missing caching subsection."
    )
CACHING_REDIS_HOST = REDIS['caching'].get('HOST', 'localhost')
CACHING_REDIS_PORT = REDIS['caching'].get('PORT', 6379)
CACHING_REDIS_DATABASE = REDIS['caching'].get('DATABASE', 0)
CACHING_REDIS_USERNAME = REDIS['caching'].get('USERNAME', '')
CACHING_REDIS_USERNAME_HOST = '@'.join(filter(None, [CACHING_REDIS_USERNAME, CACHING_REDIS_HOST]))
CACHING_REDIS_PASSWORD = REDIS['caching'].get('PASSWORD', '')
CACHING_REDIS_SENTINELS = REDIS['caching'].get('SENTINELS', [])
CACHING_REDIS_SENTINEL_SERVICE = REDIS['caching'].get('SENTINEL_SERVICE', 'default')
CACHING_REDIS_PROTO = 'rediss' if REDIS['caching'].get('SSL', False) else 'redis'
CACHING_REDIS_SKIP_TLS_VERIFY = REDIS['caching'].get('INSECURE_SKIP_TLS_VERIFY', False)
CACHING_REDIS_CA_CERT_PATH = REDIS['caching'].get('CA_CERT_PATH', False)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'{CACHING_REDIS_PROTO}://{CACHING_REDIS_USERNAME_HOST}:{CACHING_REDIS_PORT}/{CACHING_REDIS_DATABASE}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': CACHING_REDIS_PASSWORD,
        }
    }
}


if CACHING_REDIS_SENTINELS:
    DJANGO_REDIS_CONNECTION_FACTORY = 'django_redis.pool.SentinelConnectionFactory'
    CACHES['default']['LOCATION'] = f'{CACHING_REDIS_PROTO}://{CACHING_REDIS_SENTINEL_SERVICE}/{CACHING_REDIS_DATABASE}'
    CACHES['default']['OPTIONS']['CLIENT_CLASS'] = 'django_redis.client.SentinelClient'
    CACHES['default']['OPTIONS']['SENTINELS'] = CACHING_REDIS_SENTINELS
if CACHING_REDIS_SKIP_TLS_VERIFY:
    CACHES['default']['OPTIONS'].setdefault('CONNECTION_POOL_KWARGS', {})
    CACHES['default']['OPTIONS']['CONNECTION_POOL_KWARGS']['ssl_cert_reqs'] = False
if CACHING_REDIS_CA_CERT_PATH:
    CACHES['default']['OPTIONS'].setdefault('CONNECTION_POOL_KWARGS', {})
    CACHES['default']['OPTIONS']['CONNECTION_POOL_KWARGS']['ssl_ca_certs'] = CACHING_REDIS_CA_CERT_PATH

#
# Sessions
#

if LOGIN_TIMEOUT is not None:
    # Django default is 1209600 seconds (14 days)
    SESSION_COOKIE_AGE = LOGIN_TIMEOUT
SESSION_SAVE_EVERY_REQUEST = bool(LOGIN_PERSISTENCE)
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
    'corsheaders',
    'debug_toolbar',
    'graphiql_debug_toolbar',
    'django_filters',
    'django_tables2',
    'django_prometheus',
    'graphene_django',
    'mptt',
    'rest_framework',
    'social_django',
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
    'wireless',
    'django_rq',  # Must come after extras to allow overriding management commands
    'drf_yasg',
]

# Middleware
MIDDLEWARE = [
    'graphiql_debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'netbox.middleware.ExceptionHandlingMiddleware',
    'netbox.middleware.RemoteUserMiddleware',
    'netbox.middleware.LoginRequiredMiddleware',
    'netbox.middleware.DynamicConfigMiddleware',
    'netbox.middleware.APIVersionMiddleware',
    'netbox.middleware.ObjectChangeMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

if not ENABLE_LOCALIZATION:
    MIDDLEWARE.remove("django.middleware.locale.LocaleMiddleware")

ROOT_URLCONF = 'netbox.urls'

TEMPLATES_DIR = BASE_DIR + '/templates'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins': [
                'utilities.templatetags.builtins.filters',
                'utilities.templatetags.builtins.tags',
            ],
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
if type(REMOTE_AUTH_BACKEND) not in (list, tuple):
    REMOTE_AUTH_BACKEND = [REMOTE_AUTH_BACKEND]
AUTHENTICATION_BACKENDS = [
    *REMOTE_AUTH_BACKEND,
    'netbox.authentication.ObjectPermissionBackend',
]

# Time zones
USE_TZ = True

# WSGI
WSGI_APPLICATION = 'netbox.wsgi.application'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR + '/static'
STATIC_URL = f'/{BASE_PATH}static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'project-static', 'dist'),
    os.path.join(BASE_DIR, 'project-static', 'img'),
    os.path.join(BASE_DIR, 'project-static', 'js'),
    ('docs', os.path.join(BASE_DIR, 'project-static', 'docs')),  # Prefix with /docs
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
LOGIN_URL = f'/{BASE_PATH}login/'
LOGIN_REDIRECT_URL = f'/{BASE_PATH}'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEST_RUNNER = "django_rich.test.RichRunner"

# Exclude potentially sensitive models from wildcard view exemption. These may still be exempted
# by specifying the model individually in the EXEMPT_VIEW_PERMISSIONS configuration parameter.
EXEMPT_EXCLUDE_MODELS = (
    ('auth', 'group'),
    ('auth', 'user'),
    ('users', 'objectpermission'),
)

# All URLs starting with a string listed here are exempt from login enforcement
EXEMPT_PATHS = (
    f'/{BASE_PATH}api/',
    f'/{BASE_PATH}graphql/',
    f'/{BASE_PATH}login/',
    f'/{BASE_PATH}oauth/',
    f'/{BASE_PATH}metrics',
)

SERIALIZATION_MODULES = {
    'json': 'utilities.serializers.json',
}


#
# Sentry
#

if SENTRY_ENABLED:
    if not SENTRY_DSN:
        raise ImproperlyConfigured("SENTRY_ENABLED is True but SENTRY_DSN has not been defined.")
    # If using the default DSN, force sampling rates
    if SENTRY_DSN == DEFAULT_SENTRY_DSN:
        SENTRY_SAMPLE_RATE = 1.0
        SENTRY_TRACES_SAMPLE_RATE = 0
    # Initialize the SDK
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        release=VERSION,
        integrations=[DjangoIntegration()],
        sample_rate=SENTRY_SAMPLE_RATE,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=True,
        http_proxy=HTTP_PROXIES.get('http') if HTTP_PROXIES else None,
        https_proxy=HTTP_PROXIES.get('https') if HTTP_PROXIES else None
    )
    # Assign any configured tags
    for k, v in SENTRY_TAGS.items():
        sentry_sdk.set_tag(k, v)
    # If using the default DSN, append a unique deployment ID tag for error correlation
    if SENTRY_DSN == DEFAULT_SENTRY_DSN:
        sentry_sdk.set_tag('netbox.deployment_id', DEPLOYMENT_ID)


#
# Django social auth
#

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'netbox.authentication.user_default_groups_handler',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# Load all SOCIAL_AUTH_* settings from the user configuration
for param in dir(configuration):
    if param.startswith('SOCIAL_AUTH_'):
        globals()[param] = getattr(configuration, param)

# Force usage of PostgreSQL's JSONB field for extra data
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_CLEAN_USERNAME_FUNCTION = 'users.utils.clean_username'

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

REST_FRAMEWORK_VERSION = '.'.join(VERSION.split('-')[0].split('.')[:2])  # Use major.minor as API version
REST_FRAMEWORK = {
    'ALLOWED_VERSIONS': [REST_FRAMEWORK_VERSION],
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'netbox.api.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_METADATA_CLASS': 'netbox.api.metadata.BulkOperationMetadata',
    'DEFAULT_PAGINATION_CLASS': 'netbox.api.pagination.OptionalLimitOffsetPagination',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'netbox.api.authentication.TokenPermissions',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'netbox.api.renderers.FormlessBrowsableAPIRenderer',
    ),
    'DEFAULT_VERSION': REST_FRAMEWORK_VERSION,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
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
# Graphene
#

GRAPHENE = {
    # Avoids naming collision on models with 'type' field; see
    # https://github.com/graphql-python/graphene-django/issues/185
    'DJANGO_CHOICE_FIELD_ENUM_V3_NAMING': True,
}


#
# drf_yasg (OpenAPI/Swagger)
#

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'utilities.custom_inspectors.NetBoxSwaggerAutoSchema',
    'DEFAULT_FIELD_INSPECTORS': [
        'utilities.custom_inspectors.CustomFieldsDataFieldInspector',
        'utilities.custom_inspectors.NullableBooleanFieldInspector',
        'utilities.custom_inspectors.ChoiceFieldInspector',
        'utilities.custom_inspectors.SerializedPKRelatedFieldInspector',
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.ReferencingSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.JSONFieldInspector',
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
        'SOCKET_TIMEOUT': None,
        'CONNECTION_KWARGS': {
            'socket_connect_timeout': TASKS_REDIS_SENTINEL_TIMEOUT
        },
    }
else:
    RQ_PARAMS = {
        'HOST': TASKS_REDIS_HOST,
        'PORT': TASKS_REDIS_PORT,
        'SSL': TASKS_REDIS_SSL,
        'SSL_CERT_REQS': None if TASKS_REDIS_SKIP_TLS_VERIFY else 'required',
    }
RQ_PARAMS.update({
    'DB': TASKS_REDIS_DATABASE,
    'USERNAME': TASKS_REDIS_USERNAME,
    'PASSWORD': TASKS_REDIS_PASSWORD,
    'DEFAULT_TIMEOUT': RQ_DEFAULT_TIMEOUT,
})

if TASKS_REDIS_CA_CERT_PATH:
    RQ_PARAMS.setdefault('REDIS_CLIENT_KWARGS', {})
    RQ_PARAMS['REDIS_CLIENT_KWARGS']['ssl_ca_certs'] = TASKS_REDIS_CA_CERT_PATH

RQ_QUEUES = {
    RQ_QUEUE_HIGH: RQ_PARAMS,
    RQ_QUEUE_DEFAULT: RQ_PARAMS,
    RQ_QUEUE_LOW: RQ_PARAMS,
}

# Add any queues defined in QUEUE_MAPPINGS
RQ_QUEUES.update({
    queue: RQ_PARAMS for queue in set(QUEUE_MAPPINGS.values()) if queue not in RQ_QUEUES
})

#
# Localization
#

if not ENABLE_LOCALIZATION:
    USE_I18N = False
    USE_L10N = False

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
        plugin_config: PluginConfig = plugin.config
    except AttributeError:
        raise ImproperlyConfigured(
            "Plugin {} does not provide a 'config' variable. This should be defined in the plugin's __init__.py file "
            "and point to the PluginConfig subclass.".format(plugin_name)
        )

    plugin_module = "{}.{}".format(plugin_config.__module__, plugin_config.__name__)  # type: ignore

    # Gather additional apps to load alongside this plugin
    django_apps = plugin_config.django_apps
    if plugin_name in django_apps:
        django_apps.pop(plugin_name)
    if plugin_module not in django_apps:
        django_apps.append(plugin_module)

    # Test if we can import all modules (or its parent, for PluginConfigs and AppConfigs)
    for app in django_apps:
        if "." in app:
            parts = app.split(".")
            spec = importlib.util.find_spec(".".join(parts[:-1]))
        else:
            spec = importlib.util.find_spec(app)
        if spec is None:
            raise ImproperlyConfigured(
                f"Failed to load django_apps specified by plugin {plugin_name}: {django_apps} "
                f"The module {app} cannot be imported. Check that the necessary package has been "
                "installed within the correct Python environment."
            )

    INSTALLED_APPS.extend(django_apps)

    # Preserve uniqueness of the INSTALLED_APPS list, we keep the last occurence
    sorted_apps = reversed(list(dict.fromkeys(reversed(INSTALLED_APPS))))
    INSTALLED_APPS = list(sorted_apps)

    # Validate user-provided configuration settings and assign defaults
    if plugin_name not in PLUGINS_CONFIG:
        PLUGINS_CONFIG[plugin_name] = {}
    plugin_config.validate(PLUGINS_CONFIG[plugin_name], VERSION)

    # Add middleware
    plugin_middleware = plugin_config.middleware
    if plugin_middleware and type(plugin_middleware) in (list, tuple):
        MIDDLEWARE.extend(plugin_middleware)

    # Create RQ queues dedicated to the plugin
    # we use the plugin name as a prefix for queue name's defined in the plugin config
    # ex: mysuperplugin.mysuperqueue1
    if type(plugin_config.queues) is not list:
        raise ImproperlyConfigured(
            "Plugin {} queues must be a list.".format(plugin_name)
        )
    RQ_QUEUES.update({
        f"{plugin_name}.{queue}": RQ_PARAMS for queue in plugin_config.queues
    })
