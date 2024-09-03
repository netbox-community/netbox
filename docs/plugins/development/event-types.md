# Event Types

!!! info "This feature was introduced in NetBox v4.1."

Plugins can register their own custom event types for use with NetBox [event rules](../../models/extras/eventrule.md). This is accomplished by calling the `register()` method on an instance of the `EventType` class. This can be done anywhere within the plugin. An example is provided below.

```python
from django.utils.translation import gettext_lazy as _
from netbox.events import EventType, EVENT_TYPE_KIND_SUCCESS

EventType(
    name='ticket_opened',
    text=_('Ticket opened'),
    kind=EVENT_TYPE_KIND_SUCCESS
).register()
```

::: netbox.events.EventType
