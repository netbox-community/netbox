import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ipam.forms.widgets import PortMappingWidget
from ipam.utils import expand_port_mapping, group_port_mapping_rows
from ipam.validators import validate_port_mappings

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
                return json.dumps(group_port_mapping_rows([value]))
            return value
        return json.dumps(group_port_mapping_rows(value))

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
            for position, row in enumerate(rows, start=1):
                # The widget's JS always submits a list of {protocol, ports} objects, but the hidden
                # input is just POST data: a hand-crafted payload can put anything here, so validate the
                # shape rather than letting a non-dict row raise AttributeError (a 500) on .get() below.
                if not isinstance(row, dict):
                    raise ValidationError(_("Invalid port mapping data."))
                protocol = row.get('protocol')
                raw_ports = row.get('ports')
                # Likewise `protocol` is only ever a string, and `ports` either a string (the widget's
                # comma/range format) or a list of ports (set programmatically); anything else would reach
                # expand_port_mapping() and fail there on .strip().
                if (
                    (protocol is not None and not isinstance(protocol, str))
                    or (raw_ports is not None and not isinstance(raw_ports, (str, list)))
                ):
                    raise ValidationError(_("Invalid port mapping data."))
                if isinstance(raw_ports, str):
                    raw_ports = raw_ports.strip()
                # Ignore entirely-empty rows (e.g. the default blank row on an untouched form)
                if not protocol and not raw_ports:
                    continue
                # Expand via the shared helper, which accepts either the widget's comma/range string or an
                # already-expanded list, rejects a blank protocol, and preserves a protocol-without-ports
                # row as a bare 'protocol/' token. Errors are re-raised with the row's position (among the
                # submitted rows — the widget omits entirely-blank ones), since it renders one row per
                # protocol and an unqualified "must specify a protocol" gives no clue which row to fix.
                # Errors from validate_port_mappings() below are deliberately left unqualified: each quotes
                # the offending mapping already, and a duplicate spans two rows.
                try:
                    mappings.extend(expand_port_mapping(protocol, raw_ports))
                except ValidationError as e:
                    raise ValidationError([
                        _("Row {position}: {error}").format(position=position, error=message)
                        for message in e.messages
                    ])

        # Shared validation returns the canonical (normalized) list of protocol/port strings
        return validate_port_mappings(mappings)

    def has_changed(self, initial, data):
        # Compare the parsed mappings rather than raw strings, so cosmetic differences (row/port
        # ordering, whitespace) don't register as a change.
        def normalize(value):
            try:
                return sorted(self.to_python(value))
            except ValidationError:
                return None

        return normalize(self.prepare_value(initial)) != normalize(data)
