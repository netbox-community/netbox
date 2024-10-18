from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import Accessor

from ipam.models import *
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin, TenantColumn

__all__ = (
    'AggregateTable',
    'AssignedIPAddressesTable',
    'IPAddressAssignTable',
    'IPAddressTable',
    'IPRangeTable',
    'PrefixTable',
    'RIRTable',
    'RoleTable',
)

AVAILABLE_LABEL = mark_safe('<span class="badge text-bg-success">Available</span>')

AGGREGATE_COPY_BUTTON = """
{% copy_content record.pk prefix="aggregate_" %}
"""

PREFIX_LINK = """
{% if record.pk %}
  <a href="{{ record.get_absolute_url }}" id="prefix_{{ record.pk }}">{{ record.prefix }}</a>
{% else %}
  <a href="{% url 'ipam:prefix_add' %}?prefix={{ record }}{% if object.vrf %}&vrf={{ object.vrf.pk }}{% endif %}{% if object.site %}&site={{ object.site.pk }}{% endif %}{% if object.tenant %}&tenant_group={{ object.tenant.group.pk }}&tenant={{ object.tenant.pk }}{% endif %}">{{ record.prefix }}</a>
{% endif %}
"""

PREFIX_COPY_BUTTON = """
{% copy_content record.pk prefix="prefix_" %}
"""

PREFIX_LINK_WITH_DEPTH = """
{% load helpers %}
{% if record.depth %}
    <div class="record-depth">
        {% for i in record.depth|as_range %}
            <span>•</span>
        {% endfor %}
    </div>
{% endif %}
""" + PREFIX_LINK

