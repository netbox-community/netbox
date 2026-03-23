from django.template.loader import render_to_string

from netbox.ui import attrs


class VRFDisplayAttr(attrs.ObjectAttribute):
    """
    Renders a VRF reference, displaying 'Global' when no VRF is assigned. Optionally includes
    the route distinguisher (RD).
    """
    template_name = 'ipam/attrs/vrf.html'
    template_name_with_rd = 'ipam/attrs/vrf_with_rd.html'

    def __init__(self, *args, show_rd=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_rd = show_rd

    def render(self, obj, context):
        value = self.get_value(obj)
        template = self.template_name_with_rd if self.show_rd else self.template_name
        return render_to_string(template, {
            **self.get_context(obj, context),
            'name': context['name'],
            'value': value,
        })


class PrefixAggregateAttr(attrs.ObjectAttribute):
    """
    Renders the containing aggregate for a prefix. Reads the aggregate from the template context
    (set via get_extra_context) rather than from the object itself.
    """
    template_name = 'ipam/prefix/attrs/aggregate.html'

    def render(self, obj, context):
        value = context.get(self.accessor)
        if value is None:
            return self.placeholder
        return render_to_string(self.template_name, {'value': value})
