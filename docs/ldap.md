
<h1>LDAP Authentication</h1>

This section details configuration of alternatives to standard django authentication, specifically LDAP and Active Directory.

[TOC]

# Requirements

**Install openldap-devel**

On Ubuntu:
```
sudo apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev
```
or on CentOS:
```
sudo yum install -y python-devel openldap-devel
```

**Install django-auth-ldap**
```
sudo pip install django-auth-ldap
```

# General Configuration
In this guide, all shown configuration ought to be appended to the `settings.py` file.

# Basic Setup
The following configuration adds the LDAP Authentication backend to your netbox site:
```python
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
```

# General Server Configuration
```python
# Set the server
AUTH_LDAP_SERVER_URI = "ldaps://ad.example.com"

# The following may be needed if you are binding to active directory
import ldap
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0
}

# Set the DN and password for the netbox service account
AUTH_LDAP_BIND_DN = "CN=NETBOXSA, OU=Service Accounts,DC=example,DC=com"
AUTH_LDAP_BIND_PASSWORD = "demo"
```

# User Authentication
```python
from django_auth_ldap.config import LDAPSearch
# Search for a users DN.

# This search matches users with the sAMAccountName equal to the inputed username.
# This is required if the user's username is not in their DN. (Active Directory)
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=Users,dc=example,dc=com",
                                    ldap.SCOPE_SUBTREE,
                                    "(sAMAccountName=%(user)s)")

# If a users dn is producable from their username, we don't need to search
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

# You can map user attributes to django attributes as so.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn"
}
```

# User Groups for permissions
```python
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

# This search ought to return all groups that a user may be part of.
# django_auth_ldap uses this to determine group heirarchy
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("dc=example,dc=com", ldap.SCOPE_SUBTREE,
                                    "(objectClass=group)")
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

# Define a group required to login
AUTH_LDAP_REQUIRE_GROUP = "CN=NETBOX_USERS,DC=example,DC=com"

# Define user type using groups
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": "cn=active,ou=groups,dc=example,dc=com",
    "is_staff": "cn=staff,ou=groups,dc=example,dc=com",
    "is_superuser": "cn=superuser,ou=groups,dc=example,dc=com"
}

# For more granular permissions, we can map ldap groups to django groups
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache groups for one hour to reduce ldap traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
```

# Certificate Checking
```python
# If your certificate is valid and trusted, you probably don't need to do anything
# Otherwise, see the solutions below:

# Don't check the ldap server's certificate as much
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

# Don't check the cert at all
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
```

# Logging
If authentication isn't working, you can add the following to your `settings.py`.
```python
import logging

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
```
