import django_tables2 as tables

from dcim.tables import BaseInterfaceTable
from tenancy.tables import COL_TENANT
from utilities.tables import (
    BaseTable, ButtonsColumn, ChoiceFieldColumn, ColoredLabelColumn, LinkedCountColumn, TagColumn, ToggleColumn,
)
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface

VIRTUALMACHINE_PRIMARY_IP = """
{{ record.primary_ip6.address.ip|default:"" }}
{% if record.primary_ip6 and record.primary_ip4 %}<br />{% endif %}
{{ record.primary_ip4.address.ip|default:"" }}
"""


#
# Cluster types
#

class ClusterTypeTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    cluster_count = tables.Column(
        verbose_name='Clusters'
    )
    actions = ButtonsColumn(ClusterType, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = ClusterType
        fields = ('pk', 'name', 'slug', 'cluster_count', 'description', 'actions')
        default_columns = ('pk', 'name', 'cluster_count', 'description', 'actions')


#
# Cluster groups
#

class ClusterGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    cluster_count = tables.Column(
        verbose_name='Clusters'
    )
    actions = ButtonsColumn(ClusterGroup, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = ClusterGroup
        fields = ('pk', 'name', 'slug', 'cluster_count', 'description', 'actions')
        default_columns = ('pk', 'name', 'cluster_count', 'description', 'actions')


#
# Clusters
#

class ClusterTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
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
    name = tables.LinkColumn()
    status = ChoiceFieldColumn()
    cluster = tables.Column(
        linkify=True
    )
    role = ColoredLabelColumn()
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )

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
    primary_ip = tables.TemplateColumn(
        orderable=False,
        verbose_name='IP Address',
        template_code=VIRTUALMACHINE_PRIMARY_IP
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
    virtual_machine = tables.LinkColumn()
    name = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='virtualization:vminterface_list'
    )

    class Meta(BaseTable.Meta):
        model = VMInterface
        fields = (
            'pk', 'virtual_machine', 'name', 'enabled', 'mac_address', 'mtu', 'description', 'tags', 'ip_addresses',
            'untagged_vlan', 'tagged_vlans',
        )
        default_columns = ('pk', 'virtual_machine', 'name', 'enabled', 'description')
