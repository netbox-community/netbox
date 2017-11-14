from __future__ import unicode_literals

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
{% if record.pk %}{% utilization_graph record.get_utilization %}{% else %}&mdash;{% endif %}
"""

ROLE_ACTIONS = """
{% if perms.ipam.change_role %}
    <a href="{% url 'ipam:role_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""

PREFIX_LINK = """
{% if record.has_children %}
    <span class="text-nowrap" style="padding-left: {{ record.depth }}0px "><i class="fa fa-caret-right"></i></a>
{% else %}
    <span class="text-nowrap" style="padding-left: {{ record.depth }}9px">
{% endif %}
    <a href="{% if record.pk %}{% url 'ipam:prefix' pk=record.pk %}{% else %}{% url 'ipam:prefix_add' %}?prefix={{ record }}{% if parent.vrf %}&vrf={{ parent.vrf.pk }}{% endif %}{% if parent.site %}&site={{ parent.site.pk }}{% endif %}{% endif %}">{{ record.prefix }}</a>
</span>
"""

PREFIX_LINK_BRIEF = """
<span style="padding-left: {{ record.depth }}0px">
    <a href="{% if record.pk %}{% url 'ipam:prefix' pk=record.pk %}{% else %}{% url 'ipam:prefix_add' %}?prefix={{ record }}{% if parent.vrf %}&vrf={{ parent.vrf.pk }}{% endif %}{% if parent.site %}&site={{ parent.site.pk }}{% endif %}{% endif %}">{{ record.prefix }}</a>
</span>
"""

PREFIX_ROLE_LINK = """
{% if record.role %}
    <a href="{% url 'ipam:prefix_list' %}?role={{ record.role.slug }}">{{ record.role }}</a>
{% else %}
    &mdash;
{% endif %}
"""

