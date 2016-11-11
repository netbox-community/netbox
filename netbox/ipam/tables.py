import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, ToggleColumn

from .models import Aggregate, IPAddress, Prefix, RIR, Role, VLAN, VLANGroup, VRF


RIR_UTILIZATION = """
<div class="progress">
    {% if record.stats.total %}
        <div class="progress-bar" role="progressbar" style="width: {{ record.stats.percentages.active }}%;">
            <span class="sr-only">{{ record.stats.percentages.active }}%</span>
        </div>
        <div class="progress-bar progress-bar-info" role="progressbar" style="width: {{ record.stats.percentages.reserved }}%;">
            <span class="sr-only">{{ record.stats.percentages.reserved }}%</span>
        </div>
        <div class="progress-bar progress-bar-danger" role="progressbar" style="width: {{ record.stats.percentages.deprecated }}%;">
            <span class="sr-only">{{ record.stats.percentages.deprecated }}%</span>
        </div>
        <div class="progress-bar progress-bar-success" role="progressbar" style="width: {{ record.stats.percentages.available }}%;">
            <span class="sr-only">{{ record.stats.percentages.available }}%</span>
        </div>
    {% endif %}
</div>
"""

RIR_ACTIONS = """
{% if perms.ipam.change_rir %}
    <a href="{% url 'ipam:rir_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""

UTILIZATION_GRAPH = """
{% load helpers %}
{% utilization_graph value %}
"""

ROLE_ACTIONS = """
{% if perms.ipam.change_role %}
    <a href="{% url 'ipam:role_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""

PREFIX_LINK = """
{% if record.has_children %}
    <span style="padding-left: {{ record.depth }}0px "><i class="fa fa-caret-right"></i></a>
{% else %}
    <span style="padding-left: {{ record.depth }}9px">
{% endif %}
    <a href="{% if record.pk %}{% url 'ipam:prefix' pk=record.pk %}{% else %}{% url 'ipam:prefix_add' %}?prefix={{ record }}{% if parent.vrf %}&vrf={{ parent.vrf.pk }}{% endif %}{% if parent.site %}&site={{ parent.site.pk }}{% endif %}{% endif %}">{{ record.prefix }}</a>
</span>
"""

PREFIX_LINK_BRIEF = """
<span style="padding-left: {{ record.depth }}0px">
    <a href="{% if record.pk %}{% url 'ipam:prefix' pk=record.pk %}{% else %}{% url 'ipam:prefix_add' %}?prefix={{ record }}{% if parent.vrf %}&vrf={{ parent.vrf.pk }}{% endif %}{% if parent.site %}&site={{ parent.site.pk }}{% endif %}{% endif %}">{{ record.prefix }}</a>
</span>
"""

IPADDRESS_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}">{{ record.address }}</a>
{% elif perms.ipam.add_ipaddress %}
    <a href="{% url 'ipam:ipaddress_add' %}?address={{ record.1 }}{% if prefix.vrf %}&vrf={{ prefix.vrf.pk }}{% endif %}" class="btn btn-xs btn-success">{% if record.0 <= 65536 %}{{ record.0 }}{% else %}Lots of{% endif %} free IP{{ record.0|pluralize }}</a>
{% else %}
    {{ record.0 }}
{% endif %}
"""

VRF_LINK = """
{% if record.vrf %}
    <a href="{{ record.vrf.get_absolute_url }}">{{ record.vrf }}</a>
{% elif prefix.vrf %}
    {{ prefix.vrf }}
{% else %}
    Global
{% endif %}
"""

STATUS_LABEL = """
{% if record.pk %}
    <span class="label label-{{ record.get_status_class }}">{{ record.get_status_display }}</span>
{% else %}
    <span class="label label-success">Available</span>
{% endif %}
"""

VLANGROUP_ACTIONS = """
{% if perms.ipam.change_vlangroup %}
    <a href="{% url 'ipam:vlangroup_edit' pk=record.pk %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""

