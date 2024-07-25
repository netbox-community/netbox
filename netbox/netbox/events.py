from dataclasses import dataclass

from netbox.registry import registry

EVENT_TYPE_INFO = 'info'
EVENT_TYPE_SUCCESS = 'success'
EVENT_TYPE_WARNING = 'warning'
EVENT_TYPE_DANGER = 'danger'

__all__ = (
    'EVENT_TYPE_DANGER',
    'EVENT_TYPE_INFO',
    'EVENT_TYPE_SUCCESS',
    'EVENT_TYPE_WARNING',
    'Event',
    'get_event',
    'get_event_type_choices',
    'get_event_text',
)


def get_event(name):
    return registry['events'].get(name)


def get_event_text(name):
    if event := registry['events'].get(name):
        return event.text
    return ''


def get_event_type_choices():
    return [
        (event.name, event.text) for event in registry['events'].values()
    ]


@dataclass
class Event:
    """
    A type of event which can occur in NetBox. Event rules can be defined to automatically
    perform some action in response to an event.

    Args:
        name: The unique name under which the event is registered.
        text: The human-friendly event name. This should support translation.
        type: The event's classification (info, success, warning, or danger). The default type is info.
    """
    name: str
    text: str
    type: str = EVENT_TYPE_INFO

    def __str__(self):
        return self.text

    def register(self):
        if self.name in registry['events']:
            raise Exception(f"An event named {self.name} has already been registered!")
        registry['events'][self.name] = self

    def color(self):
        return {
            EVENT_TYPE_INFO: 'blue',
            EVENT_TYPE_SUCCESS: 'green',
            EVENT_TYPE_WARNING: 'orange',
            EVENT_TYPE_DANGER: 'red',
        }.get(self.type)

    def icon(self):
        return {
            EVENT_TYPE_INFO: 'mdi mdi-information',
            EVENT_TYPE_SUCCESS: 'mdi mdi-check-circle',
            EVENT_TYPE_WARNING: 'mdi mdi-alert-box',
            EVENT_TYPE_DANGER: 'mdi mdi-alert-octagon',
        }.get(self.type)
