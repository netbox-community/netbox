import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ipam.forms.widgets import PortMappingWidget, group_mappings
from ipam.validators import expand_port_mapping, validate_port_mappings

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
            # An already-grouped JSON string (e.g. re-rendering a bound form) is passed through. A bare
            # 'protocol/port' string arrives when cloning a single-mapping object: the querystring
            # single-value collapse (normalize_querydict) yields a str rather than a list, so group it
            # like the list case instead of handing the widget unparseable JSON (which blanks the row).
            try:
                json.loads(value)
            except (TypeError, ValueError):
                return json.dumps(group_mappings([value]))
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
                if isinstance(raw_ports, list):
                    # Ports already expanded (e.g. set programmatically as a flat list)
                    mappings.extend(f'{protocol}/{port}' for port in raw_ports)
                else:
                    # A comma/range string (the widget's format); expand it via the shared helper, which
                    # also preserves a protocol-without-ports row as a bare 'protocol/' token.
                    mappings.extend(expand_port_mapping(protocol, raw_ports))

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
