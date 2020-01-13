# v2.7.0 (FUTURE)

**Note:** NetBox v2.7 is the last major release that will support Python 3.5. Beginning with NetBox v2.8, Python 3.6 or
higher will be required.

## New Features

### Enhanced Device Type Import ([#451](https://github.com/netbox-community/netbox/issues/451))

NetBox now supports the import of device types and related component templates using a definition written in YAML or
JSON. For example, the following will create a new device type with four network interfaces, two power ports, and a
console port:

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

### Bulk Import of Device Components ([#822](https://github.com/netbox-community/netbox/issues/822))

NetBox now supports the bulk import of device components such as console ports, power ports, and interfaces across
multiple devices. Device components can be imported in CSV-format.

Here's an example bulk import of interfaces to several devices:

```
device,name,type
Switch1,Vlan100,Virtual
Switch1,Vlan200,Virtual
Switch2,Vlan100,Virtual
Switch2,Vlan200,Virtual
```

### External File Storage ([#1814](https://github.com/netbox-community/netbox/issues/1814))

In prior releases, the only option for storing uploaded files (e.g. image attachments) was to save them to the local
filesystem on the NetBox server. This release introduces support for several remote storage backends provided by the
[`django-storages`](https://django-storages.readthedocs.io/en/stable/) library. These include:

* Amazon S3
* ApacheLibcloud
* Azure Storage
* DigitalOcean Spaces
* Dropbox
* FTP
* Google Cloud Storage
* SFTP

To enable remote file storage, first install `django-storages`:

```
pip install django-storages
```

Then, set the appropriate storage backend and its configuration in `configuration.py`. Here's an example using Amazon
S3:

```python
STORAGE_BACKEND = 'storages.backends.s3boto3.S3Boto3Storage'
STORAGE_CONFIG = {
    'AWS_ACCESS_KEY_ID': '<Key>',
    'AWS_SECRET_ACCESS_KEY': '<Secret>',
    'AWS_STORAGE_BUCKET_NAME': 'netbox',
    'AWS_S3_REGION_NAME': 'eu-west-1',
}
```

Thanks to [@steffann](https://github.com/steffann) for contributing this work!

## Changes

### Rack Elevations Rendered via SVG ([#2248](https://github.com/netbox-community/netbox/issues/2248))

NetBox v2.7 introduces a new method of rendering rack elevations as an
[SVG](https://en.wikipedia.org/wiki/Scalable_Vector_Graphics) via a REST API endpoint. This replaces the prior method of
rendering elevations using pure HTML which was cumbersome and had several shortcomings. Allowing elevations to be
rendered as an SVG image in the API allows users to retrieve and make use of the drawings in their own tooling. This
also opens the door to other feature requests related to rack elevations in the NetBox backlog.

This feature implements a new REST API endpoint:

```
/api/dcim/racks/<id>/elevation/
```

By default, this endpoint returns a paginated JSON response representing each rack unit in the given elevation. This is
the same response returned by the rack units detail endpoint and for this reason the rack units endpoint has been
deprecated and will be removed in v2.8 (see [#3753](https://github.com/netbox-community/netbox/issues/3753)):

```
/api/dcim/racks/<id>/units/
```

In order to render the elevation as an SVG, include the `render=svg` query parameter in the request. You may also
control the width of the elevation drawing in pixels with `unit_width=<width in pixels>` and the height of each rack
unit with `unit_height=<height in pixels>`. The `unit_width` defaults to `230` and the `unit_height` default to `20`
which produces elevations the same size as those that appear in the NetBox Web UI. The query parameter `face` is used to
request either the `front` or `rear` of the elevation and defaults to `front`.

Here is an example of the request url for an SVG rendering using the default parameters to render the front of the
elevation:

```
/api/dcim/racks/<id>/elevation/?render=svg
```

Here is an example of the request url for an SVG rendering of the rear of the elevation having a width of 300 pixels and
per unit height of 35 pixels:

```
/api/dcim/racks/<id>/elevation/?render=svg&face=rear&unit_width=300&unit_height=35
```

Thanks to [@hellerve](https://github.com/hellerve) for doing the heavy lifting on this!

### Topology Maps Removed ([#2745](https://github.com/netbox-community/netbox/issues/2745))

The topology maps feature has been removed to help focus NetBox development efforts.

### Redis Configuration ([#3282](https://github.com/netbox-community/netbox/issues/3282))

v2.6.0 introduced caching and added the `CACHE_DATABASE` option to the existing `REDIS` database configuration section.
This did not however, allow for using two different Redis connections for the seperate caching and webhooks features.
This change separates the Redis connection configurations in the `REDIS` section into distinct `webhooks` and `caching`
subsections. This requires modification of the `REDIS` section of the `configuration.py` file as follows:

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

Note that `CACHE_DATABASE` has been removed and the connection settings have been duplicated for both `webhooks` and
`caching`. This allows the user to make use of separate Redis instances and/or databases if desired. Full connection
details are required in both sections, even if they are the same.

### WEBHOOKS_ENABLED Configuration Setting Removed ([#3408](https://github.com/netbox-community/netbox/issues/3408))

As `django-rq` is now a required library, NetBox assumes that the RQ worker process is running. The installation and
upgrade documentation has been updated to reflect this, and the `WEBHOOKS_ENABLED` configuration parameter is no longer
used. Please ensure that both the NetBox WSGI service and the RQ worker process are running on all production
installations.

### API Choice Fields Now Use String Values ([#3569](https://github.com/netbox-community/netbox/issues/3569))

NetBox's REST API presents fields which reference a particular choice as a dictionary with two keys: `value` and
`label`. In previous versions, `value` was an integer which represented the particular choice in the database. This has
been changed to a more human-friendly "slug" string, which is essentially a simplified version of the choice's `label`.

For example, The site status field was previously represented as:

```json
"status": {
    "value": 1,
    "label": "Active"
},
```

Beginning with v2.7.0, it now looks like this:

```json
"status": {
    "value": "active",
    "label": "Active"
},
```

This change allows for much more intuitive representation of values, and obviates the need for API consumers to maintain
a mapping of static integer values.

Note that that all v2.7 releases will continue to accept the legacy integer values in write requests (POST, PUT, and
PATCH) to maintain backward compatibility. This behavior will be discontinued beginning in v2.8.0.

## Enhancements

* [#33](https://github.com/digitalocean/netbox/issues/33) - Add ability to clone objects (pre-populate form fields)
* [#648](https://github.com/digitalocean/netbox/issues/648) - Pre-populate forms when selecting "create and add another"
* [#792](https://github.com/digitalocean/netbox/issues/792) - Add power port and power outlet types
* [#1865](https://github.com/digitalocean/netbox/issues/1865) - Add console port and console server port types
* [#2669](https://github.com/digitalocean/netbox/issues/2669) - Relax uniqueness constraint on device and VM names
* [#2902](https://github.com/digitalocean/netbox/issues/2902) - Replace `supervisord` with `systemd`
* [#3455](https://github.com/digitalocean/netbox/issues/3455) - Add tenant assignment to cluster
* [#3520](https://github.com/digitalocean/netbox/issues/3520) - Add Jinja2 template support for Graphs
* [#3564](https://github.com/digitalocean/netbox/issues/3564) - Add list views for device components
* [#3538](https://github.com/digitalocean/netbox/issues/3538) - Introduce a REST API endpoint for executing custom
  scripts
* [#3655](https://github.com/digitalocean/netbox/issues/3655) - Add `description` field to organizational models
* [#3664](https://github.com/digitalocean/netbox/issues/3664) - Enable applying configuration contexts by tags
* [#3706](https://github.com/digitalocean/netbox/issues/3706) - Increase `available_power` maximum value on PowerFeed
* [#3731](https://github.com/digitalocean/netbox/issues/3731) - Change Graph.type to a ContentType foreign key field
* [#3801](https://github.com/digitalocean/netbox/issues/3801) - Use YAML for export of device types

## Bug Fixes (From Beta)

* [#3868](https://github.com/digitalocean/netbox/issues/3868) - Fix creation of interfaces for virtual machines
* [#3878](https://github.com/digitalocean/netbox/issues/3878) - Fix database migration for cable status field

## API Changes

* Choice fields now use human-friendly strings for their values instead of integers (see
  [#3569](https://github.com/netbox-community/netbox/issues/3569)).
* Introduced `/api/extras/scripts/` endpoint for retrieving and executing custom scripts
* circuits.CircuitType: Added field `description`
* dcim.ConsolePort: Added field `type`
* dcim.ConsolePortTemplate: Added field `type`
* dcim.ConsoleServerPort: Added field `type`
* dcim.ConsoleServerPortTemplate: Added field `type`
* dcim.DeviceRole: Added field `description`
* dcim.PowerPort: Added field `type`
* dcim.PowerPortTemplate: Added field `type`
* dcim.PowerOutlet: Added field `type`
* dcim.PowerOutletTemplate: Added field `type`
* dcim.RackRole: Added field `description`
* extras.Graph: Added field `template_language` (to indicate `django` or `jinja2`)
* extras.Graph: The `type` field has been changed to a content type foreign key. Models are specified as
  `<app>.<model>`; e.g. `dcim.site`.
* ipam.Role: Added field `description`
* secrets.SecretRole: Added field `description`
* virtualization.Cluster: Added field `tenant`
