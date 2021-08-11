# Webhooks

A webhook is a mechanism for conveying to some external system a change that took place in NetBox. For example, you may want to notify a monitoring system whenever the status of a device is updated in NetBox. This can be done by creating a webhook for the device model in NetBox and identifying the webhook receiver. When NetBox detects a change to a device, an HTTP request containing the details of the change and who made it be sent to the specified receiver. Webhooks are managed under Logging > Webhooks.

!!! warning
    Webhooks support the inclusion of user-submitted code to generate custom headers and payloads, which may pose security risks under certain conditions. Only grant permission to create or modify webhooks to trusted users.

## Configuration

* **Name** - A unique name for the webhook. The name is not included with outbound messages.
* **Object type(s)** - The type or types of NetBox object that will trigger the webhook.
* **Enabled** - If unchecked, the webhook will be inactive.
* **Events** - A webhook may trigger on any combination of create, update, and delete events. At least one event type must be selected.
* **HTTP method** - The type of HTTP request to send. Options include `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`.
* **URL** - The fuly-qualified URL of the request to be sent. This may specify a destination port number if needed.
* **HTTP content type** - The value of the request's `Content-Type` header. (Defaults to `application/json`)
* **Additional headers** - Any additional headers to include with the request (optional). Add one header per line in the format `Name: Value`. Jinja2 templating is supported for this field (see below).
* **Body template** - The content of the request being sent (optional). Jinja2 templating is supported for this field (see below). If blank, NetBox will populate the request body with a raw dump of the webhook context. (If the HTTP cotent type is set to `application/json`, this will be formatted as a JSON object.)
* **Secret** - A secret string used to prove authenticity of the request (optional). This will append a `X-Hook-Signature` header to the request, consisting of a HMAC (SHA-512) hex digest of the request body using the secret as the key.
* **SSL verification** - Uncheck this option to disable validation of the receiver's SSL certificate. (Disable with caution!)
* **CA file path** - The file path to a particular certificate authority (CA) file to use when validating the receiver's SSL certificate (optional).

## Jinja2 Template Support

[Jinja2 templating](https://jinja.palletsprojects.com/) is supported for the `additional_headers` and `body_template` fields. This enables the user to convey object data in the request headers as well as to craft a customized request body. Request content can be crafted to enable the direct interaction with external systems by ensuring the outgoing message is in a format the receiver expects and understands.

For example, you might create a NetBox webhook to [trigger a Slack message](https://api.slack.com/messaging/webhooks) any time an IP address is created. You can accomplish this using the following configuration:

* Object type: IPAM > IP address
* HTTP method: `POST`
* URL: Slack incoming webhook URL
* HTTP content type: `application/json`
* Body template: `{"text": "IP address {{ data['address'] }} was created by {{ username }}!"}`

### Available Context

The following data is available as context for Jinja2 templates:

* `event` - The type of event which triggered the webhook: created, updated, or deleted.
* `model` - The NetBox model which triggered the change.
* `timestamp` - The time at which the event occurred (in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format).
* `username` - The name of the user account associated with the change.
* `request_id` - The unique request ID. This may be used to correlate multiple changes associated with a single request.
* `data` - A detailed representation of the object in its current state. This is typically equivalent to the model's representation in NetBox's REST API.
* `snapshots` - Minimal "snapshots" of the object state both before and after the change was made; provided ass a dictionary with keys named `prechange` and `postchange`. These are not as extensive as the fully serialized representation, but contain enough information to convey what has changed.

### Default Request Body

If no body template is specified, the request body will be populated with a JSON object containing the context data. For example, a newly created site might appear as follows:

```no-highlight
{
    "event": "created",
    "timestamp": "2021-03-09 17:55:33.968016+00:00",
    "model": "site",
    "username": "jstretch",
    "request_id": "fdbca812-3142-4783-b364-2e2bd5c16c6a",
    "data": {
        "id": 19,
        "name": "Site 1",
        "slug": "site-1",
        "status": 
            "value": "active",
            "label": "Active",
            "id": 1
        },
        "region": null,
        ...
    },
    "snapshots": {
        "prechange": null,
        "postchange": {
            "created": "2021-03-09",
            "last_updated": "2021-03-09T17:55:33.851Z",
            "name": "Site 1",
            "slug": "site-1",
            "status": "active",
            ...
        }
    }
}
```

## Webhook Processing

When a change is detected, any resulting webhooks are placed into a Redis queue for processing. This allows the user's request to complete without needing to wait for the outgoing webhook(s) to be processed. The webhooks are then extracted from the queue by the `rqworker` process and HTTP requests are sent to their respective destinations. The current webhook queue and any failed webhooks can be inspected in the admin UI under System > Background Tasks.

A request is considered successful if the response has a 2XX status code; otherwise, the request is marked as having failed. Failed requests may be retried manually via the admin UI.

## Troubleshooting

To assist with verifying that the content of outgoing webhooks is rendered correctly, NetBox provides a simple HTTP listener that can be run locally to receive and display webhook requests. First, modify the target URL of the desired webhook to `http://localhost:9000/`. This will instruct NetBox to send the request to the local server on TCP port 9000. Then, start the webhook receiver service from the NetBox root directory:

```no-highlight
$ python netbox/manage.py webhook_receiver
Listening on port http://localhost:9000. Stop with CONTROL-C.
```

You can test the receiver itself by sending any HTTP request to it. For example:

```no-highlight
$ curl -X POST http://localhost:9000 --data '{"foo": "bar"}'
```

The server will print output similar to the following:

```no-highlight
[1] Tue, 07 Apr 2020 17:44:02 GMT 127.0.0.1 "POST / HTTP/1.1" 200 -
Host: localhost:9000
User-Agent: curl/7.58.0
Accept: */*
Content-Length: 14
Content-Type: application/x-www-form-urlencoded

{"foo": "bar"}
------------
```

Note that `webhook_receiver` does not actually _do_ anything with the information received: It merely prints the request headers and body for inspection.

Now, when the NetBox webhook is triggered and processed, you should see its headers and content appear in the terminal where the webhook receiver is listening. If you don't, check that the `rqworker` process is running and that webhook events are being placed into the queue (visible under the NetBox admin UI).
