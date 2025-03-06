import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_tables2.utils import Accessor

from dcim.models import Interface
from ipam.models import *
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin, TenantColumn
from virtualization.models import VMInterface
from .template_code import *

__all__ = (
    'InterfaceVLANTable',
    'VLANDevicesTable',
    'VLANGroupTable',
    'VLANMembersTable',
    'VLANTable',
    'VLANVirtualMachinesTable',
    'VLANTranslationPolicyTable',
    'VLANTranslationRuleTable',
)

AVAILABLE_LABEL = mark_safe('<span class="badge text-bg-success">Available</span>')


#
# VLAN groups
#

class VLANGroupTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    scope_type = columns.ContentTypeColumn(
        verbose_name=_('Scope Type'),
    )
    scope = tables.Column(
        verbose_name=_('Scope'),
        linkify=True,
        orderable=False
    )
    vid_ranges_list = tables.Column(
        verbose_name=_('VID Ranges'),
        orderable=False
    )
    vlan_count = columns.LinkedCountColumn(
        viewname='ipam:vlan_list',
        url_params={'group_id': 'pk'},
        verbose_name=_('VLANs')
    )
    utilization = columns.UtilizationColumn(
        orderable=False,
        verbose_name=_('Utilization')
    )
    tags = columns.TagColumn(
        url_name='ipam:vlangroup_list'
    )
    actions = columns.ActionsColumn(
        extra_buttons=VLANGROUP_BUTTONS
    )

    class Meta(NetBoxTable.Meta):
        model = VLANGroup
        fields = (
            'pk', 'id', 'name', 'scope_type', 'scope', 'vid_ranges_list', 'vlan_count', 'slug', 'description',
            'tags', 'created', 'last_updated', 'actions', 'utilization',
        )
        default_columns = ('pk', 'name', 'scope_type', 'scope', 'vlan_count', 'utilization', 'description')


#
# VLANs
#

class VLANTable(TenancyColumnsMixin, NetBoxTable):
    vid = tables.TemplateColumn(
        template_code=VLAN_LINK,
        verbose_name=_('VID')
    )
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    site = tables.Column(
        verbose_name=_('Site'),
        linkify=True
    )
    group = tables.Column(
        verbose_name=_('Group'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
        default=AVAILABLE_LABEL
    )
    role = tables.Column(
        verbose_name=_('Role'),
        linkify=True
    )
    qinq_role = columns.ChoiceFieldColumn(
        verbose_name=_('Q-in-Q role')
    )
    qinq_svlan = tables.Column(
        verbose_name=_('Q-in-Q SVLAN'),
        linkify=True
    )
    l2vpn = tables.Column(
        accessor=tables.A('l2vpn_termination__l2vpn'),
        linkify=True,
        orderable=False,
        verbose_name=_('L2VPN')
    )
    prefixes = columns.TemplateColumn(
        template_code=VLAN_PREFIXES,
        orderable=False,
        verbose_name=_('Prefixes')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='ipam:vlan_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VLAN
        fields = (
            'pk', 'id', 'vid', 'name', 'site', 'group', 'prefixes', 'tenant', 'tenant_group', 'status', 'role',
            'qinq_role', 'qinq_svlan', 'description', 'comments', 'tags', 'l2vpn', 'created', 'last_updated',
        )
        default_columns = ('pk', 'vid', 'name', 'site', 'group', 'prefixes', 'tenant', 'status', 'role', 'description')
        row_attrs = {
            'class': lambda record: 'success' if not isinstance(record, VLAN) else '',
        }


class VLANMembersTable(NetBoxTable):
    """
    Base table for Interface and VMInterface assignments
    """
    name = tables.Column(
        linkify=True,
        verbose_name=_('Interface')
    )
    tagged = tables.TemplateColumn(
        verbose_name=_('Tagged'),
        template_code=VLAN_MEMBER_TAGGED,
        orderable=False
    )


class VLANDevicesTable(VLANMembersTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify=True
    )
    actions = columns.ActionsColumn(
        actions=('edit',)
    )

    class Meta(NetBoxTable.Meta):
        model = Interface
        fields = ('device', 'name', 'tagged', 'actions')
        exclude = ('id', )


class VLANVirtualMachinesTable(VLANMembersTable):
    virtual_machine = tables.Column(
        verbose_name=_('Virtual Machine'),
        linkify=True
    )
    actions = columns.ActionsColumn(
        actions=('edit',)
    )

    class Meta(NetBoxTable.Meta):
        model = VMInterface
        fields = ('virtual_machine', 'name', 'tagged', 'actions')
        exclude = ('id', )


class InterfaceVLANTable(NetBoxTable):
    """
    List VLANs assigned to a specific Interface.
    """
    vid = tables.Column(
        linkify=True,
        verbose_name=_('VID')
    )
    tagged = columns.BooleanColumn(
        verbose_name=_('Tagged'),
        false_mark=None
    )
    site = tables.Column(
        verbose_name=_('Site'),
        linkify=True
    )
    group = tables.Column(
        accessor=Accessor('group__name'),
        verbose_name=_('Group')
    )
    tenant = TenantColumn(
        verbose_name=_('Tenant'),
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    role = tables.Column(
        verbose_name=_('Role'),
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = VLAN
        fields = ('vid', 'tagged', 'site', 'group', 'name', 'tenant', 'status', 'role', 'description')
        exclude = ('id', )

    def __init__(self, interface, *args, **kwargs):
        self.interface = interface
        super().__init__(*args, **kwargs)


#
# VLAN Translation
#

class VLANTranslationPolicyTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    rule_count = columns.LinkedCountColumn(
        viewname='ipam:vlantranslationrule_list',
        url_params={'policy_id': 'pk'},
        verbose_name=_('Rules')
    )
    description = tables.Column(
        verbose_name=_('Description'),
    )
    tags = columns.TagColumn(
        url_name='ipam:vlantranslationpolicy_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VLANTranslationPolicy
        fields = (
            'pk', 'id', 'name', 'rule_count', 'description', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'rule_count', 'description')


class VLANTranslationRuleTable(NetBoxTable):
    policy = tables.Column(
        verbose_name=_('Policy'),
        linkify=True
    )
    local_vid = tables.Column(
        verbose_name=_('Local VID'),
        linkify=True
    )
    remote_vid = tables.Column(
        verbose_name=_('Remote VID'),
    )
    description = tables.Column(
        verbose_name=_('Description'),
    )
    tags = columns.TagColumn(
        url_name='ipam:vlantranslationrule_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VLANTranslationRule
        fields = (
            'pk', 'id', 'name', 'policy', 'local_vid', 'remote_vid', 'description', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'policy', 'local_vid', 'remote_vid', 'description')
