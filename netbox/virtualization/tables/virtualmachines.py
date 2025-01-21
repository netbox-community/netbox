import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from dcim.tables.devices import BaseInterfaceTable
from netbox.tables import NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin
from utilities.templatetags.helpers import humanize_megabytes
from virtualization.models import VirtualDisk, VirtualMachine, VMInterface
from .template_code import *

__all__ = (
    'VirtualDiskTable',
    'VirtualMachineTable',
    'VirtualMachineVirtualDiskTable',
    'VirtualMachineVMInterfaceTable',
    'VMInterfaceTable',
)


#
# Virtual machines
#

class VirtualMachineTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    site = tables.Column(
        verbose_name=_('Site'),
        linkify=True
    )
    cluster = tables.Column(
        verbose_name=_('Cluster'),
        linkify=True
    )
    device = tables.Column(
        verbose_name=_('Device'),
        linkify=True
    )
    role = columns.ColoredLabelColumn(
        verbose_name=_('Role'),
    )
    platform = tables.Column(
        linkify=True,
        verbose_name=_('Platform')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    primary_ip4 = tables.Column(
        linkify=True,
        verbose_name=_('IPv4 Address')
    )
    primary_ip6 = tables.Column(
        linkify=True,
        verbose_name=_('IPv6 Address')
    )
    primary_ip = tables.Column(
        linkify=True,
        order_by=('primary_ip4', 'primary_ip6'),
        verbose_name=_('IP Address')
    )
    tags = columns.TagColumn(
        url_name='virtualization:virtualmachine_list'
    )
    interface_count = tables.Column(
        verbose_name=_('Interfaces')
    )
    virtual_disk_count = tables.Column(
        verbose_name=_('Virtual Disks')
    )
    config_template = tables.Column(
        verbose_name=_('Config Template'),
        linkify=True
    )
    disk = tables.Column(
        verbose_name=_('Disk'),
    )

    class Meta(NetBoxTable.Meta):
        model = VirtualMachine
        fields = (
            'pk', 'id', 'name', 'status', 'site', 'cluster', 'device', 'role', 'tenant', 'tenant_group', 'vcpus',
            'memory', 'disk', 'primary_ip4', 'primary_ip6', 'primary_ip', 'description', 'comments', 'config_template',
            'serial', 'contacts', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'status', 'site', 'cluster', 'role', 'tenant', 'vcpus', 'memory', 'disk', 'primary_ip',
        )

    def render_disk(self, value):
        return humanize_megabytes(value)


#
# VM components
#

class VMInterfaceTable(BaseInterfaceTable):
    virtual_machine = tables.Column(
        verbose_name=_('Virtual Machine'),
        linkify=True
    )
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    vrf = tables.Column(
        verbose_name=_('VRF'),
        linkify=True
    )
    mac_address = tables.Column(
        verbose_name=_('MAC Address'),
        orderable=False,
    )
    tags = columns.TagColumn(
        url_name='virtualization:vminterface_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VMInterface
        fields = (
            'pk', 'id', 'name', 'virtual_machine', 'enabled', 'mtu', 'mode', 'description', 'tags', 'vrf',
            'mac_address', 'primary_mac_address', 'l2vpn', 'tunnel', 'ip_addresses', 'fhrp_groups', 'untagged_vlan',
            'tagged_vlans', 'qinq_svlan', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'virtual_machine', 'enabled', 'description')


class VirtualMachineVMInterfaceTable(VMInterfaceTable):
    parent = tables.Column(
        verbose_name=_('Parent'),
        linkify=True
    )
    bridge = tables.Column(
        verbose_name=_('Bridge'),
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
            'vrf', 'l2vpn', 'tunnel', 'ip_addresses', 'fhrp_groups', 'untagged_vlan', 'tagged_vlans', 'qinq_svlan',
            'actions',
        )
        default_columns = ('pk', 'name', 'enabled', 'mac_address', 'mtu', 'mode', 'description', 'ip_addresses')
        row_attrs = {
            'data-name': lambda record: record.name,
            'data-virtual': lambda record: "true",
            'data-enabled': lambda record: "true" if record.enabled else "false",
        }


class VirtualDiskTable(NetBoxTable):
    virtual_machine = tables.Column(
        verbose_name=_('Virtual Machine'),
        linkify=True
    )
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    size = tables.Column(
        verbose_name=_('Size')
    )
    tags = columns.TagColumn(
        url_name='virtualization:virtualdisk_list'
    )

    class Meta(NetBoxTable.Meta):
        model = VirtualDisk
        fields = (
            'pk', 'id', 'virtual_machine', 'name', 'size', 'description', 'tags',
        )
        default_columns = ('pk', 'name', 'virtual_machine', 'size', 'description')
        row_attrs = {
            'data-name': lambda record: record.name,
        }

    def render_size(self, value):
        return humanize_megabytes(value)


class VirtualMachineVirtualDiskTable(VirtualDiskTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(VirtualDiskTable.Meta):
        fields = (
            'pk', 'id', 'name', 'size', 'description', 'tags', 'actions',
        )
        default_columns = ('pk', 'name', 'size', 'description')
