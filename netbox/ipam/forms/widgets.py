import json

from django import forms
from django.forms.utils import flatatt

from ipam.choices import ServiceProtocolChoices

__all__ = (
    'PortMappingWidget',
)


class PortMappingWidget(forms.Widget):
    """
    Renders a dynamic set of (protocol, ports) rows. The rows are serialized to a JSON string held in a
    single hidden input (client-side JS keeps the hidden input in sync as rows are added/removed). Each
    row's ``ports`` value is a raw comma/range string (e.g. "80,443,8000-8010"); the server expands it.
    """
    template_name = 'ipam/widgets/port_mappings.html'

    # aria-* attributes which render_field_with_aria() sets per-field, and which must be copied onto the
    # row controls: the wrapping <div> isn't a form control, so assistive technology ignores them there.
    CONTROL_ATTRS = ('aria-describedby', 'aria-invalid')

    def id_for_label(self, id_):
        # The field's <label for="..."> must point at a real form control, not the wrapping <div> which
        # carries the widget's id. Target the first row's protocol <select>; the client-side widget keeps
        # this id on whichever row is first as rows are added and removed.
        return f'{id_}_protocol_0' if id_ else ''

    def get_context(self, name, value, attrs):
        attrs = attrs or {}
        rows = []
        if value:
            try:
                rows = json.loads(value)
            except (TypeError, ValueError):
                rows = []
        # Re-rendering an invalid bound form hands us back the raw POST value, which need not be the list
        # of {protocol, ports} objects the JS produces: a crafted payload of e.g. `5` or `{"a": 1}` parses
        # as valid JSON but would break the template's row loop. Discard anything of the wrong shape and
        # fall through to the blank row below.
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            rows = []
        # Always render at least one (blank) row so the entry fields are visible on an empty form
        if not rows:
            rows = [{'protocol': '', 'ports': ''}]
        return {
            'widget': {
                'name': name,
                'value': value or '[]',
                'rows': rows,
                'attrs': attrs,
                'label_id': self.id_for_label(attrs.get('id')),
                'control_attrs': flatatt({
                    key: value for key, value in attrs.items() if key in self.CONTROL_ATTRS
                }),
            },
            'protocol_choices': list(ServiceProtocolChoices),
        }

    def value_from_datadict(self, data, files, name):
        return data.get(name)
