# LDAP Configuration

This guide explains how to implement LDAP authentication using an external server. User authentication will fall back to built-in Django users in the event of a failure.

## Install Requirements

### Install System Packages

On Ubuntu:

```no-highlight
sudo apt install -y libldap2-dev libsasl2-dev libssl-dev
```

On CentOS:

```no-highlight
sudo yum install -y openldap-devel
```

### Install django-auth-ldap

Activate the Python virtual environment and install the `django-auth-ldap` package using pip:

```no-highlight
source /opt/netbox/venv/bin/activate
pip3 install django-auth-ldap
```

Once installed, add the package to `local_requirements.txt` to ensure it is re-installed during future rebuilds of the virtual environment:

```no-highlight
sudo sh -c "echo 'django-auth-ldap' >> /opt/netbox/local_requirements.txt"
```

## Configuration

First, enable the LDAP authentication backend in `configuration.py`. (Be sure to overwrite this definition if it is already set to `RemoteUserBackend`.)

```python
REMOTE_AUTH_BACKEND = 'netbox.authentication.LDAPBackend'
```

Next, create a file in the same directory as `configuration.py` (typically `/opt/netbox/netbox/netbox/`) named `ldap_config.py`. Define all of the parameters required below in `ldap_config.py`. Complete documentation of all `django-auth-ldap` configuration options is included in the project's [official documentation](https://django-auth-ldap.readthedocs.io/).

### General Server Configuration

!!! info
    When using Windows Server 2012 you may need to specify a port on `AUTH_LDAP_SERVER_URI`. Use `3269` for secure, or `3268` for non-secure.

```python
import ldap

# Server URI
AUTH_LDAP_SERVER_URI = "ldaps://ad.example.com"

# The following may be needed if you are binding to Active Directory.
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0
}

# Set the DN and password for the NetBox service account.
AUTH_LDAP_BIND_DN = "CN=NETBOXSA, OU=Service Accounts,DC=example,DC=com"
AUTH_LDAP_BIND_PASSWORD = "demo"

# Include this setting if you want to ignore certificate errors. This might be needed to accept a self-signed cert.
# Note that this is a NetBox-specific setting which sets:
#     ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
LDAP_IGNORE_CERT_ERRORS = True
```

STARTTLS can be configured by setting `AUTH_LDAP_START_TLS = True` and using the `ldap://` URI scheme.

### User Authentication

!!! info
    When using Windows Server 2012+, `AUTH_LDAP_USER_DN_TEMPLATE` should be set to None.

```python
from django_auth_ldap.config import LDAPSearch

# This search matches users with the sAMAccountName equal to the provided username. This is required if the user's
# username is not in their DN (Active Directory).
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=Users,dc=example,dc=com",
                                    ldap.SCOPE_SUBTREE,
                                    "(sAMAccountName=%(user)s)")

# If a user's DN is producible from their username, we don't need to search.
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

# You can map user attributes to Django attributes as so.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}
```

### User Groups for Permissions

!!! info
    When using Microsoft Active Directory, support for nested groups can be activated by using `NestedGroupOfNamesType()` instead of `GroupOfNamesType()` for `AUTH_LDAP_GROUP_TYPE`. You will also need to modify the import line to use `NestedGroupOfNamesType` instead of `GroupOfNamesType` .

```python
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

# This search ought to return all groups to which the user belongs. django_auth_ldap uses this to determine group
# hierarchy.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("dc=example,dc=com", ldap.SCOPE_SUBTREE,
                                    "(objectClass=group)")
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

# Define a group required to login.
AUTH_LDAP_REQUIRE_GROUP = "CN=NETBOX_USERS,DC=example,DC=com"

# Mirror LDAP group assignments.
AUTH_LDAP_MIRROR_GROUPS = True

# Define special user types using groups. Exercise great caution when assigning superuser status.
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": "cn=active,ou=groups,dc=example,dc=com",
    "is_staff": "cn=staff,ou=groups,dc=example,dc=com",
    "is_superuser": "cn=superuser,ou=groups,dc=example,dc=com"
}

# For more granular permissions, we can map LDAP groups to Django groups.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache groups for one hour to reduce LDAP traffic
AUTH_LDAP_CACHE_TIMEOUT = 3600

```

* `is_active` - All users must be mapped to at least this group to enable authentication. Without this, users cannot log in.
* `is_staff` - Users mapped to this group are enabled for access to the administration tools; this is the equivalent of checking the "staff status" box on a manually created user. This doesn't grant any specific permissions.
* `is_superuser` - Users mapped to this group will be granted superuser status. Superusers are implicitly granted all permissions.

!!! warning
    Authentication will fail if the groups (the distinguished names) do not exist in the LDAP directory.

## Troubleshooting LDAP

`systemctl restart netbox` restarts the NetBox service, and initiates any changes made to `ldap_config.py`. If there are syntax errors present, the NetBox process will not spawn an instance, and errors should be logged to `/var/log/messages`.

For troubleshooting LDAP user/group queries, add or merge the following [logging](../configuration/optional-settings.md#logging) configuration to `configuration.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'netbox_auth_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/netbox/logs/django-ldap-debug.log',
            'maxBytes': 1024 * 500,
            'backupCount': 5,
        },
    },
    'loggers': {
        'django_auth_ldap': {
            'handlers': ['netbox_auth_log'],
            'level': 'DEBUG',
        },
    },
}
```

Ensure the file and path specified in logfile exist and are writable and executable by the application service account. Restart the netbox service and attempt to log into the site to trigger log entries to this file.