IPADDRESS_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}" id="ipaddress_{{ record.pk }}">{{ record.address }}</a>
{% elif perms.ipam.add_ipaddress %}
    <a href="{% url 'ipam:ipaddress_add' %}?address={{ record.1 }}{% if object.vrf %}&vrf={{ object.vrf.pk }}{% endif %}{% if object.tenant %}&tenant={{ object.tenant.pk }}{% endif %}&return_url={% url 'ipam:prefix_ipaddresses' pk=object.pk %}" class="btn btn-sm btn-success">{% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available</a>
{% else %}
    {% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available
{% endif %}
"""

IPADDRESS_COPY_BUTTON = """
{% copy_content record.pk prefix="ipaddress_" %}
"""

IPADDRESS_ASSIGN_LINK = """
<a href="{% url 'ipam:ipaddress_edit' pk=record.pk %}?{% if request.GET.interface %}interface={{ request.GET.interface }}{% elif request.GET.vminterface %}vminterface={{ request.GET.vminterface }}{% endif %}&return_url={{ request.GET.return_url }}">{{ record }}</a>
"""

VRF_LINK = """
{% if value %}
    <a href="{{ record.vrf.get_absolute_url }}">{{ record.vrf }}</a>
{% elif object.vrf %}
    <a href="{{ object.vrf.get_absolute_url }}">{{ object.vrf }}</a>
{% else %}
    Global
{% endif %}
"""


#
# RIRs
#

class RIRTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    is_private = columns.BooleanColumn(
        verbose_name=_('Private'),
        false_mark=None
    )
    aggregate_count = columns.LinkedCountColumn(
        viewname='ipam:aggregate_list',
        url_params={'rir_id': 'pk'},
        verbose_name=_('Aggregates')
    )
    tags = columns.TagColumn(
        url_name='ipam:rir_list'
    )

    class Meta(NetBoxTable.Meta):
        model = RIR
        fields = (
            'pk', 'id', 'name', 'slug', 'is_private', 'aggregate_count', 'description', 'tags', 'created',
            'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'is_private', 'aggregate_count', 'description')


#
# Aggregates
#

class AggregateTable(TenancyColumnsMixin, NetBoxTable):
    prefix = tables.Column(
        linkify=True,
        verbose_name=_('Aggregate'),
        attrs={
            # Allow the aggregate to be copied to the clipboard
            'a': {'id': lambda record: f"aggregate_{record.pk}"}
        }
    )
    date_added = tables.DateColumn(
        format="Y-m-d",
        verbose_name=_('Added')
    )
    child_count = tables.Column(
        verbose_name=_('Prefixes')
    )
    utilization = columns.UtilizationColumn(
        verbose_name=_('Utilization'),
        accessor='get_utilization',
        orderable=False
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='ipam:aggregate_list'
    )
    actions = columns.ActionsColumn(
        extra_buttons=AGGREGATE_COPY_BUTTON
    )

    class Meta(NetBoxTable.Meta):
        model = Aggregate
        fields = (
            'pk', 'id', 'prefix', 'rir', 'tenant', 'tenant_group', 'child_count', 'utilization', 'date_added',
            'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'prefix', 'rir', 'tenant', 'child_count', 'utilization', 'date_added', 'description')


#
# Roles
#

class RoleTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    prefix_count = columns.LinkedCountColumn(
        viewname='ipam:prefix_list',
        url_params={'role_id': 'pk'},
        verbose_name=_('Prefixes')
    )
    iprange_count = columns.LinkedCountColumn(
        viewname='ipam:iprange_list',
        url_params={'role_id': 'pk'},
        verbose_name=_('IP Ranges')
    )
    vlan_count = columns.LinkedCountColumn(
        viewname='ipam:vlan_list',
        url_params={'role_id': 'pk'},
        verbose_name=_('VLANs')
    )
    tags = columns.TagColumn(
        url_name='ipam:role_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Role
        fields = (
            'pk', 'id', 'name', 'slug', 'prefix_count', 'iprange_count', 'vlan_count', 'description', 'weight', 'tags',
            'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'prefix_count', 'iprange_count', 'vlan_count', 'description')


#
# Prefixes
#

class PrefixUtilizationColumn(columns.UtilizationColumn):
    """
    Extend UtilizationColumn to allow disabling the warning & danger thresholds for prefixes
    marked as fully utilized.
    """
    template_code = """
    {% load helpers %}
    {% if record.pk and record.mark_utilized %}
      {% utilization_graph value warning_threshold=0 danger_threshold=0 %}
    {% elif record.pk %}
      {% utilization_graph value %}
    {% endif %}
    """


class PrefixTable(TenancyColumnsMixin, NetBoxTable):
    prefix = columns.TemplateColumn(
        verbose_name=_('Prefix'),
        template_code=PREFIX_LINK_WITH_DEPTH,
        export_raw=True,
        attrs={'td': {'class': 'text-nowrap'}}
    )
    prefix_flat = columns.TemplateColumn(
        accessor=Accessor('prefix'),
        template_code=PREFIX_LINK,
        export_raw=True,
        verbose_name=_('Prefix (Flat)')
    )
    depth = tables.Column(
        accessor=Accessor('_depth'),
        verbose_name=_('Depth')
    )
    children = columns.LinkedCountColumn(
        accessor=Accessor('_children'),
        viewname='ipam:prefix_list',
        url_params={
            'vrf_id': 'vrf_id',
            'within': 'prefix',
        },
        verbose_name=_('Children')
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
        default=AVAILABLE_LABEL
    )
    vrf = tables.TemplateColumn(
        template_code=VRF_LINK,
        verbose_name=_('VRF')
    )
    scope_type = columns.ContentTypeColumn(
        verbose_name=_('Scope Type'),
    )
    scope = tables.Column(
        verbose_name=_('Scope'),
        linkify=True
    )
    vlan_group = tables.Column(
        accessor='vlan__group',
        linkify=True,
        verbose_name=_('VLAN Group')
    )
    vlan = tables.Column(
        linkify=True,
        verbose_name=_('VLAN')
    )
    role = tables.Column(
        verbose_name=_('Role'),
        linkify=True
    )
    is_pool = columns.BooleanColumn(
        verbose_name=_('Pool'),
        false_mark=None
    )
    mark_utilized = columns.BooleanColumn(
        verbose_name=_('Marked Utilized'),
        false_mark=None
    )
    utilization = PrefixUtilizationColumn(
        verbose_name=_('Utilization'),
        accessor='get_utilization',
        orderable=False
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='ipam:prefix_list'
    )
    actions = columns.ActionsColumn(
        extra_buttons=PREFIX_COPY_BUTTON
    )

    class Meta(NetBoxTable.Meta):
        model = Prefix
        fields = (
            'pk', 'id', 'prefix', 'prefix_flat', 'status', 'children', 'vrf', 'utilization', 'tenant', 'tenant_group',
            'scope', 'scope_type', 'vlan_group', 'vlan', 'role', 'is_pool', 'mark_utilized', 'description', 'comments',
            'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'prefix', 'status', 'children', 'vrf', 'utilization', 'tenant', 'scope', 'vlan', 'role',
            'description',
        )
        row_attrs = {
            'class': lambda record: 'success' if not record.pk else '',
        }


#
# IP ranges
#
class IPRangeTable(TenancyColumnsMixin, NetBoxTable):
    start_address = tables.Column(
        verbose_name=_('Start address'),
        linkify=True
    )
    vrf = tables.TemplateColumn(
        template_code=VRF_LINK,
        verbose_name=_('VRF')
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
        default=AVAILABLE_LABEL
    )
    role = tables.Column(
        verbose_name=_('Role'),
        linkify=True
    )
    mark_utilized = columns.BooleanColumn(
        verbose_name=_('Marked Utilized'),
        false_mark=None
    )
    utilization = columns.UtilizationColumn(
        verbose_name=_('Utilization'),
        accessor='utilization',
        orderable=False
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='ipam:iprange_list'
    )

    class Meta(NetBoxTable.Meta):
        model = IPRange
        fields = (
            'pk', 'id', 'start_address', 'end_address', 'size', 'vrf', 'status', 'role', 'tenant', 'tenant_group',
            'mark_utilized', 'utilization', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'start_address', 'end_address', 'size', 'vrf', 'status', 'role', 'tenant', 'description',
        )
        row_attrs = {
            'class': lambda record: 'success' if not record.pk else '',
        }


#
# IPAddresses
#

class IPAddressTable(TenancyColumnsMixin, NetBoxTable):
    address = tables.TemplateColumn(
        template_code=IPADDRESS_LINK,
        verbose_name=_('IP Address')
    )
    vrf = tables.TemplateColumn(
        template_code=VRF_LINK,
        verbose_name=_('VRF')
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
        default=AVAILABLE_LABEL
    )
    role = columns.ChoiceFieldColumn(
        verbose_name=_('Role'),
    )
    assigned_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name=_('Interface')
    )
    assigned_object_parent = tables.Column(
        accessor='assigned_object__parent_object',
        linkify=True,
        orderable=False,
        verbose_name=_('Parent')
    )
    nat_inside = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name=_('NAT (Inside)')
    )
    nat_outside = columns.ManyToManyColumn(
        linkify_item=True,
        orderable=False,
        verbose_name=_('NAT (Outside)')
    )
    assigned = columns.BooleanColumn(
        accessor='assigned_object_id',
        linkify=lambda record: record.assigned_object.get_absolute_url(),
        verbose_name=_('Assigned'),
        false_mark=None
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='ipam:ipaddress_list'
    )
    actions = columns.ActionsColumn(
        extra_buttons=IPADDRESS_COPY_BUTTON
    )

    class Meta(NetBoxTable.Meta):
        model = IPAddress
        fields = (
            'pk', 'id', 'address', 'vrf', 'status', 'role', 'tenant', 'tenant_group', 'nat_inside', 'nat_outside',
            'assigned', 'dns_name', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'address', 'vrf', 'status', 'role', 'tenant', 'assigned', 'dns_name', 'description',
        )
        row_attrs = {
            'class': lambda record: 'success' if not isinstance(record, IPAddress) else '',
        }


class IPAddressAssignTable(NetBoxTable):
    address = tables.TemplateColumn(
        template_code=IPADDRESS_ASSIGN_LINK,
        verbose_name=_('IP Address')
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    assigned_object = tables.Column(
        verbose_name=_('Assigned Object'),
        orderable=False
    )

    class Meta(NetBoxTable.Meta):
        model = IPAddress
        fields = ('address', 'dns_name', 'vrf', 'status', 'role', 'tenant', 'assigned_object', 'description')
        exclude = ('id', )
        orderable = False


class AssignedIPAddressesTable(NetBoxTable):
    """
    List IP addresses assigned to an object.
    """
    address = tables.Column(
        linkify=True,
        verbose_name=_('IP Address')
    )
    vrf = tables.TemplateColumn(
        template_code=VRF_LINK,
        verbose_name=_('VRF')
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    tenant = TenantColumn(
        verbose_name=_('Tenant'),
    )

    class Meta(NetBoxTable.Meta):
        model = IPAddress
        fields = ('address', 'vrf', 'status', 'role', 'tenant', 'description')
        exclude = ('id', )