TENANT_LINK = """
{% if record.tenant %}
    <a href="{% url 'tenancy:tenant' slug=record.tenant.slug %}">{{ record.tenant }}</a>
{% elif record.vrf.tenant %}
    <a href="{% url 'tenancy:tenant' slug=record.vrf.tenant.slug %}">{{ record.vrf.tenant }}</a>*
{% else %}
    &mdash;
{% endif %}
"""


#
# VRFs
#

class VRFTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn('ipam:vrf', args=[Accessor('pk')], verbose_name='Name')
    rd = tables.Column(verbose_name='RD')
    tenant = tables.LinkColumn('tenancy:tenant', args=[Accessor('tenant.slug')], verbose_name='Tenant')
    description = tables.Column(orderable=False, verbose_name='Description')

    class Meta(BaseTable.Meta):
        model = VRF
        fields = ('pk', 'name', 'rd', 'tenant', 'description')


#
# RIRs
#

class RIRTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    aggregate_count = tables.Column(verbose_name='Aggregates')
    stats_total = tables.Column(accessor='stats.total', verbose_name='Total',
                                footer=lambda table: sum(r.stats['total'] for r in table.data))
    stats_active = tables.Column(accessor='stats.active', verbose_name='Active',
                                 footer=lambda table: sum(r.stats['active'] for r in table.data))
    stats_reserved = tables.Column(accessor='stats.reserved', verbose_name='Reserved',
                                   footer=lambda table: sum(r.stats['reserved'] for r in table.data))
    stats_deprecated = tables.Column(accessor='stats.deprecated', verbose_name='Deprecated',
                                     footer=lambda table: sum(r.stats['deprecated'] for r in table.data))
    stats_available = tables.Column(accessor='stats.available', verbose_name='Available',
                                    footer=lambda table: sum(r.stats['available'] for r in table.data))
    utilization = tables.TemplateColumn(template_code=RIR_UTILIZATION, verbose_name='Utilization')
    actions = tables.TemplateColumn(template_code=RIR_ACTIONS, attrs={'td': {'class': 'text-right'}}, verbose_name='')

    class Meta(BaseTable.Meta):
        model = RIR
        fields = ('pk', 'name', 'aggregate_count', 'stats_total', 'stats_active', 'stats_reserved', 'stats_deprecated', 'stats_available', 'utilization', 'actions')


#
# Aggregates
#

class AggregateTable(BaseTable):
    pk = ToggleColumn()
    prefix = tables.LinkColumn('ipam:aggregate', args=[Accessor('pk')], verbose_name='Aggregate')
    rir = tables.Column(verbose_name='RIR')
    child_count = tables.Column(verbose_name='Prefixes')
    get_utilization = tables.TemplateColumn(UTILIZATION_GRAPH, orderable=False, verbose_name='Utilization')
    date_added = tables.DateColumn(format="Y-m-d", verbose_name='Added')
    description = tables.Column(orderable=False, verbose_name='Description')

    class Meta(BaseTable.Meta):
        model = Aggregate
        fields = ('pk', 'prefix', 'rir', 'child_count', 'get_utilization', 'date_added', 'description')


#
# Roles
#

class RoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(verbose_name='Name')
    prefix_count = tables.Column(accessor=Accessor('count_prefixes'), orderable=False, verbose_name='Prefixes')
    vlan_count = tables.Column(accessor=Accessor('count_vlans'), orderable=False, verbose_name='VLANs')
    slug = tables.Column(verbose_name='Slug')
    actions = tables.TemplateColumn(template_code=ROLE_ACTIONS, attrs={'td': {'class': 'text-right'}}, verbose_name='')

    class Meta(BaseTable.Meta):
        model = Role
        fields = ('pk', 'name', 'prefix_count', 'vlan_count', 'slug', 'actions')


#
# Prefixes
#

