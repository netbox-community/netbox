from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels


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
