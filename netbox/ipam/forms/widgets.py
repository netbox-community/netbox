import json

from django import forms

from ipam.choices import ServiceProtocolChoices
from ipam.validators import group_port_mappings

__all__ = (
    'PortMappingWidget',
)


def group_mappings(mappings):
    """
    Group a flat ``['tcp/80', 'tcp/443', 'udp/53']`` list into widget rows
    ``[{'protocol': 'tcp', 'ports': '80,443'}, {'protocol': 'udp', 'ports': '53'}]``.
    """
    return [
        {'protocol': protocol, 'ports': ','.join(ports)}
        for protocol, ports in group_port_mappings(mappings).items()
    ]


class PortMappingWidget(forms.Widget):
    """
    Renders a dynamic set of (protocol, ports) rows. The rows are serialized to a JSON string held in a
    single hidden input (client-side JS keeps the hidden input in sync as rows are added/removed). Each
    row's ``ports`` value is a raw comma/range string (e.g. "80,443,8000-8010"); the server expands it.
    """
    template_name = 'ipam/widgets/port_mappings.html'

    def get_context(self, name, value, attrs):
        rows = []
        if value:
            try:
                rows = json.loads(value)
            except (TypeError, ValueError):
                rows = []
        # Always render at least one (blank) row so the entry fields are visible on an empty form
        if not rows:
            rows = [{'protocol': '', 'ports': ''}]
        return {
            'widget': {
                'name': name,
                'value': value or '[]',
                'rows': rows,
                'attrs': attrs or {},
            },
            'protocol_choices': list(ServiceProtocolChoices),
        }

    def value_from_datadict(self, data, files, name):
        return data.get(name)
