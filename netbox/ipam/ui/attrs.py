from django.template.loader import render_to_string

from netbox.ui import attrs


class VRFDisplayAttr(attrs.ObjectAttribute):
    """
    Renders a VRF reference, displaying 'Global' when no VRF is assigned. Optionally includes
    the route distinguisher (RD).
    """
    template_name = 'ipam/attrs/vrf.html'

    def __init__(self, *args, show_rd=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_rd = show_rd

    def render(self, obj, context):
        value = self.get_value(obj)
        return render_to_string(self.template_name, {
            **self.get_context(obj, context),
            'name': context['name'],
            'value': value,
            'show_rd': self.show_rd,
        })