IPADDRESS_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}">{{ record.address }}</a>
{% elif perms.ipam.add_ipaddress %}
    <a href="{% url 'ipam:ipaddress_add' %}?address={{ record.1 }}{% if prefix.vrf %}&vrf={{ prefix.vrf.pk }}{% endif %}{% if prefix.tenant %}&tenant={{ prefix.tenant.pk }}{% endif %}" class="btn btn-xs btn-success">{% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available</a>
{% else %}
    {% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available
{% endif %}
"""

IPADDRESS_ASSIGN_LINK = """
<a href="{% url 'ipam:ipaddress_edit' pk=record.pk %}?interface={{ request.GET.interface }}&return_url={{ request.GET.return_url }}">{{ record }}</a>
"""

IPADDRESS_PARENT = """
{% if record.interface %}
    <a href="{{ record.interface.parent.get_absolute_url }}">{{ record.interface.parent }}</a>
{% else %}
    &mdash;
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

VLAN_PREFIXES = """
{% for prefix in record.prefixes.all %}
    <a href="{% url 'ipam:prefix' pk=prefix.pk %}">{{ prefix }}</a>{% if not forloop.last %}<br />{% endif %}
{% empty %}
    &mdash;
{% endfor %}
"""

VLAN_ROLE_LINK = """
{% if record.role %}
    <a href="{% url 'ipam:vlan_list' %}?role={{ record.role.slug }}">{{ record.role }}</a>
{% else %}
    &mdash;
{% endif %}
"""

VLANGROUP_ACTIONS = """
{% with next_vid=record.get_next_available_vid %}
    {% if next_vid and perms.ipam.add_vlan %}
        <a href="{% url 'ipam:vlan_add' %}?site={{ record.site_id }}&group={{ record.pk }}&vid={{ next_vid }}" title="Add VLAN" class="btn btn-xs btn-success">
            <i class="glyphicon glyphicon-plus" aria-hidden="true"></i>
        </a>
    {% endif %}
{% endwith %}
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
    name = tables.LinkColumn()
    rd = tables.Column(verbose_name='RD')
    tenant = tables.LinkColumn('tenancy:tenant', args=[Accessor('tenant.slug')])

    class Meta(BaseTable.Meta):
        model = VRF
        fields = ('pk', 'name', 'rd', 'tenant', 'description')


#
# RIRs
#

class RIRTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    is_private = tables.BooleanColumn(verbose_name='Private')
    aggregate_count = tables.Column(verbose_name='Aggregates')
    actions = tables.TemplateColumn(template_code=RIR_ACTIONS, attrs={'td': {'class': 'text-right'}}, verbose_name='')

    class Meta(BaseTable.Meta):
        model = RIR
        fields = ('pk', 'name', 'is_private', 'aggregate_count', 'actions')


class RIRDetailTable(RIRTable):
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

    class Meta(RIRTable.Meta):
        fields = (
            'pk', 'name', 'is_private', 'aggregate_count', 'stats_total', 'stats_active', 'stats_reserved',
            'stats_deprecated', 'stats_available', 'utilization', 'actions',
        )


#
# Aggregates
#

class AggregateTable(BaseTable):
    pk = ToggleColumn()
    prefix = tables.LinkColumn(verbose_name='Aggregate')
    date_added = tables.DateColumn(format="Y-m-d", verbose_name='Added')

    class Meta(BaseTable.Meta):
        model = Aggregate
        fields = ('pk', 'prefix', 'rir', 'date_added', 'description')


class AggregateDetailTable(AggregateTable):
    child_count = tables.Column(verbose_name='Prefixes')
    utilization = tables.TemplateColumn(UTILIZATION_GRAPH, orderable=False, verbose_name='Utilization')

    class Meta(AggregateTable.Meta):
        fields = ('pk', 'prefix', 'rir', 'child_count', 'utilization', 'date_added', 'description')


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
    prefix = tables.TemplateColumn(PREFIX_LINK, attrs={'th': {'style': 'padding-left: 17px'}})
    status = tables.TemplateColumn(STATUS_LABEL)
    vrf = tables.TemplateColumn(VRF_LINK, verbose_name='VRF')
    tenant = tables.TemplateColumn(TENANT_LINK)
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')])
    vlan = tables.LinkColumn('ipam:vlan', args=[Accessor('vlan.pk')], verbose_name='VLAN')
    role = tables.TemplateColumn(PREFIX_ROLE_LINK)

    class Meta(BaseTable.Meta):
        model = Prefix
        fields = ('pk', 'prefix', 'status', 'vrf', 'tenant', 'site', 'vlan', 'role', 'description')
        row_attrs = {
            'class': lambda record: 'success' if not record.pk else '',
        }


class PrefixDetailTable(PrefixTable):
    utilization = tables.TemplateColumn(UTILIZATION_GRAPH, orderable=False)

    class Meta(PrefixTable.Meta):
        fields = ('pk', 'prefix', 'status', 'vrf', 'utilization', 'tenant', 'site', 'vlan', 'role', 'description')


#
# IPAddresses
#

class IPAddressTable(BaseTable):
    pk = ToggleColumn()
    address = tables.TemplateColumn(IPADDRESS_LINK, verbose_name='IP Address')
    vrf = tables.TemplateColumn(VRF_LINK, verbose_name='VRF')
    status = tables.TemplateColumn(STATUS_LABEL)
    tenant = tables.TemplateColumn(TENANT_LINK)
    parent = tables.TemplateColumn(IPADDRESS_PARENT, orderable=False)
    interface = tables.Column(orderable=False)

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = ('pk', 'address', 'vrf', 'status', 'role', 'tenant', 'parent', 'interface', 'description')
        row_attrs = {
            'class': lambda record: 'success' if not isinstance(record, IPAddress) else '',
        }


class IPAddressDetailTable(IPAddressTable):
    nat_inside = tables.LinkColumn(
        'ipam:ipaddress', args=[Accessor('nat_inside.pk')], orderable=False, verbose_name='NAT (Inside)'
    )

    class Meta(IPAddressTable.Meta):
        fields = (
            'pk', 'address', 'vrf', 'status', 'role', 'tenant', 'nat_inside', 'parent', 'interface', 'description',
        )


class IPAddressAssignTable(BaseTable):
    address = tables.TemplateColumn(IPADDRESS_ASSIGN_LINK, verbose_name='IP Address')
    status = tables.TemplateColumn(STATUS_LABEL)
    parent = tables.TemplateColumn(IPADDRESS_PARENT, orderable=False)
    interface = tables.Column(orderable=False)

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = ('address', 'vrf', 'status', 'role', 'tenant', 'parent', 'interface')
        orderable = False


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
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')])
    group = tables.Column(accessor=Accessor('group.name'), verbose_name='Group')
    tenant = tables.LinkColumn('tenancy:tenant', args=[Accessor('tenant.slug')])
    status = tables.TemplateColumn(STATUS_LABEL)
    role = tables.TemplateColumn(VLAN_ROLE_LINK)

    class Meta(BaseTable.Meta):
        model = VLAN
        fields = ('pk', 'vid', 'site', 'group', 'name', 'tenant', 'status', 'role', 'description')


class VLANDetailTable(VLANTable):
    prefixes = tables.TemplateColumn(VLAN_PREFIXES, orderable=False, verbose_name='Prefixes')

    class Meta(VLANTable.Meta):
        fields = ('pk', 'vid', 'site', 'group', 'name', 'prefixes', 'tenant', 'status', 'role', 'description')
