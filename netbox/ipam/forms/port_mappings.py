import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ipam.choices import ServiceProtocolChoices
from ipam.validators import validate_port_mappings
from utilities.data import array_to_string
from utilities.forms.utils import parse_numeric_range

__all__ = (
    'PortMappingField',
    'PortMappingWidget',
)


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
        if value is None:
            return '[]'
        if isinstance(value, str):
            return value
        return json.dumps(value)


class PortMappingField(forms.Field):
    """
    A form field for editing a list of (protocol, ports) port mappings. Cleans to a list of dicts of the
    form ``{'protocol': <str>, 'ports': [<int>, ...]}``, suitable for syncing child mapping rows.
    """
    widget = PortMappingWidget

    def prepare_value(self, value):
        # Normalize the value to a JSON string with ports rendered as comma/range strings for display.
        if value in (None, ''):
            return '[]'
        if isinstance(value, str):
            return value

        rows = []
        for item in value:
            if hasattr(item, 'protocol'):
                # A ServicePortMapping / ServiceTemplatePortMapping instance
                rows.append({'protocol': item.protocol, 'ports': array_to_string(item.ports)})
            else:
                # A dict; ports may be a list of ints or an already-formatted string
                ports = item.get('ports')
                if not isinstance(ports, str):
                    ports = array_to_string(ports or [])
                rows.append({'protocol': item.get('protocol'), 'ports': ports})
        return json.dumps(rows)

    def to_python(self, value):
        if value in (None, ''):
            return []
        if isinstance(value, list):
            return value
        try:
            rows = json.loads(value)
        except (TypeError, ValueError):
            raise ValidationError(_("Invalid port mapping data."))
        if not isinstance(rows, list):
            raise ValidationError(_("Invalid port mapping data."))

        valid_protocols = ServiceProtocolChoices.values()
        cleaned = []
        for row in rows:
            protocol = (row or {}).get('protocol')
            raw_ports = (row or {}).get('ports')
            # Ignore entirely-empty rows (e.g. the default blank row on an untouched form)
            if not protocol and not raw_ports:
                continue
            if protocol not in valid_protocols:
                raise ValidationError(
                    _("Invalid protocol: {protocol}").format(protocol=protocol)
                )
            ports = parse_numeric_range(raw_ports) if isinstance(raw_ports, str) else (raw_ports or [])
            cleaned.append({'protocol': protocol, 'ports': ports})

        # Shared validation: unique protocol per mapping, at least one port, ports within range
        validate_port_mappings(cleaned)

        return cleaned

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')

    def has_changed(self, initial, data):
        # Compare the parsed mappings rather than raw strings, so cosmetic differences (row/port
        # ordering, whitespace) don't register as a change.
        def normalize(value):
            try:
                mappings = self.to_python(value)
            except ValidationError:
                return None
            return sorted((m['protocol'], tuple(sorted(m['ports']))) for m in mappings)

        return normalize(self.prepare_value(initial)) != normalize(data)
