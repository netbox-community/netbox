from django.template.loader import render_to_string

from netbox.ui import attrs


class VRFDisplayAttr(attrs.ObjectAttribute):
    """
    Renders a VRF reference, displaying 'Global' when no VRF is assigned.
    """
    template_name = 'ipam/attrs/vrf.html'

    def render(self, obj, context):
        value = self.get_value(obj)
        return render_to_string(self.template_name, {
            **self.get_context(obj, context),
            'name': context.get('name', ''),
            'value': value,
        })


class VRFDisplayWithRDAttr(VRFDisplayAttr):
    """
    Renders a VRF reference with its route distinguisher.
    """
    template_name = 'ipam/attrs/vrf_with_rd.html'
