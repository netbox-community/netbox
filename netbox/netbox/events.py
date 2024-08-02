from dataclasses import dataclass

from netbox.registry import registry

EVENT_TYPE_KIND_INFO = 'info'
EVENT_TYPE_KIND_SUCCESS = 'success'
EVENT_TYPE_KIND_WARNING = 'warning'
EVENT_TYPE_KIND_DANGER = 'danger'

__all__ = (
    'EVENT_TYPE_KIND_DANGER',
    'EVENT_TYPE_KIND_INFO',
    'EVENT_TYPE_KIND_SUCCESS',
    'EVENT_TYPE_KIND_WARNING',
    'EventType',
    'get_event_type',
    'get_event_type_choices',
    'get_event_text',
)


def get_event_type(name):
    return registry['event_types'].get(name)


def get_event_text(name):
    if event := registry['event_types'].get(name):
        return event.text
    return ''


def get_event_type_choices():
    return [
        (event.name, event.text) for event in registry['event_types'].values()
    ]


@dataclass
class EventType:
    """
    A type of event which can occur in NetBox. Event rules can be defined to automatically
    perform some action in response to an event.

    Args:
        name: The unique name under which the event is registered.
        text: The human-friendly event name. This should support translation.
        kind: The event's classification (info, success, warning, or danger). The default type is info.
    """
    name: str
    text: str
    kind: str = EVENT_TYPE_KIND_INFO

    def __str__(self):
        return self.text

    def register(self):
        if self.name in registry['event_types']:
            raise Exception(f"An event type named {self.name} has already been registered!")
        registry['event_types'][self.name] = self

    def color(self):
        return {
            EVENT_TYPE_KIND_INFO: 'blue',
            EVENT_TYPE_KIND_SUCCESS: 'green',
            EVENT_TYPE_KIND_WARNING: 'orange',
            EVENT_TYPE_KIND_DANGER: 'red',
        }.get(self.kind)

    def icon(self):
        return {
            EVENT_TYPE_KIND_INFO: 'mdi mdi-information',
            EVENT_TYPE_KIND_SUCCESS: 'mdi mdi-check-circle',
            EVENT_TYPE_KIND_WARNING: 'mdi mdi-alert-box',
            EVENT_TYPE_KIND_DANGER: 'mdi mdi-alert-octagon',
        }.get(self.kind)
