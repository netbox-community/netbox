from django.template.loader import render_to_string

from netbox.ui import attrs


class VRFDisplayAttr(attrs.ObjectAttribute):
    """
    Renders a VRF reference, displaying 'Global' when no VRF is assigned. Optionally includes
    the route distinguisher (RD).

    Parameters:
         show_rd (bool): If true, the VRF's RD will be included. (Default: False)
    """
    template_name = 'ipam/attrs/vrf.html'

    def __init__(self, *args, show_rd=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_rd = show_rd

    def get_context(self, obj, attr, value, context):
        return {
            'show_rd': self.show_rd,
        }

    def render(self, obj, context):
        name = context['name']
        value = self.get_value(obj)

        return render_to_string(self.template_name, {
            **self.get_context(obj, name, value, context),
            'name': name,
            'value': value,
        })