class PrefixTable(BaseTable):
    pk = ToggleColumn()
    status = tables.TemplateColumn(STATUS_LABEL, verbose_name='Status')
    prefix = tables.TemplateColumn(PREFIX_LINK, verbose_name='Prefix')
    vrf = tables.TemplateColumn(VRF_LINK, verbose_name='VRF')
    tenant = tables.TemplateColumn(TENANT_LINK, verbose_name='Tenant')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    role = tables.Column(verbose_name='Role')
    description = tables.Column(orderable=False, verbose_name='Description')

    class Meta(BaseTable.Meta):
        model = Prefix
        fields = ('pk', 'prefix', 'status', 'vrf', 'tenant', 'site', 'role', 'description')
        row_attrs = {
            'class': lambda record: 'success' if not record.pk else '',
        }


class PrefixBriefTable(BaseTable):
    prefix = tables.TemplateColumn(PREFIX_LINK_BRIEF, verbose_name='Prefix')
    vrf = tables.LinkColumn('ipam:vrf', args=[Accessor('vrf.pk')], default='Global', verbose_name='VRF')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    status = tables.TemplateColumn(STATUS_LABEL, verbose_name='Status')
    role = tables.Column(verbose_name='Role')

    class Meta(BaseTable.Meta):
        model = Prefix
        fields = ('prefix', 'vrf', 'status', 'site', 'role')
        orderable = False


#
# IPAddresses
#

class IPAddressTable(BaseTable):
    pk = ToggleColumn()
    address = tables.TemplateColumn(IPADDRESS_LINK, verbose_name='IP Address')
    status = tables.TemplateColumn(STATUS_LABEL, verbose_name='Status')
    vrf = tables.TemplateColumn(VRF_LINK, verbose_name='VRF')
    tenant = tables.TemplateColumn(TENANT_LINK, verbose_name='Tenant')
    device = tables.LinkColumn('dcim:device', args=[Accessor('interface.device.pk')], orderable=False,
                               verbose_name='Device')
    interface = tables.Column(orderable=False, verbose_name='Interface')
    description = tables.Column(orderable=False, verbose_name='Description')

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = ('pk', 'address', 'status', 'vrf', 'tenant', 'device', 'interface', 'description')
        row_attrs = {
            'class': lambda record: 'success' if not isinstance(record, IPAddress) else '',
        }


class IPAddressBriefTable(BaseTable):
    address = tables.LinkColumn('ipam:ipaddress', args=[Accessor('pk')], verbose_name='IP Address')
    device = tables.LinkColumn('dcim:device', args=[Accessor('interface.device.pk')], orderable=False,
                               verbose_name='Device')
    interface = tables.Column(orderable=False, verbose_name='Interface')
    nat_inside = tables.LinkColumn('ipam:ipaddress', args=[Accessor('nat_inside.pk')], orderable=False,
                                   verbose_name='NAT (Inside)')

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = ('address', 'device', 'interface', 'nat_inside')


#
# VLAN groups
#

class VLANGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    vlan_count = tables.Column(verbose_name='VLANs')
    slug = tables.Column(verbose_name='Slug')
    actions = tables.TemplateColumn(template_code=VLANGROUP_ACTIONS, attrs={'td': {'class': 'text-right'}},
                                    verbose_name='')

    class Meta(BaseTable.Meta):
        model = VLANGroup
        fields = ('pk', 'name', 'site', 'vlan_count', 'slug', 'actions')


#
# VLANs
#

class VLANTable(BaseTable):
    pk = ToggleColumn()
    vid = tables.LinkColumn('ipam:vlan', args=[Accessor('pk')], verbose_name='ID')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    group = tables.Column(accessor=Accessor('group.name'), verbose_name='Group')
    name = tables.Column(verbose_name='Name')
    tenant = tables.LinkColumn('tenancy:tenant', args=[Accessor('tenant.slug')], verbose_name='Tenant')
    status = tables.TemplateColumn(STATUS_LABEL, verbose_name='Status')
    role = tables.Column(verbose_name='Role')

    class Meta(BaseTable.Meta):
        model = VLAN
        fields = ('pk', 'vid', 'site', 'group', 'name', 'tenant', 'status', 'role')
