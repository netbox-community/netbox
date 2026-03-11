from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels


class WirelessLANGroupPanel(panels.NestedGroupObjectPanel):
    pass


class WirelessLANPanel(panels.ObjectAttributesPanel):
    ssid = attrs.TextAttr('ssid', label=_('SSID'))
    group = attrs.RelatedObjectAttr('group', linkify=True)
    status = attrs.ChoiceAttr('status')
    scope = attrs.GenericForeignKeyAttr('scope', linkify=True)
    description = attrs.TextAttr('description')
    vlan = attrs.RelatedObjectAttr('vlan', label=_('VLAN'), linkify=True)
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')


class WirelessAuthenticationPanel(panels.ObjectAttributesPanel):
    title = _('Authentication')

    auth_type = attrs.ChoiceAttr('auth_type', label=_('Type'))
    auth_cipher = attrs.ChoiceAttr('auth_cipher', label=_('Cipher'))
    auth_psk = attrs.TemplatedAttr('auth_psk', label=_('PSK'), template_name='wireless/attrs/auth_psk.html')


class WirelessLinkInterfacePanel(panels.ObjectPanel):
    template_name = 'wireless/panels/wirelesslink_interface.html'

    def __init__(self, interface_attr, title, **kwargs):
        super().__init__(**kwargs)
        self.interface_attr = interface_attr
        self.title = title

    def get_context(self, context):
        obj = context['object']
        return {
            **super().get_context(context),
            'interface': getattr(obj, self.interface_attr),
        }


class WirelessLinkPropertiesPanel(panels.ObjectAttributesPanel):
    title = _('Link Properties')

    status = attrs.ChoiceAttr('status')
    ssid = attrs.TextAttr('ssid', label=_('SSID'))
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    description = attrs.TextAttr('description')
    distance = attrs.NumericAttr('distance', unit_accessor='get_distance_unit_display')
