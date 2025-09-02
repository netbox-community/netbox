# Webhooks

NetBox supports the configuration of outbound [webhooks](../../integrations/webhooks.md) which can be triggered by custom [event rules](../../features/event-rules.md). By default, a webhook's payload will contain a serialized representation of the object, before & after snapshots (if applicable), and some metadata.

## Callback Registration

Plugins can register callback functions to supplement a webhook's payload with their own data. For example, it might be desirable for a plugin to attach information about the status of some objects at the time a change was made.

This can be accomplished by defining a function which accepts a defined set of keyword arguments and registering it as a webhook callback. Whenever a new webhook is generated, the function will be called, and any data it returns will be attached to the webhook's payload under the `context` key.

### Example

```python
from extras.webhooks import register_webhook_callback
from my_plugin.utilities import get_foo_status

@register_webhook_callback
def set_foo_status(object_type, event_type, data, request):
    if status := get_foo_status():
        return {
            'foo': status
        }
```

The resulting webhook payload will look like the following:

```json
{
    "event": "updated",
    "timestamp": "2025-08-07T14:24:30.627321+00:00",
    "object_type": "dcim.site",
    "username": "admin",
    "request_id": "49e3e39e-7333-4b9c-a9af-19f0dc1e7dc9",
    "data": {
        "id": 2,
        "url": "/api/dcim/sites/2/",
        ...
    },
    "snapshots": {...},
    "context": {
        "foo": 123
    }
}
```

!!! note "Consider namespacing webhook data"
    The data returned from all webhook callbacks will be compiled into a single `context` dictionary. Any existing keys within this dictionary will be overwritten by subsequent callbacks which include those keys. To avoid collisions with webhook data provided by other plugins, consider namespacing your plugin's data within a nested dictionary as such:
    
    ```python
    return {
        'my_plugin': {
            'foo': 123,
            'bar': 456,
        }
    }
    ```

### Callback Function Arguments

| Name          | Type              | Description                                                       |
|---------------|-------------------|-------------------------------------------------------------------|
| `object_type` | ObjectType        | The ObjectType which represents the triggering object             |
| `event_type`  | String            | The type of event which triggered the webhook (see `core.events`) |
| `data`        | Dictionary        | The serialized representation of the object                       |
| `request`     | NetBoxFakeRequest | A copy of the request (if any) which resulted in the change       |

## Where to Define Callbacks

Webhook callbacks can be defined anywhere within a plugin, but must be imported during plugin initialization. If you wish to keep them in a separate module, you can import that module under the PluginConfig's `ready()` method:

```python
def ready(self):
    super().ready()
    from my_plugin import webhook_callbacks
```
