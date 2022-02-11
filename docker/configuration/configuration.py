####
## We recommend to not edit this file.
## Create separate files to overwrite the settings.
## See `extra.py` as an example.
####

import re
from os import environ
from os.path import abspath, dirname, join

# For reference see https://netbox.readthedocs.io/en/stable/configuration/
# Based on https://github.com/netbox-community/netbox/blob/master/netbox/netbox/configuration.example.py

# Read secret from file
def _read_secret(secret_name, default = None):
    try:
        f = open('/run/secrets/' + secret_name, 'r', encoding='utf-8')
    except EnvironmentError:
        return default
    else:
        with f:
            return f.readline().strip()

_BASE_DIR = dirname(dirname(abspath(__file__)))

#########################
#                       #
#   Required settings   #
#                       #
#########################

# This is a list of valid fully-qualified domain names (FQDNs) for the NetBox server. NetBox will not permit write
# access to the server via any other hostnames. The first FQDN in the list will be treated as the preferred name.
#
# Example: ALLOWED_HOSTS = ['netbox.example.com', 'netbox.internal.local']
ALLOWED_HOSTS = environ.get('ALLOWED_HOSTS', '*').split(' ')

# PostgreSQL database configuration. See the Django documentation for a complete list of available parameters:
#   https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASE = {
    'NAME': environ.get('DB_NAME', 'netbox'),       # Database name
    'USER': environ.get('DB_USER', ''),             # PostgreSQL username
    'PASSWORD': _read_secret('db_password', environ.get('DB_PASSWORD', '')),
                                                    # PostgreSQL password
    'HOST': environ.get('DB_HOST', 'localhost'),    # Database server
    'PORT': environ.get('DB_PORT', ''),             # Database port (leave blank for default)
    'OPTIONS': {'sslmode': environ.get('DB_SSLMODE', 'prefer')},
                                                    # Database connection SSLMODE
    'CONN_MAX_AGE': int(environ.get('DB_CONN_MAX_AGE', '300')),
                                                    # Max database connection age
}

# Redis database settings. Redis is used for caching and for queuing background tasks such as webhook events. A separate
# configuration exists for each. Full connection details are required in both sections, and it is strongly recommended
# to use two separate database IDs.
REDIS = {
    'tasks': {
        'HOST': environ.get('REDIS_HOST', 'localhost'),
        'PORT': int(environ.get('REDIS_PORT', 6379)),
        'PASSWORD': _read_secret('redis_password', environ.get('REDIS_PASSWORD', '')),
        'DATABASE': int(environ.get('REDIS_DATABASE', 0)),
        'SSL': environ.get('REDIS_SSL', 'False').lower() == 'true',
    },
    'caching': {
        'HOST': environ.get('REDIS_CACHE_HOST', environ.get('REDIS_HOST', 'localhost')),
        'PORT': int(environ.get('REDIS_CACHE_PORT', environ.get('REDIS_PORT', 6379))),
        'PASSWORD': _read_secret('redis_cache_password', environ.get('REDIS_CACHE_PASSWORD', environ.get('REDIS_PASSWORD', ''))),
        'DATABASE': int(environ.get('REDIS_CACHE_DATABASE', 1)),
        'SSL': environ.get('REDIS_CACHE_SSL', environ.get('REDIS_SSL', 'False')).lower() == 'true',
    },
}

# This key is used for secure generation of random numbers and strings. It must never be exposed outside of this file.
# For optimal security, SECRET_KEY should be at least 50 characters in length and contain a mix of letters, numbers, and
# symbols. NetBox will not run without this defined. For more information, see
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = _read_secret('secret_key', environ.get('SECRET_KEY', ''))


#########################
#                       #
#   Optional settings   #
#                       #
#########################

# Specify one or more name and email address tuples representing NetBox administrators. These people will be notified of
# application errors (assuming correct email settings are provided).
ADMINS = [
    # ['John Doe', 'jdoe@example.com'],
]

# URL schemes that are allowed within links in NetBox
ALLOWED_URL_SCHEMES = (
    'file', 'ftp', 'ftps', 'http', 'https', 'irc', 'mailto', 'sftp', 'ssh', 'tel', 'telnet', 'tftp', 'vnc', 'xmpp',
)

# Optionally display a persistent banner at the top and/or bottom of every page. HTML is allowed. To display the same
# content in both banners, define BANNER_TOP and set BANNER_BOTTOM = BANNER_TOP.
BANNER_TOP = environ.get('BANNER_TOP', '')
BANNER_BOTTOM = environ.get('BANNER_BOTTOM', '')

# Text to include on the login page above the login form. HTML is allowed.
BANNER_LOGIN = environ.get('BANNER_LOGIN', '')

