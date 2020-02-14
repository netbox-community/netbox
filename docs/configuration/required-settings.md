# Required Configuration Settings

## ALLOWED_HOSTS

This is a list of valid fully-qualified domain names (FQDNs) that is used to reach the NetBox service. Usually this is the same as the hostname for the NetBox server, but can also be different (e.g. when using a reverse proxy serving the NetBox website under a different FQDN than the hostname of the NetBox server). NetBox will not permit access to the server via any other hostnames (or IPs). The value of this option is also used to set `CSRF_TRUSTED_ORIGINS`, which restricts `HTTP POST` to the same set of hosts (more about this [here](https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-CSRF_TRUSTED_ORIGINS)). Keep in mind that NetBox, by default, has `USE_X_FORWARDED_HOST = True` (in `netbox/netbox/settings.py`) which means that if you're using a reverse proxy, it's the FQDN used to reach that reverse proxy which needs to be in this list (more about this [here](https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts)).

Example:

```
ALLOWED_HOSTS = ['netbox.example.com', '192.0.2.123']
```

---

## DATABASE

NetBox requires access to a PostgreSQL database service to store data. This service can run locally or on a remote system. The following parameters must be defined within the `DATABASE` dictionary:

* `NAME` - Database name
* `USER` - PostgreSQL username
* `PASSWORD` - PostgreSQL password
* `HOST` - Name or IP address of the database server (use `localhost` if running locally)
* `PORT` - TCP port of the PostgreSQL service; leave blank for default port (5432)
* `CONN_MAX_AGE` - Lifetime of a [persistent database connection](https://docs.djangoproject.com/en/stable/ref/databases/#persistent-connections), in seconds (150-300 is recommended)

Example:

```python
DATABASE = {
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

---

## REDIS

[Redis](https://redis.io/) is an in-memory data store similar to memcached. While Redis has been an optional component of
NetBox since the introduction of webhooks in version 2.4, it is required starting in 2.6 to support NetBox's caching
functionality (as well as other planned features). In 2.7, the connection settings were broken down into two sections for
webhooks and caching, allowing the user to connect to different Redis instances/databases per feature.

Redis is configured using a configuration setting similar to `DATABASE` and these settings are the same for both of the `webhooks` and `caching` subsections:

* `HOST` - Name or IP address of the Redis server (use `localhost` if running locally)
* `PORT` - TCP port of the Redis service; leave blank for default port (6379)
* `PASSWORD` - Redis password (if set)
* `DATABASE` - Numeric database ID
* `DEFAULT_TIMEOUT` - Connection timeout in seconds
* `SSL` - Use SSL connection to Redis

Example:

```python
REDIS = {
    'webhooks': {
        'HOST': 'redis.example.com',
        'PORT': 1234,
        'PASSWORD': 'foobar',
        'DATABASE': 0,
        'DEFAULT_TIMEOUT': 300,
        'SSL': False,
    },
    'caching': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 1,
        'DEFAULT_TIMEOUT': 300,
        'SSL': False,
    }
}
```

!!! note
    If you are upgrading from a version prior to v2.7, please note that the Redis connection configuration settings have
    changed. Manual modification to bring the `REDIS` section inline with the above specification is necessary

!!! note
    It is highly recommended to keep the webhook and cache databases separate. Using the same database number on the
    same Redis instance for both may result in webhook processing data being lost during cache flushing events.

### Using Redis Sentinel

If you are using [Redis Sentinel](https://redis.io/topics/sentinel) for high-availability purposes, there is minimal 
configuration necessary to convert NetBox to recognize it. It requires the removal of the `HOST` and `PORT` keys from 
above and the addition of two new keys.

* `SENTINELS`: List of tuples or tuple of tuples with each inner tuple containing the name or IP address 
of the Redis server and port for each sentinel instance to connect to
* `SENTINEL_SERVICE`: Name of the master / service to connect to

Example:

```python
REDIS = {
    'webhooks': {
        'SENTINELS': [('mysentinel.redis.example.com', 6379)],
        'SENTINEL_SERVICE': 'netbox',
        'PASSWORD': '',
        'DATABASE': 0,
        'DEFAULT_TIMEOUT': 300,
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
        'DEFAULT_TIMEOUT': 300,
        'SSL': False,
    }
}
```

!!! note
    It is possible to have only one or the other Redis configurations to use Sentinel functionality. It is possible
    for example to have the webhook use sentinel via `HOST`/`PORT` and for caching to use Sentinel via 
    `SENTINELS`/`SENTINEL_SERVICE`.


---

## SECRET_KEY

This is a secret cryptographic key is used to improve the security of cookies and password resets. The key defined here should not be shared outside of the configuration file. `SECRET_KEY` can be changed at any time, however be aware that doing so will invalidate all existing sessions.

Please note that this key is **not** used for hashing user passwords or for the encrypted storage of secret data in NetBox.

`SECRET_KEY` should be at least 50 characters in length and contain a random mix of letters, digits, and symbols. The script located at `netbox/generate_secret_key.py` may be used to generate a suitable key.
