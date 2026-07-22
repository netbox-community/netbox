import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ipam.constants import SERVICE_PORT_MAX, SERVICE_PORT_MIN
from ipam.forms.widgets import PortMappingWidget, group_mappings
from ipam.validators import validate_port_mappings
from utilities.forms.utils import parse_numeric_range

__all__ = (
    'PortMappingField',
)


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
        return json.dumps(group_mappings(value))

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
                # A non-empty ports string that expands to nothing means a reversed range (e.g.
                # "9000-53"); reject it rather than silently dropping the mapping.
                if not ports:
                    raise ValidationError(_('Range "{value}" is invalid.').format(value=raw_ports))
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
