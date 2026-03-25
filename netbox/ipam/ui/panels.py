from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.ui import actions, attrs, panels

from .attrs import VRFDisplayAttr


class FHRPGroupAssignmentsPanel(panels.ObjectPanel):
    """
    A panel which lists all FHRP group assignments for a given object.
    """
    template_name = 'ipam/panels/fhrp_groups.html'
    title = _('FHRP Groups')
    actions = [
        actions.AddObject(
            'ipam.FHRPGroup',
            url_params={
                'return_url': lambda ctx: reverse(
                    'ipam:fhrpgroupassignment_add',
                    query={
                        'interface_type': ContentType.objects.get_for_model(ctx['object']).pk,
                        'interface_id': ctx['object'].pk,
                    },
                ),
            },
            label=_('Create Group'),
        ),
        actions.AddObject(
            'ipam.FHRPGroupAssignment',
            url_params={
                'interface_type': lambda ctx: ContentType.objects.get_for_model(ctx['object']).pk,
                'interface_id': lambda ctx: ctx['object'].pk,
            },
            label=_('Assign Group'),
        ),
    ]


class VRFPanel(panels.ObjectAttributesPanel):
    rd = attrs.TextAttr('rd', label=_('Route Distinguisher'), style='font-monospace')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    enforce_unique = attrs.BooleanAttr('enforce_unique', label=_('Unique IP Space'))
    description = attrs.TextAttr('description')


class RouteTargetPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name', style='font-monospace')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    description = attrs.TextAttr('description')


class RIRPanel(panels.OrganizationalObjectPanel):
    is_private = attrs.BooleanAttr('is_private', label=_('Private'))


class ASNRangePanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    rir = attrs.RelatedObjectAttr('rir', linkify=True, label=_('RIR'))
    range = attrs.TextAttr('range_as_string_with_asdot', label=_('Range'))
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    description = attrs.TextAttr('description')


class ASNPanel(panels.ObjectAttributesPanel):
    asn = attrs.TextAttr('asn_with_asdot', label=_('AS Number'))
    rir = attrs.RelatedObjectAttr('rir', linkify=True, label=_('RIR'))
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    description = attrs.TextAttr('description')


class AggregatePanel(panels.ObjectAttributesPanel):
    family = attrs.TextAttr('family', format_string='IPv{}', label=_('Family'))
    rir = attrs.RelatedObjectAttr('rir', linkify=True, label=_('RIR'))
    utilization = attrs.TemplatedAttr(
        'prefix',
        template_name='ipam/aggregate/attrs/utilization.html',
        label=_('Utilization'),
    )
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    date_added = attrs.DateTimeAttr('date_added', spec='date', label=_('Date Added'))
    description = attrs.TextAttr('description')


class RolePanel(panels.OrganizationalObjectPanel):
    weight = attrs.NumericAttr('weight')


class IPRangePanel(panels.ObjectAttributesPanel):
    family = attrs.TextAttr('family', format_string='IPv{}', label=_('Family'))
    start_address = attrs.TextAttr('start_address', label=_('Starting Address'))
    end_address = attrs.TextAttr('end_address', label=_('Ending Address'))
    size = attrs.NumericAttr('size')
    mark_populated = attrs.BooleanAttr('mark_populated', label=_('Marked Populated'))
    mark_utilized = attrs.BooleanAttr('mark_utilized', label=_('Marked Utilized'))
    utilization = attrs.TemplatedAttr(
        'utilization',
        template_name='ipam/iprange/attrs/utilization.html',
        label=_('Utilization'),
    )
    vrf = VRFDisplayAttr('vrf', label=_('VRF'), show_rd=True)
    role = attrs.RelatedObjectAttr('role', linkify=True)
    status = attrs.ChoiceAttr('status')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    description = attrs.TextAttr('description')


class IPAddressPanel(panels.ObjectAttributesPanel):
    family = attrs.TextAttr('family', format_string='IPv{}', label=_('Family'))
    vrf = VRFDisplayAttr('vrf', label=_('VRF'))
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    status = attrs.ChoiceAttr('status')
    role = attrs.ChoiceAttr('role')
    dns_name = attrs.TextAttr('dns_name', label=_('DNS Name'))
    description = attrs.TextAttr('description')
    assigned_object = attrs.RelatedObjectAttr(
        'assigned_object',
        linkify=True,
        grouped_by='parent_object',
        label=_('Assignment'),
    )
    nat_inside = attrs.TemplatedAttr(
        'nat_inside',
        template_name='ipam/ipaddress/attrs/nat_inside.html',
        label=_('NAT (inside)'),
    )
    nat_outside = attrs.TemplatedAttr(
        'nat_outside',
        template_name='ipam/ipaddress/attrs/nat_outside.html',
        label=_('NAT (outside)'),
    )
    is_primary_ip = attrs.BooleanAttr('is_primary_ip', label=_('Primary IP'))
    is_oob_ip = attrs.BooleanAttr('is_oob_ip', label=_('OOB IP'))


