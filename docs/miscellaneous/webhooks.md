# NetBox Webhook Backend

NetBox includes the ability to send outbound requests to external webhooks upon certain model events occuring, however this functionality is disabled by default and requires some admin interaction to setup.

When enabled, the user may subscribe webhooks to certain model events. These events include when a model is either created, updated, or deleted. More than one webhook my be registered to a particular model and/or event type.

## Allowed Models

The models which may have webhooks registered to them are:

DCIM:

- Site
- Rack
- RackGroup
- Device
- Interface

IPAM:

- VRF
- IPAddress
- Prefix
- Aggregate
- VLAN
- VLANGroup
- Service

Tenancy:

- Tenant
- TenantGroup

Ciruits:

- Circuit
- Provider

Virtualization:

- Cluster
- ClusterGroup
- VirtualMachine

## Defining Webhooks

The [webhook model](../data-model/extras/#webhooks) is used to define a webhook. In general an event type, registered models, and payload url are needed. When a matching event on a registered model occurs, a HTTP POST request is made to the payload url.

Webhooks are created and updated under extras in the admin site.

### Request

The webhook POST request is structured as so (assuming `application/json` as the Content-Type):

```no-highlight
{
    "event": "created",
    "signal_received_timestamp": 1508769597,
    "model": "Site"
    "data": {
        ...
    }
}
```

`data` is the serialized representation of the model instance(s) from the event. The same serializers from the NetBox API are used. So an example of the payload for a Site delete event would be:

```no-highlight
{
    "event": "deleted",
    "signal_received_timestamp": 1508781858.544069,
    "model": "Site",
    "data": {
        "asn": None,
        "comments": "",
        "contact_email": "",
        "contact_name": "",
        "contact_phone": "",
        "count_circuits": 0,
        "count_devices": 0,
        "count_prefixes": 0,
        "count_racks": 0,
        "count_vlans": 0,
        "custom_fields": {},
        "facility": "",
        "id": 54,
        "name": "test",
        "physical_address": "",
        "region": None,
        "shipping_address": "",
        "slug": "test",
        "tenant": None
    }
}
```

A request is considered successful if the response status code is any one of a list of "good" statuses defined in the [requests library](https://github.com/requests/requests/blob/205755834d34a8a6ecf2b0b5b2e9c3e6a7f4e4b6/requests/models.py#L688), otherwise the request is marked as having failed. The user may manually retry a failed request.

## Installation

The webhook backend feature is considered an "advanced" feature and requires some extra effort to get it running. This is due the fact that a background worker is needed to process events in a non blocking way, i.e. the webhooks are sent in the background as not to interrupt what a user is doing in the NetBox foreground.

To do this, you must install [Redis](https://redis.io/) or simply be able to connect to an existing redis server. Redis is a lightweight, in memory database. Redis is used as a means of persistence between NetBox and the background worker for the queue of webhooks to be sent. It can be installed through most package managers.

```no-highlight
# apt-get install redis-server
```

The only other component needed is [Django-rq](https://github.com/ui/django-rq) which implements [python-rq](http://python-rq.org/) in a native Django context. This should be done from the same place NetBox is installed, i.e. the same python namespace where you run the upgrade script. Python-rq is a simple background job queueing system sitting on top of redis.

```no-highlight
pip install django-rq
```

As mentioned before, the feature requires running a background process. This means we need to run another process along side the NetBox application. We can do this conveniently by modifying the supervisord unit used to run NetBox. Taking the configuration provided from the [installation guide](../installation/web-server/#supervisord_installation) modify it to look like this:

```no-highlight
[program:netbox-core]
command = gunicorn -c /opt/netbox/gunicorn_config.py netbox.wsgi
directory = /opt/netbox/netbox/
user = www-data

[program:netbox-webhook-backend]
command = python3 /opt/netbox/netbox/manage.py rqworker
directory = /opt/netbox/netbox/
user = www-data

[group:netbox]
programs=netbox-core,netbox-webhook-backend
```

!!! note
    `[program:netbox]` was changed to `[program:netbox-core]`

This allows you to control both the NetBox application and the background worker as one unit.

Then, restart the supervisor service to detect the changes:

```no-highlight
# service supervisor restart
```

!!! note
    Now any time you start or stop NetBox using `supervisorctl`, you will need to refer to the
    NetBox process as `netbox:*` (before this was just `netbox`). This is due to the fact that
    we are now running multiple processes with supervisor, and `netbox:*` tells supervisor to
    act on all NetBox processes (`netbox-core` and `netbox-webhook-backend` in this case).

Now you need only add the configuration settings to connect to redis and enable the webhook backend feature.

- In your `configuration.py` Set [WEBHOOKS_ENABLED](../configuration/optional-settings/#webhooks_enabled) to `True`.
- If needed, set the optional redis connection settings. By default, they will allow connecting to DB 0 on a locally installed redis server with no password.
  - [REDIS_DB](../configuration/optional-settings/#redis_db)
  - [REDIS_DEFAULT_TIMEOUT](../configuration/optional-settings/#redis_default_timeout)
  - [REDIS_HOST](../configuration/optional-settings/#redis_host)
  - [REDIS_PASSWORD](../configuration/optional-settings/#redis_password)
  - [REDIS_PORT](../configuration/optional-settings/#redis_port)

Now you may restart NetBox as normal and the webhook backend should start running!

```no-highlight
# sudo supervisorctl restart netbox:*
```

## Backend Status

Django-rq includes a status page in the admin site which can be used to view the result of processed webhooks and manually retry any failed webhooks. Access it from http://netbox.local/admin/webhook-backend-status/.
