from importlib import import_module
from os import environ

import ldap
from django_auth_ldap.config import LDAPSearch


# Read secret from file
def _read_secret(secret_name, default=None):
    try:
        f = open('/run/secrets/' + secret_name, 'r', encoding='utf-8')
    except EnvironmentError:
        return default
    else:
        with f:
            return f.readline().strip()

# Import and return the group type based on string name
def _import_group_type(group_type_name):
    mod = import_module('django_auth_ldap.config')
    try:
        return getattr(mod, group_type_name)()
    except:
        return None

# Server URI
AUTH_LDAP_SERVER_URI = environ.get('AUTH_LDAP_SERVER_URI', '')

# The following may be needed if you are binding to Active Directory.
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0
}

# Set the DN and password for the NetBox service account.
AUTH_LDAP_BIND_DN = environ.get('AUTH_LDAP_BIND_DN', '')
AUTH_LDAP_BIND_PASSWORD = _read_secret('auth_ldap_bind_password', environ.get('AUTH_LDAP_BIND_PASSWORD', ''))

# Set a string template that describes any user’s distinguished name based on the username.
AUTH_LDAP_USER_DN_TEMPLATE = environ.get('AUTH_LDAP_USER_DN_TEMPLATE', None)

# Enable STARTTLS for ldap authentication.
AUTH_LDAP_START_TLS = environ.get('AUTH_LDAP_START_TLS', 'False').lower() == 'true'

# Include this setting if you want to ignore certificate errors. This might be needed to accept a self-signed cert.
# Note that this is a NetBox-specific setting which sets:
#     ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
LDAP_IGNORE_CERT_ERRORS = environ.get('LDAP_IGNORE_CERT_ERRORS', 'False').lower() == 'true'

AUTH_LDAP_USER_SEARCH_BASEDN = environ.get('AUTH_LDAP_USER_SEARCH_BASEDN', '')
AUTH_LDAP_USER_SEARCH_ATTR = environ.get('AUTH_LDAP_USER_SEARCH_ATTR', 'sAMAccountName')
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    AUTH_LDAP_USER_SEARCH_BASEDN,
    ldap.SCOPE_SUBTREE,
    "(" + AUTH_LDAP_USER_SEARCH_ATTR + "=%(user)s)"
)

# This search ought to return all groups to which the user belongs. django_auth_ldap uses this to determine group
# heirarchy.
AUTH_LDAP_GROUP_SEARCH_BASEDN = environ.get('AUTH_LDAP_GROUP_SEARCH_BASEDN', '')
AUTH_LDAP_GROUP_SEARCH_CLASS = environ.get('AUTH_LDAP_GROUP_SEARCH_CLASS', 'group')
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(AUTH_LDAP_GROUP_SEARCH_BASEDN, ldap.SCOPE_SUBTREE,
                                    "(objectClass=" + AUTH_LDAP_GROUP_SEARCH_CLASS + ")")
AUTH_LDAP_GROUP_TYPE = _import_group_type(environ.get('AUTH_LDAP_GROUP_TYPE', 'GroupOfNamesType'))

# Define a group required to login.
AUTH_LDAP_REQUIRE_GROUP = environ.get('AUTH_LDAP_REQUIRE_GROUP_DN')

# Define special user types using groups. Exercise great caution when assigning superuser status.
AUTH_LDAP_USER_FLAGS_BY_GROUP = {}

if AUTH_LDAP_REQUIRE_GROUP is not None:
    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_active": environ.get('AUTH_LDAP_REQUIRE_GROUP_DN', ''),
        "is_staff": environ.get('AUTH_LDAP_IS_ADMIN_DN', ''),
        "is_superuser": environ.get('AUTH_LDAP_IS_SUPERUSER_DN', '')
    }

# For more granular permissions, we can map LDAP groups to Django groups.
AUTH_LDAP_FIND_GROUP_PERMS = environ.get('AUTH_LDAP_FIND_GROUP_PERMS', 'True').lower() == 'true'
AUTH_LDAP_MIRROR_GROUPS = environ.get('AUTH_LDAP_MIRROR_GROUPS', '').lower() == 'true'

# Cache groups for one hour to reduce LDAP traffic
AUTH_LDAP_CACHE_TIMEOUT = int(environ.get('AUTH_LDAP_CACHE_TIMEOUT', 3600))

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": environ.get('AUTH_LDAP_ATTR_FIRSTNAME', 'givenName'),
    "last_name": environ.get('AUTH_LDAP_ATTR_LASTNAME', 'sn'),
    "email": environ.get('AUTH_LDAP_ATTR_MAIL', 'mail')
}
