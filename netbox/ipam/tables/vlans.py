import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import Accessor

from dcim.models import Interface
from tenancy.tables import TenantColumn
from utilities.tables import (
    BaseTable, BooleanColumn, ButtonsColumn, ChoiceFieldColumn, ContentTypeColumn, LinkedCountColumn, TagColumn,
    TemplateColumn, ToggleColumn,
)
from virtualization.models import VMInterface
from ipam.models import *

__all__ = (
    'InterfaceVLANTable',
    'VLANDevicesTable',
    'VLANGroupTable',
    'VLANMembersTable',
    'VLANTable',
    'VLANVirtualMachinesTable',
)

AVAILABLE_LABEL = mark_safe('<span class="badge bg-success">Available</span>')

VLAN_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}">{{ record.vid }}</a>
{% elif perms.ipam.add_vlan %}
    <a href="{% url 'ipam:vlan_add' %}?vid={{ record.vid }}{% if record.vlan_group %}&group={{ record.vlan_group.pk }}{% endif %}" class="btn btn-sm btn-success">{{ record.available }} VLAN{{ record.available|pluralize }} available</a>
{% else %}
    {{ record.available }} VLAN{{ record.available|pluralize }} available
{% endif %}
"""

VLAN_PREFIXES = """
{% for prefix in record.prefixes.all %}
    <a href="{% url 'ipam:prefix' pk=prefix.pk %}">{{ prefix }}</a>{% if not forloop.last %}<br />{% endif %}
{% endfor %}
"""

VLANGROUP_ADD_VLAN = """
{% with next_vid=record.get_next_available_vid %}
    {% if next_vid and perms.ipam.add_vlan %}
        <a href="{% url 'ipam:vlan_add' %}?group={{ record.pk }}&vid={{ next_vid }}" title="Add VLAN" class="btn btn-sm btn-success">
            <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
        </a>
    {% endif %}
{% endwith %}
"""

VLAN_MEMBER_TAGGED = """
{% if record.untagged_vlan_id == object.pk %}
    <span class="text-danger"><i class="mdi mdi-close-thick"></i></span>
{% else %}
    <span class="text-success"><i class="mdi mdi-check-bold"></i></span>
{% endif %}
"""


#
# VLAN groups
#

class VLANGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    scope_type = ContentTypeColumn()
    scope = tables.Column(
        linkify=True,
        orderable=False
    )
    vlan_count = LinkedCountColumn(
        viewname='ipam:vlan_list',
        url_params={'group_id': 'pk'},
        verbose_name='VLANs'
    )
    actions = ButtonsColumn(
        model=VLANGroup,
        prepend_template=VLANGROUP_ADD_VLAN
    )

    class Meta(BaseTable.Meta):
        model = VLANGroup
        fields = ('pk', 'id', 'name', 'scope_type', 'scope', 'vlan_count', 'slug', 'description', 'actions')
        default_columns = ('pk', 'name', 'scope_type', 'scope', 'vlan_count', 'description', 'actions')


#
# VLANs
#

class VLANTable(BaseTable):
    pk = ToggleColumn()
    vid = tables.TemplateColumn(
        template_code=VLAN_LINK,
        verbose_name='ID'
    )
    site = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    tenant = TenantColumn()
    status = ChoiceFieldColumn(
        default=AVAILABLE_LABEL
    )
    role = tables.Column(
        linkify=True
    )
    prefixes = TemplateColumn(
        template_code=VLAN_PREFIXES,
        orderable=False,
        verbose_name='Prefixes'
    )
    tags = TagColumn(
        url_name='ipam:vlan_list'
    )

    class Meta(BaseTable.Meta):
        model = VLAN
        fields = ('pk', 'id', 'vid', 'name', 'site', 'group', 'prefixes', 'tenant', 'status', 'role', 'description', 'tags')
        default_columns = ('pk', 'vid', 'name', 'site', 'group', 'prefixes', 'tenant', 'status', 'role', 'description')
        row_attrs = {
            'class': lambda record: 'success' if not isinstance(record, VLAN) else '',
        }


class VLANMembersTable(BaseTable):
    """
    Base table for Interface and VMInterface assignments
    """
    name = tables.Column(
        linkify=True,
        verbose_name='Interface'
    )
    tagged = tables.TemplateColumn(
        template_code=VLAN_MEMBER_TAGGED,
        orderable=False
    )


class VLANDevicesTable(VLANMembersTable):
    device = tables.Column(
        linkify=True
    )
    actions = ButtonsColumn(Interface, buttons=['edit'])

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('device', 'name', 'tagged', 'actions')
        exclude = ('id', )


class VLANVirtualMachinesTable(VLANMembersTable):
    virtual_machine = tables.Column(
        linkify=True
    )
    actions = ButtonsColumn(VMInterface, buttons=['edit'])

    class Meta(BaseTable.Meta):
        model = VMInterface
        fields = ('virtual_machine', 'name', 'tagged', 'actions')
        exclude = ('id', )


class InterfaceVLANTable(BaseTable):
    """
    List VLANs assigned to a specific Interface.
    """
    vid = tables.Column(
        linkify=True,
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
    tenant = TenantColumn()
    status = ChoiceFieldColumn()
    role = tables.Column(
        linkify=True
    )

    class Meta(BaseTable.Meta):
        model = VLAN
        fields = ('vid', 'tagged', 'site', 'group', 'name', 'tenant', 'status', 'role', 'description')
        exclude = ('id', )

    def __init__(self, interface, *args, **kwargs):
        self.interface = interface
        super().__init__(*args, **kwargs)
