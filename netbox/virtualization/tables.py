import django_tables2 as tables
from django.conf import settings
from dcim.tables.devices import BaseInterfaceTable
from tenancy.tables import TenantColumn
from utilities.tables import (
    BaseTable, ButtonsColumn, ChoiceFieldColumn, ColoredLabelColumn, LinkedCountColumn, TagColumn, ToggleColumn,
)
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface

__all__ = (
    'ClusterTable',
    'ClusterGroupTable',
    'ClusterTypeTable',
    'VirtualMachineDetailTable',
    'VirtualMachineTable',
    'VirtualMachineVMInterfaceTable',
    'VMInterfaceTable',
)

VMINTERFACE_BUTTONS = """
{% if perms.ipam.add_ipaddress %}
    <a href="{% url 'ipam:ipaddress_add' %}?vminterface={{ record.pk }}&return_url={{ virtualmachine.get_absolute_url }}" class="btn btn-sm btn-success" title="Add IP Address">
        <i class="mdi mdi-plus-thick" aria-hidden="true"></i>
    </a>
{% endif %}
"""


#
# Cluster types
#

class ClusterTypeTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    cluster_count = tables.Column(
        verbose_name='Clusters'
    )
    actions = ButtonsColumn(ClusterType)

    class Meta(BaseTable.Meta):
        model = ClusterType
        fields = ('pk', 'name', 'slug', 'cluster_count', 'description', 'actions')
        default_columns = ('pk', 'name', 'cluster_count', 'description', 'actions')


#
# Cluster groups
#

class ClusterGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    cluster_count = tables.Column(
        verbose_name='Clusters'
    )
    actions = ButtonsColumn(ClusterGroup)

    class Meta(BaseTable.Meta):
        model = ClusterGroup
        fields = ('pk', 'name', 'slug', 'cluster_count', 'description', 'actions')
        default_columns = ('pk', 'name', 'cluster_count', 'description', 'actions')


#
# Clusters
#

class ClusterTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    tenant = tables.Column(
        linkify=True
    )
    site = tables.Column(
        linkify=True
    )
    device_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'cluster_id': 'pk'},
        verbose_name='Devices'
    )
    vm_count = LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'cluster_id': 'pk'},
        verbose_name='VMs'
    )
    tags = TagColumn(
        url_name='virtualization:cluster_list'
    )

    class Meta(BaseTable.Meta):
        model = Cluster
        fields = ('pk', 'name', 'type', 'group', 'tenant', 'site', 'device_count', 'vm_count', 'tags')
        default_columns = ('pk', 'name', 'type', 'group', 'tenant', 'site', 'device_count', 'vm_count')


#
# Virtual machines
#

class VirtualMachineTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    status = ChoiceFieldColumn()
    cluster = tables.Column(
        linkify=True
    )
    role = ColoredLabelColumn()
    tenant = TenantColumn()

    class Meta(BaseTable.Meta):
        model = VirtualMachine
        fields = ('pk', 'name', 'status', 'cluster', 'role', 'tenant', 'vcpus', 'memory', 'disk')


class VirtualMachineDetailTable(VirtualMachineTable):
    primary_ip4 = tables.Column(
        linkify=True,
        verbose_name='IPv4 Address'
    )
    primary_ip6 = tables.Column(
        linkify=True,
        verbose_name='IPv6 Address'
    )
    if settings.PREFER_IPV4:
        primary_ip = tables.Column(
            linkify=True,
            order_by=('primary_ip4', 'primary_ip6'),
            verbose_name='IP Address'
        )
    else:
        primary_ip = tables.Column(
            linkify=True,
            order_by=('primary_ip6', 'primary_ip4'),
            verbose_name='IP Address'
        )
    tags = TagColumn(
        url_name='virtualization:virtualmachine_list'
    )

    class Meta(BaseTable.Meta):
        model = VirtualMachine
        fields = (
            'pk', 'name', 'status', 'cluster', 'role', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'primary_ip4',
            'primary_ip6', 'primary_ip', 'tags',
        )
        default_columns = (
            'pk', 'name', 'status', 'cluster', 'role', 'tenant', 'vcpus', 'memory', 'disk', 'primary_ip',
        )


#
# VM components
#

class VMInterfaceTable(BaseInterfaceTable):
    pk = ToggleColumn()
    virtual_machine = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True
    )
    parent = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='virtualization:vminterface_list'
    )

    class Meta(BaseTable.Meta):
        model = VMInterface
        fields = (
            'pk', 'virtual_machine', 'name', 'enabled', 'parent', 'mac_address', 'mtu', 'mode', 'description', 'tags',
            'ip_addresses', 'untagged_vlan', 'tagged_vlans',
        )
        default_columns = ('pk', 'virtual_machine', 'name', 'enabled', 'parent', 'description')


class VirtualMachineVMInterfaceTable(VMInterfaceTable):
    actions = ButtonsColumn(
        model=VMInterface,
        buttons=('edit', 'delete'),
        prepend_template=VMINTERFACE_BUTTONS
    )

    class Meta(BaseTable.Meta):
        model = VMInterface
        fields = (
            'pk', 'name', 'enabled', 'mac_address', 'mtu', 'mode', 'description', 'tags', 'ip_addresses',
            'untagged_vlan', 'tagged_vlans', 'actions',
        )
        default_columns = (
            'pk', 'name', 'enabled', 'mac_address', 'mtu', 'mode', 'description', 'ip_addresses', 'actions',
        )
        row_attrs = {
            'data-name': lambda record: record.name,
        }