# Base URL path if accessing NetBox within a directory. For example, if installed at http://example.com/netbox/, set:
# BASE_PATH = 'netbox/'
BASE_PATH = environ.get('BASE_PATH', '')

# Maximum number of days to retain logged changes. Set to 0 to retain changes indefinitely. (Default: 90)
CHANGELOG_RETENTION = int(environ.get('CHANGELOG_RETENTION', 90))

# API Cross-Origin Resource Sharing (CORS) settings. If CORS_ORIGIN_ALLOW_ALL is set to True, all origins will be
# allowed. Otherwise, define a list of allowed origins using either CORS_ORIGIN_WHITELIST or
# CORS_ORIGIN_REGEX_WHITELIST. For more information, see https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = environ.get('CORS_ORIGIN_ALLOW_ALL', 'False').lower() == 'true'
CORS_ORIGIN_WHITELIST = list(filter(None, environ.get('CORS_ORIGIN_WHITELIST', 'https://localhost').split(' ')))
CORS_ORIGIN_REGEX_WHITELIST = [re.compile(r) for r in list(filter(None, environ.get('CORS_ORIGIN_REGEX_WHITELIST', '').split(' ')))]

# Set to True to enable server debugging. WARNING: Debugging introduces a substantial performance penalty and may reveal
# sensitive information about your installation. Only enable debugging while performing testing. Never enable debugging
# on a production system.
DEBUG = environ.get('DEBUG', 'False').lower() == 'true'

# Email settings
EMAIL = {
    'SERVER': environ.get('EMAIL_SERVER', 'localhost'),
    'PORT': int(environ.get('EMAIL_PORT', 25)),
    'USERNAME': environ.get('EMAIL_USERNAME', ''),
    'PASSWORD': _read_secret('email_password', environ.get('EMAIL_PASSWORD', '')),
    'USE_SSL': environ.get('EMAIL_USE_SSL', 'False').lower() == 'true',
    'USE_TLS': environ.get('EMAIL_USE_TLS', 'False').lower() == 'true',
    'SSL_CERTFILE': environ.get('EMAIL_SSL_CERTFILE', ''),
    'SSL_KEYFILE': environ.get('EMAIL_SSL_KEYFILE', ''),
    'TIMEOUT': int(environ.get('EMAIL_TIMEOUT', 10)),  # seconds
    'FROM_EMAIL': environ.get('EMAIL_FROM', ''),
}

# Enforcement of unique IP space can be toggled on a per-VRF basis. To enforce unique IP space within the global table
# (all prefixes and IP addresses not assigned to a VRF), set ENFORCE_GLOBAL_UNIQUE to True.
ENFORCE_GLOBAL_UNIQUE = environ.get('ENFORCE_GLOBAL_UNIQUE', 'False').lower() == 'true'

# Exempt certain models from the enforcement of view permissions. Models listed here will be viewable by all users and
# by anonymous users. List models in the form `<app>.<model>`. Add '*' to this list to exempt all models.
EXEMPT_VIEW_PERMISSIONS = list(filter(None, environ.get('EXEMPT_VIEW_PERMISSIONS', '').split(' ')))

# Enable custom logging. Please see the Django documentation for detailed guidance on configuring custom logs:
#   https://docs.djangoproject.com/en/stable/topics/logging/
LOGGING = {}

# Setting this to True will permit only authenticated users to access any part of NetBox. By default, anonymous users
# are permitted to access most data in NetBox (excluding secrets) but not make any changes.
LOGIN_REQUIRED = environ.get('LOGIN_REQUIRED', 'False').lower() == 'true'

# The length of time (in seconds) for which a user will remain logged into the web UI before being prompted to
# re-authenticate. (Default: 1209600 [14 days])
LOGIN_TIMEOUT = int(environ.get('LOGIN_TIMEOUT', 1209600))

# Setting this to True will display a "maintenance mode" banner at the top of every page.
MAINTENANCE_MODE = environ.get('MAINTENANCE_MODE', 'False').lower() == 'true'

# An API consumer can request an arbitrary number of objects =by appending the "limit" parameter to the URL (e.g.
# "?limit=1000"). This setting defines the maximum limit. Setting it to 0 or None will allow an API consumer to request
# all objects by specifying "?limit=0".
MAX_PAGE_SIZE = int(environ.get('MAX_PAGE_SIZE', 1000))

# The file path where uploaded media such as image attachments are stored. A trailing slash is not needed. Note that
# the default value of this setting is derived from the installed location.
MEDIA_ROOT = environ.get('MEDIA_ROOT', join(_BASE_DIR, 'media'))

# Expose Prometheus monitoring metrics at the HTTP endpoint '/metrics'
METRICS_ENABLED = environ.get('METRICS_ENABLED', 'False').lower() == 'true'

