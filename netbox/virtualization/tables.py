import django_tables2 as tables

from dcim.tables.devices import BaseInterfaceTable
from netbox.tables import BaseTable, columns
from tenancy.tables import TenantColumn
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface

__all__ = (
    'ClusterTable',
    'ClusterGroupTable',
    'ClusterTypeTable',
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
# Cluster types
#

class ClusterTypeTable(BaseTable):
    pk = columns.ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    cluster_count = tables.Column(
        verbose_name='Clusters'
    )
    tags = columns.TagColumn(
        url_name='virtualization:clustertype_list'
    )

    class Meta(BaseTable.Meta):
        model = ClusterType
        fields = (
            'pk', 'id', 'name', 'slug', 'cluster_count', 'description', 'created', 'last_updated', 'tags', 'actions',
        )
        default_columns = ('pk', 'name', 'cluster_count', 'description')


#
# Cluster groups
#

class ClusterGroupTable(BaseTable):
    pk = columns.ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    cluster_count = tables.Column(
        verbose_name='Clusters'
    )
    tags = columns.TagColumn(
        url_name='virtualization:clustergroup_list'
    )

    class Meta(BaseTable.Meta):
        model = ClusterGroup
        fields = (
            'pk', 'id', 'name', 'slug', 'cluster_count', 'description', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'cluster_count', 'description')


#
# Clusters
#

class ClusterTable(BaseTable):
    pk = columns.ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    type = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    tenant = tables.Column(
        linkify=True
    )
    site = tables.Column(
        linkify=True
    )
    device_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'cluster_id': 'pk'},
        verbose_name='Devices'
    )
    vm_count = columns.LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'cluster_id': 'pk'},
        verbose_name='VMs'
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='virtualization:cluster_list'
    )

    class Meta(BaseTable.Meta):
        model = Cluster
        fields = (
            'pk', 'id', 'name', 'type', 'group', 'tenant', 'site', 'comments', 'device_count', 'vm_count', 'tags',
            'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'type', 'group', 'tenant', 'site', 'device_count', 'vm_count')


#
# Virtual machines
#

class VirtualMachineTable(BaseTable):
    pk = columns.ToggleColumn()
    name = tables.Column(
        order_by=('_name',),
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    cluster = tables.Column(
        linkify=True
    )
    role = columns.ColoredLabelColumn()
    tenant = TenantColumn()
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
    tags = columns.TagColumn(
        url_name='virtualization:virtualmachine_list'
    )

    class Meta(BaseTable.Meta):
        model = VirtualMachine
        fields = (
            'pk', 'id', 'name', 'status', 'cluster', 'role', 'tenant', 'platform', 'vcpus', 'memory', 'disk',
            'primary_ip4', 'primary_ip6', 'primary_ip', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'status', 'cluster', 'role', 'tenant', 'vcpus', 'memory', 'disk', 'primary_ip',
        )


#
# VM components
#

class VMInterfaceTable(BaseInterfaceTable):
    pk = columns.ToggleColumn()
    virtual_machine = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='virtualization:vminterface_list'
    )

    class Meta(BaseTable.Meta):
        model = VMInterface
        fields = (
            'pk', 'id', 'name', 'virtual_machine', 'enabled', 'mac_address', 'mtu', 'mode', 'description', 'tags',
            'ip_addresses', 'fhrp_groups', 'untagged_vlan', 'tagged_vlans', 'created', 'last_updated',
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
        sequence=('edit', 'delete'),
        extra_buttons=VMINTERFACE_BUTTONS
    )

    class Meta(BaseTable.Meta):
        model = VMInterface
        fields = (
            'pk', 'id', 'name', 'enabled', 'parent', 'bridge', 'mac_address', 'mtu', 'mode', 'description', 'tags',
            'ip_addresses', 'fhrp_groups', 'untagged_vlan', 'tagged_vlans', 'actions',
        )
        default_columns = ('pk', 'name', 'enabled', 'mac_address', 'mtu', 'mode', 'description', 'ip_addresses')
        row_attrs = {
            'data-name': lambda record: record.name,
        }
