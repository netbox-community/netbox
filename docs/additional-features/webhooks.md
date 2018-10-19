# Webhooks

A webhook defines an HTTP request that is sent to an external application when certain types of objects are created, updated, and/or deleted in NetBox. When a webhook is triggered, a POST request is sent to its configured URL. This request will include a full representation of the object being modified for consumption by the receiver. Webhooks are configured via the admin UI under Extras > Webhooks.

An optional secret key can be configured for each webhook. This will append a `X-Hook-Signature` header to the request, consisting of a HMAC (SHA-512) hex digest of the request body using the secret as the key. This digest can be used by the receiver to authenticate the request's content.

## Installation

If you are upgrading from a previous version of Netbox and want to enable the webhook feature, please follow the directions listed in the sections below.

* [Install Redis server and djano-rq package](../installation/2-netbox/#install-python-packages)
* [Modify configuration to enable webhooks](../installation/2-netbox/#webhooks-configuration)
* [Create supervisord program to run the rqworker process](../installation/3-http-daemon/#supervisord-installation)

## Requests

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

## Backend Status

Django-rq includes a status page in the admin site which can be used to view the result of processed webhooks and manually retry any failed webhooks. Access it from http://netbox.local/admin/webhook-backend-status/.
