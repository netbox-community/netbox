import django_tables2 as tables

from ipam.models import *
from ipam.models.l2vpn import L2VPN, L2VPNTermination
from netbox.tables import NetBoxTable, columns

__all__ = (
    'L2VPNTable',
    'L2VPNTerminationTable',
)


class L2VPNTable(NetBoxTable):
    pk = columns.ToggleColumn()
    name = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = L2VPN
        fields = ('pk', 'name', 'description', 'slug', 'type', 'tenant', 'actions')
        default_columns = ('pk', 'name', 'description', 'actions')


class L2VPNTerminationTable(NetBoxTable):
    pk = columns.ToggleColumn()
    assigned_object_type = columns.ContentTypeColumn(
        verbose_name='Object Type'
    )
    assigned_object = tables.Column(
        linkify=True,
        orderable=False
    )

    class Meta(NetBoxTable.Meta):
        model = L2VPNTermination
        fields = ('pk', 'l2vpn', 'assigned_object_type', 'assigned_object', 'actions')
        default_columns = ('pk', 'l2vpn', 'assigned_object_type', 'assigned_object', 'actions')
