v2.7.0 (FUTURE)

## Changes

### Redis Configuration ([#3282](https://github.com/netbox-community/netbox/issues/3282))

v2.6.0 introduced caching and added the `CACHE_DATABASE` option to the existing `REDIS` database configuration section.
This did not however, allow for using two different Redis connections for the seperate caching and webhooks features.
This change separates the Redis connection configurations in the `REDIS` section into distinct `webhooks` and `caching` subsections.
This requires modification of the `REDIS` section of the `configuration.py` file as follows:

Old Redis configuration:
```python
REDIS = {
    'HOST': 'localhost',
    'PORT': 6379,
    'PASSWORD': '',
    'DATABASE': 0,
    'CACHE_DATABASE': 1,
    'DEFAULT_TIMEOUT': 300,
    'SSL': False,
}
```

New Redis configuration:
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

Note that `CACHE_DATABASE` has been removed and the connection settings have been duplicated for both `webhooks` and `caching`.
This allows the user to make use of separate Redis instances and/or databases if desired.
Full connection details are required in both sections, even if they are the same.

## Enhancements

* [#2902](https://github.com/digitalocean/netbox/issues/2902) - Replace supervisord with systemd
