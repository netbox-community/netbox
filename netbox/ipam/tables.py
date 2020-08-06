import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import Interface
from tenancy.tables import COL_TENANT
from utilities.tables import BaseTable, BooleanColumn, ButtonsColumn, TagColumn, ToggleColumn
from .models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF

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

UTILIZATION_GRAPH = """
{% load helpers %}
{% if record.pk %}{% utilization_graph record.get_utilization %}{% else %}&mdash;{% endif %}
"""

ROLE_PREFIX_COUNT = """
<a href="{% url 'ipam:prefix_list' %}?role={{ record.slug }}">{{ value|default:0 }}</a>
"""

ROLE_VLAN_COUNT = """
<a href="{% url 'ipam:vlan_list' %}?role={{ record.slug }}">{{ value|default:0 }}</a>
"""

PREFIX_LINK = """
{% if record.children %}
    <span class="text-nowrap" style="padding-left: {{ record.parents }}0px "><i class="fa fa-caret-right"></i></a>
{% else %}
    <span class="text-nowrap" style="padding-left: {{ record.parents }}9px">
{% endif %}
    <a href="{% if record.pk %}{% url 'ipam:prefix' pk=record.pk %}{% else %}{% url 'ipam:prefix_add' %}?prefix={{ record }}{% if parent.vrf %}&vrf={{ parent.vrf.pk }}{% endif %}{% if parent.site %}&site={{ parent.site.pk }}{% endif %}{% if parent.tenant %}&tenant_group={{ parent.tenant.group.pk }}&tenant={{ parent.tenant.pk }}{% endif %}{% endif %}">{{ record.prefix }}</a>
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
{% if request.GET %}
    <a href="{% url 'ipam:ipaddress_edit' pk=record.pk %}?interface={{ request.GET.interface }}&return_url={{ request.GET.return_url }}">{{ record }}</a>
{% else %}
    <a href="{% url 'ipam:ipaddress_edit' pk=record.pk %}?interface={{ record.interface.pk }}&return_url={{ request.path }}">{{ record }}</a>
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

VLAN_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}">{{ record.vid }}</a>
{% elif perms.ipam.add_vlan %}
    <a href="{% url 'ipam:vlan_add' %}?vid={{ record.vid }}&group={{ vlan_group.pk }}{% if vlan_group.site %}&site={{ vlan_group.site.pk }}{% endif %}" class="btn btn-xs btn-success">{{ record.available }} VLAN{{ record.available|pluralize }} available</a>
{% else %}
    {{ record.available }} VLAN{{ record.available|pluralize }} available
{% endif %}
"""

