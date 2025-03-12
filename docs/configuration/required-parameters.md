# Required Configuration Settings

## ALLOWED_HOSTS

This is a list of valid fully-qualified domain names (FQDNs) and/or IP addresses that can be used to reach the NetBox service. Usually this is the same as the hostname for the NetBox server, but can also be different; for example, when using a reverse proxy serving the NetBox website under a different FQDN than the hostname of the NetBox server. To help guard against [HTTP Host header attacks](https://docs.djangoproject.com/en/3.0/topics/security/#host-headers-virtual-hosting), NetBox will not permit access to the server via any other hostnames (or IPs).

!!! note
    This parameter must always be defined as a list or tuple, even if only a single value is provided.

The value of this option is also used to set `CSRF_TRUSTED_ORIGINS`, which restricts POST requests to the same set of hosts (more about this [here](https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-CSRF_TRUSTED_ORIGINS)). Keep in mind that NetBox, by default, sets `USE_X_FORWARDED_HOST` to true, which means that if you're using a reverse proxy, it's the FQDN used to reach that reverse proxy which needs to be in this list (more about this [here](https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts)).

Example:

```
ALLOWED_HOSTS = ['netbox.example.com', '192.0.2.123']
```

If you are not yet sure what the domain name and/or IP address of the NetBox installation will be, and are comfortable accepting the risks in doing so, you can set this to a wildcard (asterisk) to allow all host values:

```
ALLOWED_HOSTS = ['*']
```

---

## DATABASE

NetBox requires access to a PostgreSQL 13 or later database service to store data. This service can run locally on the NetBox server or on a remote system. The following parameters must be defined within the `DATABASE` dictionary:

* `NAME` - Database name
* `USER` - PostgreSQL username
* `PASSWORD` - PostgreSQL password
* `HOST` - Name or IP address of the database server (use `localhost` if running locally)
* `PORT` - TCP port of the PostgreSQL service; leave blank for default port (TCP/5432)
* `CONN_MAX_AGE` - Lifetime of a [persistent database connection](https://docs.djangoproject.com/en/stable/ref/databases/#persistent-connections), in seconds (300 is the default)
* `ENGINE` - The database backend to use; must be a PostgreSQL-compatible backend (e.g. `django.db.backends.postgresql`)

Example:

```python
DATABASE = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'netbox',               # Database name
    'USER': 'netbox',               # PostgreSQL username
    'PASSWORD': 'J5brHrAXFLQSif0K', # PostgreSQL password
    'HOST': 'localhost',            # Database server
    'PORT': '',                     # Database port (leave blank for default)
    'CONN_MAX_AGE': 300,            # Max database connection age
}
```

!!! note
    NetBox supports all PostgreSQL database options supported by the underlying Django framework. For a complete list of available parameters, please see [the Django documentation](https://docs.djangoproject.com/en/stable/ref/settings/#databases).

!!! warning
    Make sure to use a PostgreSQL-compatible backend for the ENGINE setting. If you don't specify an ENGINE, the default will be django.db.backends.postgresql.

---

## REDIS

[Redis](https://redis.io/) is a lightweight in-memory data store similar to memcached. NetBox employs Redis for background task queuing and other features.

Redis is configured using a configuration setting similar to `DATABASE` and these settings are the same for both of the `tasks` and `caching` subsections:

* `HOST` - Name or IP address of the Redis server (use `localhost` if running locally)
* `PORT` - TCP port of the Redis service; leave blank for default port (6379)
* `USERNAME` - Redis username (if set)
* `PASSWORD` - Redis password (if set)
* `DATABASE` - Numeric database ID
* `SSL` - Use SSL connection to Redis
* `INSECURE_SKIP_TLS_VERIFY` - Set to `True` to **disable** TLS certificate verification (not recommended)

An example configuration is provided below:

```python
REDIS = {
    'tasks': {
        'HOST': 'redis.example.com',
        'PORT': 1234,
        'USERNAME': 'netbox',
        'PASSWORD': 'foobar',
        'DATABASE': 0,
        'SSL': False,
    },
    'caching': {
        'HOST': 'localhost',
        'PORT': 6379,
        'USERNAME': '',
        'PASSWORD': '',
        'DATABASE': 1,
        'SSL': False,
    }
}
```

!!! warning
    It is highly recommended to keep the task and cache databases separate. Using the same database number on the
    same Redis instance for both may result in queued background tasks being lost during cache flushing events.

### UNIX Socket Support

Redis may alternatively be configured by specifying a complete URL instead of individual components. This approach supports the use of a UNIX socket connection. For example:

```python
REDIS = {
    'tasks': {
        'URL': 'unix:///run/redis-netbox/redis.sock?db=0'
    },
    'caching': {
        'URL': 'unix:///run/redis-netbox/redis.sock?db=1'
    },
}
```

### Using Redis Sentinel

If you are using [Redis Sentinel](https://redis.io/topics/sentinel) for high-availability purposes, there is minimal 
configuration necessary to convert NetBox to recognize it. It requires the removal of the `HOST` and `PORT` keys from 
above and the addition of three new keys.

* `SENTINELS`: List of tuples or tuple of tuples with each inner tuple containing the name or IP address 
of the Redis server and port for each sentinel instance to connect to
* `SENTINEL_SERVICE`: Name of the master / service to connect to
* `SENTINEL_TIMEOUT`: Connection timeout, in seconds

Example:

```python
REDIS = {
    'tasks': {
        'SENTINELS': [('mysentinel.redis.example.com', 6379)],
        'SENTINEL_SERVICE': 'netbox',
        'SENTINEL_TIMEOUT': 10,
        'PASSWORD': '',
        'DATABASE': 0,
        'SSL': False,
    },
    'caching': {
        'SENTINELS': [
            ('mysentinel.redis.example.com', 6379),
            ('othersentinel.redis.example.com', 6379)
        ],
        'SENTINEL_SERVICE': 'netbox',
        'PASSWORD': '',
        'DATABASE': 1,
        'SSL': False,
    }
}
```

!!! note
    It is permissible to use Sentinel for only one database and not the other.

---

## SECRET_KEY

This is a secret, pseudorandom string used to assist in the creation new cryptographic hashes for passwords and HTTP cookies. The key defined here should not be shared outside the configuration file. `SECRET_KEY` can be changed at any time without impacting stored data, however be aware that doing so will invalidate all existing user sessions. NetBox deployments comprising multiple nodes must have the same secret key configured on all nodes.

`SECRET_KEY` **must** be at least 50 characters in length, and should contain a mix of letters, digits, and symbols. The script located at `$INSTALL_ROOT/netbox/generate_secret_key.py` may be used to generate a suitable key. Please note that this key is **not** used directly for hashing user passwords or for the encrypted storage of secret data in NetBox.
