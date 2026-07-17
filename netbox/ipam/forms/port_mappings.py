import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ipam.choices import ServiceProtocolChoices
from ipam.constants import SERVICE_PORT_MAX, SERVICE_PORT_MIN
from ipam.validators import group_port_mappings, validate_port_mappings
from utilities.forms.utils import parse_numeric_range

__all__ = (
    'PortMappingField',
    'PortMappingWidget',
)


def _group_mappings(mappings):
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

    def format_value(self, value):
        # Mirror PortMappingField.prepare_value: a raw flat list is grouped into rows; a pre-converted
        # JSON string is passed through unchanged.
        if value is None:
            return '[]'
        if isinstance(value, str):
            return value
        return json.dumps(_group_mappings(value))


class PortMappingField(forms.Field):
    """
    A form field for editing a service's port mappings. Presents one row per protocol (each with a
    comma/range list of ports) but cleans to the model's flat list of ``protocol/port`` strings, e.g.
    ``['tcp/80', 'tcp/443', 'udp/53']``.
    """
    widget = PortMappingWidget

    def prepare_value(self, value):
        # Group the flat ['tcp/80', 'tcp/443', 'udp/53'] list back into per-protocol rows for the widget.
        if value in (None, ''):
            return '[]'
        if isinstance(value, str):
            return value
        return json.dumps(_group_mappings(value))

    def to_python(self, value):
        if value in (None, ''):
            return []
        # A list is assumed to already be the flat ['tcp/80', ...] form (e.g. set programmatically)
        if isinstance(value, list):
            mappings = value
        else:
            try:
                rows = json.loads(value)
            except (TypeError, ValueError):
                raise ValidationError(_("Invalid port mapping data."))
            if not isinstance(rows, list):
                raise ValidationError(_("Invalid port mapping data."))

            mappings = []
            for row in rows:
                protocol = (row or {}).get('protocol')
                raw_ports = (row or {}).get('ports')
                if isinstance(raw_ports, str):
                    raw_ports = raw_ports.strip()
                # Ignore entirely-empty rows (e.g. the default blank row on an untouched form)
                if not protocol and not raw_ports:
                    continue
                # A protocol chosen without any ports is preserved as a bare 'protocol/' token so the
                # shared validator reports a clear "expected protocol/port" error (rather than
                # parse_numeric_range raising a confusing 'Range "" is invalid').
                if not raw_ports:
                    mappings.append(f'{protocol}/')
                    continue
                ports = (
                    parse_numeric_range(raw_ports, min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX)
                    if isinstance(raw_ports, str) else (raw_ports or [])
                )
                mappings.extend(f'{protocol}/{port}' for port in ports)

        # Shared validation returns the canonical (normalized) list of protocol/port strings
        return validate_port_mappings(mappings)

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')

    def has_changed(self, initial, data):
        # Compare the parsed mappings rather than raw strings, so cosmetic differences (row/port
        # ordering, whitespace) don't register as a change.
        def normalize(value):
            try:
                return sorted(self.to_python(value))
            except ValidationError:
                return None

        return normalize(self.prepare_value(initial)) != normalize(data)