class PrefixPanel(panels.ObjectAttributesPanel):
    family = attrs.TextAttr('family', format_string='IPv{}', label=_('Family'))
    vrf = VRFDisplayAttr('vrf', label=_('VRF'))
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    aggregate = attrs.TemplatedAttr(
        'aggregate',
        template_name='ipam/prefix/attrs/aggregate.html',
        label=_('Aggregate'),
    )
    scope = attrs.GenericForeignKeyAttr('scope', linkify=True)
    vlan = attrs.RelatedObjectAttr('vlan', linkify=True, label=_('VLAN'), grouped_by='group')
    status = attrs.ChoiceAttr('status')
    role = attrs.RelatedObjectAttr('role', linkify=True)
    description = attrs.TextAttr('description')
    is_pool = attrs.BooleanAttr('is_pool', label=_('Is a pool'))


class VLANGroupPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    scope = attrs.GenericForeignKeyAttr('scope', linkify=True)
    vid_ranges = attrs.TemplatedAttr(
        'vid_ranges_items',
        template_name='ipam/vlangroup/attrs/vid_ranges.html',
        label=_('VLAN IDs'),
    )
    utilization = attrs.UtilizationAttr('utilization')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')


class VLANTranslationPolicyPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')


class VLANTranslationRulePanel(panels.ObjectAttributesPanel):
    policy = attrs.RelatedObjectAttr('policy', linkify=True)
    local_vid = attrs.NumericAttr('local_vid', label=_('Local VID'))
    remote_vid = attrs.NumericAttr('remote_vid', label=_('Remote VID'))
    description = attrs.TextAttr('description')


class FHRPGroupPanel(panels.ObjectAttributesPanel):
    protocol = attrs.ChoiceAttr('protocol')
    group_id = attrs.NumericAttr('group_id', label=_('Group ID'))
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    member_count = attrs.NumericAttr('member_count', label=_('Members'))


class FHRPGroupAuthPanel(panels.ObjectAttributesPanel):
    title = _('Authentication')

    auth_type = attrs.ChoiceAttr('auth_type', label=_('Authentication Type'))
    auth_key = attrs.TextAttr('auth_key', label=_('Authentication Key'))


class VLANPanel(panels.ObjectAttributesPanel):
    region = attrs.NestedObjectAttr('site.region', linkify=True, label=_('Region'))
    site = attrs.RelatedObjectAttr('site', linkify=True)
    group = attrs.RelatedObjectAttr('group', linkify=True)
    vid = attrs.NumericAttr('vid', label=_('VLAN ID'))
    name = attrs.TextAttr('name')
    tenant = attrs.RelatedObjectAttr('tenant', linkify=True, grouped_by='group')
    status = attrs.ChoiceAttr('status')
    role = attrs.RelatedObjectAttr('role', linkify=True)
    description = attrs.TextAttr('description')
    qinq_role = attrs.ChoiceAttr('qinq_role', label=_('Q-in-Q Role'))
    qinq_svlan = attrs.RelatedObjectAttr('qinq_svlan', linkify=True, label=_('Q-in-Q SVLAN'))
    l2vpn = attrs.RelatedObjectAttr('l2vpn_termination.l2vpn', linkify=True, label=_('L2VPN'))


class VLANCustomerVLANsPanel(panels.ObjectsTablePanel):
    """
    A panel listing customer VLANs (C-VLANs) for an S-VLAN. Only renders when the VLAN has Q-in-Q
    role 'svlan'.
    """
    def __init__(self):
        super().__init__(
            'ipam.vlan',
            filters={'qinq_svlan_id': lambda ctx: ctx['object'].pk},
            title=_('Customer VLANs'),
            actions=[
                actions.AddObject(
                    'ipam.vlan',
                    url_params={
                        'qinq_role': 'cvlan',
                        'qinq_svlan': lambda ctx: ctx['object'].pk,
                    },
                    label=_('Add a VLAN'),
                ),
            ],
        )

    def render(self, context):
        obj = context.get('object')
        if not obj or obj.qinq_role != 'svlan':
            return ''
        return super().render(context)


class ServiceTemplatePanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    protocol = attrs.ChoiceAttr('protocol')
    ports = attrs.TextAttr('port_list', label=_('Ports'))
    description = attrs.TextAttr('description')


class ServicePanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    parent = attrs.RelatedObjectAttr('parent', linkify=True)
    protocol = attrs.ChoiceAttr('protocol')
    ports = attrs.TextAttr('port_list', label=_('Ports'))
    ip_addresses = attrs.TemplatedAttr(
        'ipaddresses',
        template_name='ipam/service/attrs/ip_addresses.html',
        label=_('IP Addresses'),
    )
    description = attrs.TextAttr('description')
