import django_tables2 as tables
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin
from virtualization.models import Cluster, ClusterGroup, ClusterType

from netbox.tables import NetBoxTable, columns

__all__ = (
    'ClusterTable',
    'ClusterGroupTable',
    'ClusterTypeTable',
)


class ClusterTypeTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    cluster_count = columns.LinkedCountColumn(
        viewname='virtualization:cluster_list',
        url_params={'type_id': 'pk'},
        verbose_name='Clusters'
    )
    tags = columns.TagColumn(
        url_name='virtualization:clustertype_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ClusterType
        fields = (
            'pk', 'id', 'name', 'slug', 'cluster_count', 'description', 'created', 'last_updated', 'tags', 'actions',
        )
        default_columns = ('pk', 'name', 'cluster_count', 'description')


class ClusterGroupTable(ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    cluster_count = columns.LinkedCountColumn(
        viewname='virtualization:cluster_list',
        url_params={'group_id': 'pk'},
        verbose_name='Clusters'
    )
    tags = columns.TagColumn(
        url_name='virtualization:clustergroup_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ClusterGroup
        fields = (
            'pk', 'id', 'name', 'slug', 'cluster_count', 'description', 'contacts', 'tags', 'created', 'last_updated',
            'actions',
        )
        default_columns = ('pk', 'name', 'cluster_count', 'description')


class ClusterTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    type = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
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

    class Meta(NetBoxTable.Meta):
        model = Cluster
        fields = (
            'pk', 'id', 'name', 'type', 'group', 'status', 'tenant', 'tenant_group', 'site', 'description', 'comments',
            'device_count', 'vm_count', 'contacts', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'type', 'group', 'status', 'tenant', 'site', 'device_count', 'vm_count')
