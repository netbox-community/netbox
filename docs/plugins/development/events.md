# Events

Plugins can register their own custom event types for use with NetBox [event rules](../../models/extras/eventrule.md). This is accomplished by calling the `register()` method on an instance of the `Event` class. This can be done anywhere within the plugin. An example is provided below.

```python
from django.utils.translation import gettext_lazy as _
from netbox.events import Event, EVENT_TYPE_SUCCESS

Event(
    name='ticket_opened',
    text=_('Ticket opened'),
    type=EVENT_TYPE_SUCCESS
).register()
```

::: netbox.events.Event
