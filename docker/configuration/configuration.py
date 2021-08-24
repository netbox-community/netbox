import os
import re
import socket

# For reference see http://netbox.readthedocs.io/en/latest/configuration/mandatory-settings/
# Based on https://github.com/netbox-community/netbox/blob/develop/netbox/netbox/configuration.example.py

# Read secret from file
def read_secret(secret_name):
    try:
        f = open('/run/secrets/' + secret_name, 'r', encoding='utf-8')
    except EnvironmentError:
        return ''
    else:
        with f:
            return f.readline().strip()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#########################
#                       #
#   Required settings   #
#                       #
#########################

# This is a list of valid fully-qualified domain names (FQDNs) for the NetBox server. NetBox will not permit write
# access to the server via any other hostnames. The first FQDN in the list will be treated as the preferred name.
#
# Example: ALLOWED_HOSTS = ['netbox.example.com', 'netbox.internal.local']
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(' ')

# PostgreSQL database configuration.
DATABASE = {
    'NAME': os.environ.get('DB_NAME', 'netbox'),         # Database name
    'USER': os.environ.get('DB_USER', ''),               # PostgreSQL username
    'PASSWORD': os.environ.get('DB_PASSWORD', read_secret('db_password')),
                                                         # PostgreSQL password
    'HOST': os.environ.get('DB_HOST', 'localhost'),      # Database server
    'PORT': os.environ.get('DB_PORT', ''),               # Database port (leave blank for default)
    'OPTIONS': {'sslmode': os.environ.get('DB_SSLMODE', 'prefer')},
                                                         # Database connection SSLMODE
    'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '300')),
                                                         # Database connection persistence
}

# This key is used for secure generation of random numbers and strings. It must never be exposed outside of this file.
# For optimal security, SECRET_KEY should be at least 50 characters in length and contain a mix of letters, numbers, and
# symbols. NetBox will not run without this defined. For more information, see
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY', read_secret('secret_key'))

# Redis database settings. The Redis database is used for caching and background processing such as webhooks
REDIS = {
    'tasks': {
        'HOST': os.environ.get('REDIS_HOST', 'localhost'),
        'PORT': int(os.environ.get('REDIS_PORT', 6379)),
        'PASSWORD': os.environ.get('REDIS_PASSWORD', read_secret('redis_password')),
        'DATABASE': int(os.environ.get('REDIS_DATABASE', 0)),
        'DEFAULT_TIMEOUT': int(os.environ.get('REDIS_TIMEOUT', 300)),
        'SSL': os.environ.get('REDIS_SSL', 'False').lower() == 'true',
    },
    'caching': {
        'HOST': os.environ.get('REDIS_CACHE_HOST', os.environ.get('REDIS_HOST', 'localhost')),
        'PORT': int(os.environ.get('REDIS_CACHE_PORT', os.environ.get('REDIS_PORT', 6379))),
        'PASSWORD': os.environ.get('REDIS_CACHE_PASSWORD', os.environ.get('REDIS_PASSWORD', read_secret('redis_cache_password'))),
        'DATABASE': int(os.environ.get('REDIS_CACHE_DATABASE', 1)),
        'DEFAULT_TIMEOUT': int(os.environ.get('REDIS_CACHE_TIMEOUT', os.environ.get('REDIS_TIMEOUT', 300))),
        'SSL': os.environ.get('REDIS_CACHE_SSL', os.environ.get('REDIS_SSL', 'False')).lower() == 'true',
    },
}

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

# Optionally display a persistent banner at the top and/or bottom of every page. HTML is allowed. To display the same
# content in both banners, define BANNER_TOP and set BANNER_BOTTOM = BANNER_TOP.
BANNER_TOP = os.environ.get('BANNER_TOP', '')
BANNER_BOTTOM = os.environ.get('BANNER_BOTTOM', '')

# Text to include on the login page above the login form. HTML is allowed.
BANNER_LOGIN = os.environ.get('BANNER_LOGIN', '')

# Base URL path if accessing NetBox within a directory. For example, if installed at http://example.com/netbox/, set:
# BASE_PATH = 'netbox/'
BASE_PATH = os.environ.get('BASE_PATH', '')

# Cache timeout in seconds. Set to 0 to dissable caching. Defaults to 900 (15 minutes)
CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 900))

# Maximum number of days to retain logged changes. Set to 0 to retain changes indefinitely. (Default: 90)
CHANGELOG_RETENTION = int(os.environ.get('CHANGELOG_RETENTION', 90))

# API Cross-Origin Resource Sharing (CORS) settings. If CORS_ORIGIN_ALLOW_ALL is set to True, all origins will be
# allowed. Otherwise, define a list of allowed origins using either CORS_ORIGIN_WHITELIST or
# CORS_ORIGIN_REGEX_WHITELIST. For more information, see https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = os.environ.get('CORS_ORIGIN_ALLOW_ALL', 'False').lower() == 'true'
CORS_ORIGIN_WHITELIST = list(filter(None, os.environ.get('CORS_ORIGIN_WHITELIST', 'https://localhost').split(' ')))
CORS_ORIGIN_REGEX_WHITELIST = [re.compile(r) for r in list(filter(None, os.environ.get('CORS_ORIGIN_REGEX_WHITELIST', '').split(' ')))]

