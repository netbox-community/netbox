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
)


@dataclass
class Event:
    name: str
    text: str
    type: str = EVENT_TYPE_INFO

    def __str__(self):
        return self.text

    def register(self):
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