# Credentials that NetBox will uses to authenticate to devices when connecting via NAPALM.
NAPALM_USERNAME = environ.get('NAPALM_USERNAME', '')
NAPALM_PASSWORD = _read_secret('napalm_password', environ.get('NAPALM_PASSWORD', ''))

# NAPALM timeout (in seconds). (Default: 30)
NAPALM_TIMEOUT = int(environ.get('NAPALM_TIMEOUT', 30))

# NAPALM optional arguments (see http://napalm.readthedocs.io/en/latest/support/#optional-arguments). Arguments must
# be provided as a dictionary.
NAPALM_ARGS = {}

# Determine how many objects to display per page within a list. (Default: 50)
PAGINATE_COUNT = int(environ.get('PAGINATE_COUNT', 50))

# Enable installed plugins. Add the name of each plugin to the list.
PLUGINS = [
    'netbox_virtual_circuit_plugin',
    'netbox_bgp',
]

# Plugins configuration settings. These settings are used by various plugins that the user may have installed.
# Each key in the dictionary is the name of an installed plugin and its value is a dictionary of settings.
PLUGINS_CONFIG = {
}

# When determining the primary IP address for a device, IPv6 is preferred over IPv4 by default. Set this to True to
# prefer IPv4 instead.
PREFER_IPV4 = environ.get('PREFER_IPV4', 'False').lower() == 'true'

# Rack elevation size defaults, in pixels. For best results, the ratio of width to height should be roughly 10:1.
RACK_ELEVATION_DEFAULT_UNIT_HEIGHT = int(environ.get('RACK_ELEVATION_DEFAULT_UNIT_HEIGHT', 22))
RACK_ELEVATION_DEFAULT_UNIT_WIDTH = int(environ.get('RACK_ELEVATION_DEFAULT_UNIT_WIDTH', 220))

# Remote authentication support
REMOTE_AUTH_ENABLED = environ.get('REMOTE_AUTH_ENABLED', 'False').lower() == 'true'
REMOTE_AUTH_BACKEND = environ.get('REMOTE_AUTH_BACKEND', 'netbox.authentication.RemoteUserBackend')
REMOTE_AUTH_HEADER = environ.get('REMOTE_AUTH_HEADER', 'HTTP_REMOTE_USER')
REMOTE_AUTH_AUTO_CREATE_USER = environ.get('REMOTE_AUTH_AUTO_CREATE_USER', 'True').lower() == 'true'
REMOTE_AUTH_DEFAULT_GROUPS = list(filter(None, environ.get('REMOTE_AUTH_DEFAULT_GROUPS', '').split(' ')))

# This repository is used to check whether there is a new release of NetBox available. Set to None to disable the
# version check or use the URL below to check for release in the official NetBox repository.
# https://api.github.com/repos/netbox-community/netbox/releases
RELEASE_CHECK_URL = environ.get('RELEASE_CHECK_URL', None)

# The file path where custom reports will be stored. A trailing slash is not needed. Note that the default value of
# this setting is derived from the installed location.
REPORTS_ROOT = environ.get('REPORTS_ROOT', '/etc/netbox/reports')

# Maximum execution time for background tasks, in seconds.
RQ_DEFAULT_TIMEOUT = int(environ.get('RQ_DEFAULT_TIMEOUT', 300))

# The file path where custom scripts will be stored. A trailing slash is not needed. Note that the default value of
# this setting is derived from the installed location.
SCRIPTS_ROOT = environ.get('SCRIPTS_ROOT', '/etc/netbox/scripts')

# By default, NetBox will store session data in the database. Alternatively, a file path can be specified here to use
# local file storage instead. (This can be useful for enabling authentication on a standby instance with read-only
# database access.) Note that the user as which NetBox runs must have read and write permissions to this path.
SESSION_FILE_PATH = environ.get('SESSIONS_ROOT', None)

# Time zone (default: UTC)
TIME_ZONE = environ.get('TIME_ZONE', 'UTC')

# Date/time formatting. See the following link for supported formats:
# https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date
DATE_FORMAT = environ.get('DATE_FORMAT', 'N j, Y')
SHORT_DATE_FORMAT = environ.get('SHORT_DATE_FORMAT', 'Y-m-d')
TIME_FORMAT = environ.get('TIME_FORMAT', 'g:i a')
SHORT_TIME_FORMAT = environ.get('SHORT_TIME_FORMAT', 'H:i:s')
DATETIME_FORMAT = environ.get('DATETIME_FORMAT', 'N j, Y g:i a')
SHORT_DATETIME_FORMAT = environ.get('SHORT_DATETIME_FORMAT', 'Y-m-d H:i')