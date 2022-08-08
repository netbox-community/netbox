import django_tables2 as tables

from dcim.tables.devices import BaseInterfaceTable
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin
from virtualization.models import VirtualMachine, VMInterface

__all__ = (
    'VirtualMachineTable',
    'VirtualMachineVMInterfaceTable',
    'VMInterfaceTable',
)

VMINTERFACE_BUTTONS = """
{% if perms.ipam.add_ipaddress %}
    <a href="{% url 'ipam:ipaddress_add' %}?vminterface={{ record.pk }}&return_url={% url 'virtualization:virtualmachine_interfaces' pk=object.pk %}" class="btn btn-sm btn-success" title="Add IP Address">
        <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
    </a>
{% endif %}
"""


#
# Virtual machines
#

class VirtualMachineTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        order_by=('_name',),
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    cluster = tables.Column(
        linkify=True
    )
    role = columns.ColoredLabelColumn()
    comments = columns.MarkdownColumn()
    primary_ip4 = tables.Column(
        linkify=True,
        verbose_name='IPv4 Address'
    )
    primary_ip6 = tables.Column(
        linkify=True,
        verbose_name='IPv6 Address'
    )
    primary_ip = tables.Column(
        linkify=True,
        order_by=('primary_ip4', 'primary_ip6'),
        verbose_name='IP Address'
    )
    contacts = columns.ManyToManyColumn(
        linkify_item=True
    )
    tags = columns.TagColumn(
        url_name='virtualization:virtualmachine_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VirtualMachine
        fields = (
            'pk', 'id', 'name', 'status', 'cluster', 'role', 'tenant', 'tenant_group', 'platform', 'vcpus', 'memory',
            'disk', 'primary_ip4', 'primary_ip6', 'primary_ip', 'comments', 'contacts', 'tags', 'created',
            'last_updated',
        )
        default_columns = (
            'pk', 'name', 'status', 'cluster', 'role', 'tenant', 'vcpus', 'memory', 'disk', 'primary_ip',
        )


#
# VM components
#

class VMInterfaceTable(BaseInterfaceTable):
    virtual_machine = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True
    )
    vrf = tables.Column(
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='virtualization:vminterface_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VMInterface
        fields = (
            'pk', 'id', 'name', 'virtual_machine', 'enabled', 'mac_address', 'mtu', 'mode', 'description', 'tags',
            'vrf', 'ip_addresses', 'fhrp_groups', 'untagged_vlan', 'tagged_vlans', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'virtual_machine', 'enabled', 'description')


class VirtualMachineVMInterfaceTable(VMInterfaceTable):
    parent = tables.Column(
        linkify=True
    )
    bridge = tables.Column(
        linkify=True
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=VMINTERFACE_BUTTONS
    )

    class Meta(NetBoxTable.Meta):
        model = VMInterface
        fields = (
            'pk', 'id', 'name', 'enabled', 'parent', 'bridge', 'mac_address', 'mtu', 'mode', 'description', 'tags',
            'ip_addresses', 'fhrp_groups', 'untagged_vlan', 'tagged_vlans', 'actions',
        )
        default_columns = ('pk', 'name', 'enabled', 'mac_address', 'mtu', 'mode', 'description', 'ip_addresses')
        row_attrs = {
            'data-name': lambda record: record.name,
        }