# Set to True to enable server debugging. WARNING: Debugging introduces a substantial performance penalty and may reveal
# sensitive information about your installation. Only enable debugging while performing testing. Never enable debugging
# on a production system.
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Email settings
EMAIL = {
    'SERVER': os.environ.get('EMAIL_SERVER', 'localhost'),
    'PORT': int(os.environ.get('EMAIL_PORT', 25)),
    'USERNAME': os.environ.get('EMAIL_USERNAME', ''),
    'PASSWORD': os.environ.get('EMAIL_PASSWORD', read_secret('email_password')),
    'TIMEOUT': int(os.environ.get('EMAIL_TIMEOUT', 10)),  # seconds
    'FROM_EMAIL': os.environ.get('EMAIL_FROM', ''),
    'USE_SSL': os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true',
    'USE_TLS': os.environ.get('EMAIL_USE_TLS', 'False').lower() == 'true',
    'SSL_CERTFILE': os.environ.get('EMAIL_SSL_CERTFILE', ''),
    'SSL_KEYFILE': os.environ.get('EMAIL_SSL_KEYFILE', ''),
}

# Enforcement of unique IP space can be toggled on a per-VRF basis.
# To enforce unique IP space within the global table (all prefixes and IP addresses not assigned to a VRF),
# set ENFORCE_GLOBAL_UNIQUE to True.
ENFORCE_GLOBAL_UNIQUE = os.environ.get('ENFORCE_GLOBAL_UNIQUE', 'False').lower() == 'true'

# Exempt certain models from the enforcement of view permissions. Models listed here will be viewable by all users and
# by anonymous users. List models in the form `<app>.<model>`. Add '*' to this list to exempt all models.
EXEMPT_VIEW_PERMISSIONS = list(filter(None, os.environ.get('EXEMPT_VIEW_PERMISSIONS', '').split(' ')))

# Enable custom logging. Please see the Django documentation for detailed guidance on configuring custom logs:
#   https://docs.djangoproject.com/en/1.11/topics/logging/
LOGGING = {}

# Setting this to True will permit only authenticated users to access any part of NetBox. By default, anonymous users
# are permitted to access most data in NetBox (excluding secrets) but not make any changes.
LOGIN_REQUIRED = os.environ.get('LOGIN_REQUIRED', 'False').lower() == 'true'

# Setting this to True will display a "maintenance mode" banner at the top of every page.
MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE', 'False').lower() == 'true'

# An API consumer can request an arbitrary number of objects =by appending the "limit" parameter to the URL (e.g.
# "?limit=1000"). This setting defines the maximum limit. Setting it to 0 or None will allow an API consumer to request
# all objects by specifying "?limit=0".
MAX_PAGE_SIZE = int(os.environ.get('MAX_PAGE_SIZE', 1000))

# The file path where uploaded media such as image attachments are stored. A trailing slash is not needed. Note that
# the default value of this setting is derived from the installed location.
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))

# Expose Prometheus monitoring metrics at the HTTP endpoint '/metrics'
METRICS_ENABLED = os.environ.get('METRICS_ENABLED', 'False').lower() == 'true'

# Credentials that NetBox will use to access live devices.
NAPALM_USERNAME = os.environ.get('NAPALM_USERNAME', '')
NAPALM_PASSWORD = os.environ.get('NAPALM_PASSWORD', read_secret('napalm_password'))

# NAPALM timeout (in seconds). (Default: 30)
NAPALM_TIMEOUT = int(os.environ.get('NAPALM_TIMEOUT', 30))

# NAPALM optional arguments (see http://napalm.readthedocs.io/en/latest/support/#optional-arguments). Arguments must
# be provided as a dictionary.
NAPALM_ARGS = {}

# Determine how many objects to display per page within a list. (Default: 50)
PAGINATE_COUNT = int(os.environ.get('PAGINATE_COUNT', 50))

# Plugins
PLUGINS = [
    'netbox_virtual_circuit_plugin',
    'netbox_bgp',
]

# When determining the primary IP address for a device, IPv6 is preferred over IPv4 by default. Set this to True to
# prefer IPv4 instead.
PREFER_IPV4 = os.environ.get('PREFER_IPV4', 'False').lower() == 'true'

# This determines how often the GitHub API is called to check the latest release of NetBox in seconds. Must be at least 1 hour.
RELEASE_CHECK_TIMEOUT = os.environ.get('RELEASE_CHECK_TIMEOUT', 24 * 3600)

# This repository is used to check whether there is a new release of NetBox available. Set to None to disable the
# version check or use the URL below to check for release in the official NetBox repository.
# https://api.github.com/repos/netbox-community/netbox/releases
RELEASE_CHECK_URL = os.environ.get('RELEASE_CHECK_URL', None)

# The file path where custom reports will be stored. A trailing slash is not needed. Note that the default value of
# this setting is derived from the installed location.
REPORTS_ROOT = os.environ.get('REPORTS_ROOT', '/etc/netbox/reports')

# The file path where custom scripts will be stored. A trailing slash is not needed. Note that the default value of
# this setting is derived from the installed location.
SCRIPTS_ROOT = os.environ.get('SCRIPTS_ROOT', '/etc/netbox/scripts')

# Time zone (default: UTC)
TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')

# Date/time formatting. See the following link for supported formats:
# https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
DATE_FORMAT = os.environ.get('DATE_FORMAT', 'N j, Y')
SHORT_DATE_FORMAT = os.environ.get('SHORT_DATE_FORMAT', 'Y-m-d')
TIME_FORMAT = os.environ.get('TIME_FORMAT', 'g:i a')
SHORT_TIME_FORMAT = os.environ.get('SHORT_TIME_FORMAT', 'H:i:s')
DATETIME_FORMAT = os.environ.get('DATETIME_FORMAT', 'N j, Y g:i a')
SHORT_DATETIME_FORMAT = os.environ.get('SHORT_DATETIME_FORMAT', 'Y-m-d H:i')
