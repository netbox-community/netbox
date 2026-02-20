from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels


class ClusterPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    type = attrs.RelatedObjectAttr('type', linkify=True)
    status = attrs.ChoiceAttr('status')
    description = attrs.TextAttr('description')
    group = attrs.RelatedObjectAttr('group', linkify=True)
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    scope = attrs.GenericForeignKeyAttr('scope', linkify=True)


class VirtualMachinePanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    status = attrs.ChoiceAttr('status')
    start_on_boot = attrs.ChoiceAttr('start_on_boot')
    role = attrs.RelatedObjectAttr('role', linkify=True)
    platform = attrs.NestedObjectAttr('platform', linkify=True, max_depth=3)
    description = attrs.TextAttr('description')
    serial = attrs.TextAttr('serial', label=_('Serial number'), style='font-monospace', copy_button=True)
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    config_template = attrs.RelatedObjectAttr('config_template', linkify=True)
    primary_ip4 = attrs.TemplatedAttr(
        'primary_ip4',
        label=_('Primary IPv4'),
        template_name='virtualization/virtualmachine/attrs/ipaddress.html',
    )
    primary_ip6 = attrs.TemplatedAttr(
        'primary_ip6',
        label=_('Primary IPv6'),
        template_name='virtualization/virtualmachine/attrs/ipaddress.html',
    )


class VirtualMachineClusterPanel(panels.ObjectAttributesPanel):
    title = _('Cluster')

    site = attrs.RelatedObjectAttr('site', linkify=True, grouped_by='group')
    cluster = attrs.RelatedObjectAttr('cluster', linkify=True)
    cluster_type = attrs.RelatedObjectAttr('cluster.type', linkify=True)
    device = attrs.RelatedObjectAttr('device', linkify=True)


class VirtualDiskPanel(panels.ObjectAttributesPanel):
    virtual_machine = attrs.RelatedObjectAttr('virtual_machine', linkify=True, label=_('Virtual Machine'))
    name = attrs.TextAttr('name')
    size = attrs.TemplatedAttr('size', template_name='virtualization/virtualdisk/attrs/size.html')
    description = attrs.TextAttr('description')


class VMInterfacePanel(panels.ObjectAttributesPanel):
    virtual_machine = attrs.RelatedObjectAttr('virtual_machine', linkify=True, label=_('Virtual Machine'))
    name = attrs.TextAttr('name')
    enabled = attrs.BooleanAttr('enabled')
    parent = attrs.RelatedObjectAttr('parent_interface', linkify=True)
    bridge = attrs.RelatedObjectAttr('bridge', linkify=True)
    description = attrs.TextAttr('description')
    mtu = attrs.TextAttr('mtu', label=_('MTU'))
    mode = attrs.ChoiceAttr('mode', label=_('802.1Q Mode'))
    qinq_svlan = attrs.RelatedObjectAttr('qinq_svlan', linkify=True, label=_('Q-in-Q SVLAN'))
    tunnel_termination = attrs.RelatedObjectAttr('tunnel_termination.tunnel', linkify=True, label=_('Tunnel'))


class VMInterfaceAddressingPanel(panels.ObjectAttributesPanel):
    title = _('Addressing')

    primary_mac_address = attrs.TextAttr(
        'primary_mac_address', label=_('MAC Address'), style='font-monospace', copy_button=True
    )
    vrf = attrs.RelatedObjectAttr('vrf', linkify=True, label=_('VRF'))
    vlan_translation_policy = attrs.RelatedObjectAttr(
        'vlan_translation_policy', linkify=True, label=_('VLAN Translation')
    )
