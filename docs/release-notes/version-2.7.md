# v2.7.0 (FUTURE)

## New Features

### Enhanced Device Type Import ([#451](https://github.com/netbox-community/netbox/issues/451))

NetBox now supports the import of device types and related component templates using a YAML- or JSON-based definition.
For example, the following will create a new device type with four network interfaces, two power ports, and a console
port:

```yaml
manufacturer: Acme
model: Packet Shooter 9000
slug: packet-shooter-9000
u_height: 1
interfaces:
  - name: ge-0/0/0
    type: 1000base-t
  - name: ge-0/0/1
    type: 1000base-t
  - name: ge-0/0/2
    type: 1000base-t
  - name: ge-0/0/3
    type: 1000base-t
power-ports:
  - name: PSU0
  - name: PSU1
console-ports:
  - name: Console
```

This new functionality replaces the existing CSV-based import form, which did not allow for component template import.

## Changes

### Topology Maps Removed ([#2745](https://github.com/netbox-community/netbox/issues/2745))

The topology maps feature has been removed to help focus NetBox development efforts.

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
* [#3455](https://github.com/digitalocean/netbox/issues/3455) - Add tenant assignment to cluster
* [#3538](https://github.com/digitalocean/netbox/issues/3538) - 

## API Changes

* Introduced `/api/extras/scripts/` endpoint for retreiving and executing custom scripts
* virtualization.Cluster: Added field `tenant`