VLAN_PREFIXES = """
{% for prefix in record.prefixes.unrestricted %}
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

VLANGROUP_ADD_VLAN = """
{% with next_vid=record.get_next_available_vid %}
    {% if next_vid and perms.ipam.add_vlan %}
        <a href="{% url 'ipam:vlan_add' %}?site={{ record.site_id }}&group={{ record.pk }}&vid={{ next_vid }}" title="Add VLAN" class="btn btn-xs btn-success">
            <i class="glyphicon glyphicon-plus" aria-hidden="true"></i>
        </a>
    {% endif %}
{% endwith %}
"""

VLAN_MEMBER_UNTAGGED = """
{% if record.untagged_vlan_id == vlan.pk %}
    <i class="glyphicon glyphicon-ok">
{% endif %}
"""

VLAN_MEMBER_ACTIONS = """
{% if perms.dcim.change_interface %}
    <a href="{% if record.device %}{% url 'dcim:interface_edit' pk=record.pk %}{% else %}{% url 'virtualization:vminterface_edit' pk=record.pk %}{% endif %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil"></i></a>
{% endif %}
"""

TENANT_LINK = """
{% if record.tenant %}
    <a href="{% url 'tenancy:tenant' slug=record.tenant.slug %}" title="{{ record.tenant.description }}">{{ record.tenant }}</a>
{% elif record.vrf.tenant %}
    <a href="{% url 'tenancy:tenant' slug=record.vrf.tenant.slug %}" title="{{ record.vrf.tenant.description }}">{{ record.vrf.tenant }}</a>*
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
    rd = tables.Column(
        verbose_name='RD'
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    enforce_unique = BooleanColumn(
        verbose_name='Unique'
    )
    tags = TagColumn(
        url_name='ipam:vrf_list'
    )

    class Meta(BaseTable.Meta):
        model = VRF
        fields = ('pk', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'tags')
        default_columns = ('pk', 'name', 'rd', 'tenant', 'description')


#
# RIRs
#

class RIRTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    is_private = BooleanColumn(
        verbose_name='Private'
    )
    aggregate_count = tables.Column(
        verbose_name='Aggregates'
    )
    actions = ButtonsColumn(RIR, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = RIR
        fields = ('pk', 'name', 'slug', 'is_private', 'aggregate_count', 'description', 'actions')
        default_columns = ('pk', 'name', 'is_private', 'aggregate_count', 'description', 'actions')


class RIRDetailTable(RIRTable):
    stats_total = tables.Column(
        accessor='stats.total',
        verbose_name='Total',
        footer=lambda table: sum(r.stats['total'] for r in table.data)
    )
    stats_active = tables.Column(
        accessor='stats.active',
        verbose_name='Active',
        footer=lambda table: sum(r.stats['active'] for r in table.data)
    )
    stats_reserved = tables.Column(
        accessor='stats.reserved',
        verbose_name='Reserved',
        footer=lambda table: sum(r.stats['reserved'] for r in table.data)
    )
    stats_deprecated = tables.Column(
        accessor='stats.deprecated',
        verbose_name='Deprecated',
        footer=lambda table: sum(r.stats['deprecated'] for r in table.data)
    )
    stats_available = tables.Column(
        accessor='stats.available',
        verbose_name='Available',
        footer=lambda table: sum(r.stats['available'] for r in table.data)
    )
    utilization = tables.TemplateColumn(
        template_code=RIR_UTILIZATION,
        verbose_name='Utilization'
    )

    class Meta(RIRTable.Meta):
        fields = (
            'pk', 'name', 'slug', 'is_private', 'aggregate_count', 'stats_total', 'stats_active', 'stats_reserved',
            'stats_deprecated', 'stats_available', 'utilization', 'actions',
        )
        default_columns = (
            'pk', 'name', 'is_private', 'aggregate_count', 'stats_total', 'stats_active', 'stats_reserved',
            'stats_deprecated', 'stats_available', 'utilization', 'actions',
        )


#
# Aggregates
#

class AggregateTable(BaseTable):
    pk = ToggleColumn()
    prefix = tables.LinkColumn(
        verbose_name='Aggregate'
    )
    date_added = tables.DateColumn(
        format="Y-m-d",
        verbose_name='Added'
    )

    class Meta(BaseTable.Meta):
        model = Aggregate
        fields = ('pk', 'prefix', 'rir', 'date_added', 'description')


class AggregateDetailTable(AggregateTable):
    child_count = tables.Column(
        verbose_name='Prefixes'
    )
    utilization = tables.TemplateColumn(
        template_code=UTILIZATION_GRAPH,
        orderable=False
    )
    tags = TagColumn(
        url_name='ipam:aggregate_list'
    )

    class Meta(AggregateTable.Meta):
        fields = ('pk', 'prefix', 'rir', 'child_count', 'utilization', 'date_added', 'description', 'tags')
        default_columns = ('pk', 'prefix', 'rir', 'child_count', 'utilization', 'date_added', 'description')


#
# Roles
#

class RoleTable(BaseTable):
    pk = ToggleColumn()
    prefix_count = tables.TemplateColumn(
        template_code=ROLE_PREFIX_COUNT,
        verbose_name='Prefixes'
    )
    vlan_count = tables.TemplateColumn(
        template_code=ROLE_VLAN_COUNT,
        verbose_name='VLANs'
    )
    actions = ButtonsColumn(Role, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = Role
        fields = ('pk', 'name', 'slug', 'prefix_count', 'vlan_count', 'description', 'weight', 'actions')
        default_columns = ('pk', 'name', 'prefix_count', 'vlan_count', 'description', 'actions')


#
# Prefixes
#

class PrefixTable(BaseTable):
    pk = ToggleColumn()
    prefix = tables.TemplateColumn(
        template_code=PREFIX_LINK,
        attrs={'th': {'style': 'padding-left: 17px'}}
    )
    status = tables.TemplateColumn(
        template_code=STATUS_LABEL
    )
    vrf = tables.TemplateColumn(
        template_code=VRF_LINK,
        verbose_name='VRF'
    )
    tenant = tables.TemplateColumn(
        template_code=TENANT_LINK
    )
    site = tables.Column(
        linkify=True
    )
    vlan = tables.Column(
        linkify=True,
        verbose_name='VLAN'
    )
    role = tables.TemplateColumn(
        template_code=PREFIX_ROLE_LINK
    )
    is_pool = BooleanColumn(
        verbose_name='Pool'
    )

    add_prefetch = False

    class Meta(BaseTable.Meta):
        model = Prefix
        fields = (
            'pk', 'prefix', 'status', 'children', 'vrf', 'tenant', 'site', 'vlan', 'role', 'is_pool', 'description',
        )
        default_columns = ('pk', 'prefix', 'status', 'vrf', 'tenant', 'site', 'vlan', 'role', 'description')
        row_attrs = {
            'class': lambda record: 'success' if not record.pk else '',
        }


class PrefixDetailTable(PrefixTable):
    utilization = tables.TemplateColumn(
        template_code=UTILIZATION_GRAPH,
        orderable=False
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    tags = TagColumn(
        url_name='ipam:prefix_list'
    )

    class Meta(PrefixTable.Meta):
        fields = (
            'pk', 'prefix', 'status', 'children', 'vrf', 'utilization', 'tenant', 'site', 'vlan', 'role', 'is_pool',
            'description', 'tags',
        )
        default_columns = (
            'pk', 'prefix', 'status', 'children', 'vrf', 'utilization', 'tenant', 'site', 'vlan', 'role', 'description',
        )


#
# IPAddresses
#

class IPAddressTable(BaseTable):
    pk = ToggleColumn()
    address = tables.TemplateColumn(
        template_code=IPADDRESS_LINK,
        verbose_name='IP Address'
    )
    vrf = tables.TemplateColumn(
        template_code=VRF_LINK,
        verbose_name='VRF'
    )
    status = tables.TemplateColumn(
        template_code=STATUS_LABEL
    )
    tenant = tables.TemplateColumn(
        template_code=TENANT_LINK
    )
    assigned = tables.BooleanColumn(
        accessor='assigned_object_id',
        verbose_name='Assigned'
    )

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = (
            'pk', 'address', 'vrf', 'status', 'role', 'tenant', 'assigned', 'dns_name', 'description',
        )
        row_attrs = {
            'class': lambda record: 'success' if not isinstance(record, IPAddress) else '',
        }


class IPAddressDetailTable(IPAddressTable):
    nat_inside = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name='NAT (Inside)'
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    tags = TagColumn(
        url_name='ipam:ipaddress_list'
    )

    class Meta(IPAddressTable.Meta):
        fields = (
            'pk', 'address', 'vrf', 'status', 'role', 'tenant', 'nat_inside', 'assigned', 'dns_name',
            'description', 'tags',
        )
        default_columns = (
            'pk', 'address', 'vrf', 'status', 'role', 'tenant', 'assigned', 'dns_name', 'description',
        )


class IPAddressAssignTable(BaseTable):
    address = tables.TemplateColumn(
        template_code=IPADDRESS_ASSIGN_LINK,
        verbose_name='IP Address'
    )
    status = tables.TemplateColumn(
        template_code=STATUS_LABEL
    )
    assigned_object = tables.Column(
        orderable=False
    )

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = ('address', 'dns_name', 'vrf', 'status', 'role', 'tenant', 'assigned_object', 'description')
        orderable = False


class InterfaceIPAddressTable(BaseTable):
    """
    List IP addresses assigned to a specific Interface.
    """
    address = tables.LinkColumn(
        verbose_name='IP Address'
    )
    vrf = tables.TemplateColumn(
        template_code=VRF_LINK,
        verbose_name='VRF'
    )
    status = tables.TemplateColumn(
        template_code=STATUS_LABEL
    )
    tenant = tables.TemplateColumn(
        template_code=TENANT_LINK
    )

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = ('address', 'vrf', 'status', 'role', 'tenant', 'description')


#
# VLAN groups
#

class VLANGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    site = tables.LinkColumn(
        viewname='dcim:site',
        args=[Accessor('site__slug')]
    )
    vlan_count = tables.Column(
        verbose_name='VLANs'
    )
    actions = ButtonsColumn(
        model=VLANGroup,
        prepend_template=VLANGROUP_ADD_VLAN
    )

    class Meta(BaseTable.Meta):
        model = VLANGroup
        fields = ('pk', 'name', 'site', 'vlan_count', 'slug', 'description', 'actions')
        default_columns = ('pk', 'name', 'site', 'vlan_count', 'description', 'actions')


#
# VLANs
#

class VLANTable(BaseTable):
    pk = ToggleColumn()
    vid = tables.TemplateColumn(
        template_code=VLAN_LINK,
        verbose_name='ID'
    )
    site = tables.LinkColumn(
        viewname='dcim:site',
        args=[Accessor('site__slug')]
    )
    group = tables.LinkColumn(
        viewname='ipam:vlangroup_vlans',
        args=[Accessor('group__pk')]
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    status = tables.TemplateColumn(
        template_code=STATUS_LABEL
    )
    role = tables.TemplateColumn(
        template_code=VLAN_ROLE_LINK
    )

    class Meta(BaseTable.Meta):
        model = VLAN
        fields = ('pk', 'vid', 'site', 'group', 'name', 'tenant', 'status', 'role', 'description')
        row_attrs = {
            'class': lambda record: 'success' if not isinstance(record, VLAN) else '',
        }


class VLANDetailTable(VLANTable):
    prefixes = tables.TemplateColumn(
        template_code=VLAN_PREFIXES,
        orderable=False,
        verbose_name='Prefixes'
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    tags = TagColumn(
        url_name='ipam:vlan_list'
    )

    class Meta(VLANTable.Meta):
        fields = ('pk', 'vid', 'site', 'group', 'name', 'prefixes', 'tenant', 'status', 'role', 'description', 'tags')
        default_columns = ('pk', 'vid', 'site', 'group', 'name', 'prefixes', 'tenant', 'status', 'role', 'description')


class VLANMemberTable(BaseTable):
    parent = tables.LinkColumn(
        order_by=['device', 'virtual_machine']
    )
    name = tables.LinkColumn(
        verbose_name='Interface'
    )
    untagged = tables.TemplateColumn(
        template_code=VLAN_MEMBER_UNTAGGED,
        orderable=False
    )
    actions = tables.TemplateColumn(
        template_code=VLAN_MEMBER_ACTIONS,
        attrs={'td': {'class': 'text-right noprint'}},
        verbose_name=''
    )

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('parent', 'name', 'untagged', 'actions')


class InterfaceVLANTable(BaseTable):
    """
    List VLANs assigned to a specific Interface.
    """
    vid = tables.LinkColumn(
        viewname='ipam:vlan',
        args=[Accessor('pk')],
        verbose_name='ID'
    )
    tagged = BooleanColumn()
    site = tables.Column(
        linkify=True
    )
    group = tables.Column(
        accessor=Accessor('group__name'),
        verbose_name='Group'
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    status = tables.TemplateColumn(
        template_code=STATUS_LABEL
    )
    role = tables.TemplateColumn(
        template_code=VLAN_ROLE_LINK
    )

    class Meta(BaseTable.Meta):
        model = VLAN
        fields = ('vid', 'tagged', 'site', 'group', 'name', 'tenant', 'status', 'role', 'description')

    def __init__(self, interface, *args, **kwargs):
        self.interface = interface
        super().__init__(*args, **kwargs)


#
# Services
#

class ServiceTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    parent = tables.LinkColumn(
        order_by=('device', 'virtual_machine')
    )
    tags = TagColumn(
        url_name='ipam:service_list'
    )

    class Meta(BaseTable.Meta):
        model = Service
        fields = ('pk', 'name', 'parent', 'protocol', 'port', 'ipaddresses', 'description', 'tags')
        default_columns = ('pk', 'name', 'parent', 'protocol', 'port', 'description')
