import os
#########################
#                       #
#   Required settings   #
#                       #
#########################

# This is a list of valid fully-qualified domain names (FQDNs) for the NetBox server. NetBox will not permit write
# access to the server via any other hostnames. The first FQDN in the list will be treated as the preferred name.
#
# Example: ALLOWED_HOSTS = ['netbox.example.com', 'netbox.internal.local']
ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS', '')]

# PostgreSQL database configuration.
DATABASE = {
    'NAME': os.environ.get('DB_NAME', 'netbox'),         # Database name
    'USER': os.environ.get('DB_USER', ''),               # PostgreSQL username
    'PASSWORD': os.environ.get('DB_PASSWORD', ''),       # PostgreSQL password
    'HOST': os.environ.get('DB_HOST', 'localhost'),      # Database server
    'PORT': os.environ.get('DB_PORT', ''),               # Database port (leave blank for default)
}

# This key is used for secure generation of random numbers and strings. It must never be exposed outside of this file.
# For optimal security, SECRET_KEY should be at least 50 characters in length and contain a mix of letters, numbers, and
# symbols. NetBox will not run without this defined. For more information, see
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY', '')

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

# Email settings
EMAIL = {
    'SERVER': os.environ.get('EMAIL_SERVER', 'localhost'),
    'PORT': os.environ.get('EMAIL_PORT', 25),
    'USERNAME': os.environ.get('EMAIL_USERNAME', ''),
    'PASSWORD': os.environ.get('EMAIL_PASSWORD', ''),
    'TIMEOUT': os.environ.get('EMAIL_TIMEOUT', 10),  # seconds
    'FROM_EMAIL': os.environ.get('EMAIL_FROM', ''),
}

# Setting this to True will permit only authenticated users to access any part of NetBox. By default, anonymous users
# are permitted to access most data in NetBox (excluding secrets) but not make any changes.
LOGIN_REQUIRED = os.environ.get('LOGIN_REQUIRED', False)

# Base URL path if accessing NetBox within a directory. For example, if installed at http://example.com/netbox/, set:
# BASE_PATH = 'netbox/'
BASE_PATH = os.environ.get('BASE_PATH', '')

# Setting this to True will display a "maintenance mode" banner at the top of every page.
MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE', False)

# Credentials that NetBox will use to access live devices.
NETBOX_USERNAME = os.environ.get('NETBOX_USERNAME', '')
NETBOX_PASSWORD = os.environ.get('NETBOX_PASSWORD', '')

# Determine how many objects to display per page within a list. (Default: 50)
PAGINATE_COUNT = os.environ.get('PAGINATE_COUNT', 50)

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
