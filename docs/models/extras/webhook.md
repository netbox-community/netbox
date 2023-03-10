# Webhooks

A webhook is a mechanism for conveying to some external system a change that took place in NetBox. For example, you may want to notify a monitoring system whenever the status of a device is updated in NetBox. This can be done by creating a webhook for the device model in NetBox and identifying the webhook receiver. When NetBox detects a change to a device, an HTTP request containing the details of the change and who made it be sent to the specified receiver.

See the [webhooks documentation](../../integrations/webhooks.md) for more information.

## Fields

### Name

A unique human-friendly name.

### Content Types

The type(s) of object in NetBox that will trigger the webhook.

### Enabled

If not selected, the webhook will be inactive.

### Events

The events which will trigger the webhook. At least one event type must be selected.

| Name       | Description                          |
|------------|--------------------------------------|
| Creations  | A new object has been created        |
| Updates    | An existing object has been modified |
| Deletions  | An object has been deleted           |
| Job starts | A job for an object starts           |
| Job ends   | A job for an object terminates       |

### URL

The URL to which the webhook HTTP request will be made.

### HTTP Method

The type of HTTP request to send. Options are:

* `GET`
* `POST`
* `PUT`
* `PATCH`
* `DELETE`

### HTTP Content Type

The content type to indicate in the outgoing HTTP request header. See [this list](https://www.iana.org/assignments/media-types/media-types.xhtml) of known types for reference.

### Additional Headers

Any additional header to include with the outgoing HTTP request. These should be defined in the format `Name: Value`, with each header on a separate line. Jinja2 templating is supported for this field.

### Body Template

Jinja2 template for a custom request body, if desired. If not defined, NetBox will populate the request body with a raw dump of the webhook context.

### Secret

A secret string used to prove authenticity of the request (optional). This will append a `X-Hook-Signature` header to the request, consisting of a HMAC (SHA-512) hex digest of the request body using the secret as the key.

### Conditions

A set of [prescribed conditions](../../reference/conditions.md) against which the triggering object will be evaluated. If the conditions are defined but not met by the object, the webhook will not be sent. A webhook that does not define any conditions will _always_ trigger.

### SSL Verification

Controls whether validation of the receiver's SSL certificate is enforced when HTTPS is used.

!!! warning
    Disabling this can expose your webhooks to man-in-the-middle attacks.

### CA File Path

The file path to a particular certificate authority (CA) file to use when validating the receiver's SSL certificate (if not using the system defaults).

## Context Data

The following context variables are available in to the text and link templates.

| Variable     | Description                                        |
|--------------|----------------------------------------------------|
| `event`      | The event type (`create`, `update`, or `delete`)   |
| `timestamp`  | The time at which the event occured                |
| `model`      | The type of object impacted                        |
| `username`   | The name of the user associated with the change    |
| `request_id` | The unique request ID                              |
| `data`       | A complete serialized representation of the object |
| `snapshots`  | Pre- and post-change snapshots of the object       |
