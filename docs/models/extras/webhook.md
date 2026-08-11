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

The URL to which the webhook HTTP request will be made. Must be `http://` or `https://`, though
part or all of the value may be a Jinja2 template rendered at send time (e.g.
`http://{{ data.name }}.example.com/hook`, or `{{ data.custom_fields.callback_url }}` if the whole
URL comes from a template). A literal scheme is always validated as such, even if the rest of the
URL is templated; otherwise the value is checked only for valid Jinja2 syntax, since its rendered
value isn't known until the webhook actually fires.

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

!!! warning "Sanitize interpolated header values"
    When interpolating data which may be influenced by other users (such as object attributes) into a header value, apply the `header_safe` filter to guard against HTTP header (CR/LF) injection. This filter strips newlines and other control characters which could otherwise be used to smuggle additional headers into the request. For example:

    ```
    X-Object-Name: {{ data.name | header_safe }}
    ```

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

### Timeout

The maximum time (in seconds) to wait for a response from the receiver before the request is considered failed. If left blank, the global [`WEBHOOK_DEFAULT_TIMEOUT`](../../configuration/miscellaneous.md#webhook_default_timeout) configuration value is used.

The timeout must be less than [`RQ_DEFAULT_TIMEOUT`](../../configuration/miscellaneous.md#rq_default_timeout) (300 seconds by default), and NetBox will refuse to save a webhook which violates this. The background job timeout is a hard ceiling on how long a webhook request can run, so a value at or above it leaves no room for the request's own timeout to apply.

!!! note
    Staying below the job timeout makes it *likely*, but does not guarantee, that the request times out on its own. The timeout is applied separately to establishing the connection and to waiting for data, rather than to the request as a whole, so a receiver which stalls at both stages — or which responds slowly but continuously — can still outlast the job timeout and be terminated by the worker instead.

When a request does time out, the failure is recorded by the `netbox.webhooks` logger and the background job is marked as failed.

## Context Data

The following context variables are available to the text and link templates.

| Variable      | Description                                          |
|---------------|------------------------------------------------------|
| `event`       | The event type (`create`, `update`, or `delete`)     |
| `timestamp`   | The time at which the event occurred                 |
| `object_type` | The type of object impacted (`app_label.model_name`) |
| `data`        | A complete serialized representation of the object   |
| `snapshots`   | Pre- and post-change snapshots of the object         |
| `request`     | Data about the triggering request (if available)     |

!!! note
    The `request` variable is populated in the context only when the webhook is associated with a triggering request. It exposes `request.id` (the unique request ID) and `request.user` (the name of the user associated with the change), among other attributes.
