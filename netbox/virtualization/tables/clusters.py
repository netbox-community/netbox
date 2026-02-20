import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import OrganizationalModelTable, PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin
from virtualization.models import Cluster, ClusterGroup, ClusterType

__all__ = (
    'ClusterGroupTable',
    'ClusterTable',
    'ClusterTypeTable',
)


class ClusterTypeTable(OrganizationalModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    cluster_count = columns.LinkedCountColumn(
        viewname='virtualization:cluster_list',
        url_params={'type_id': 'pk'},
        verbose_name=_('Clusters')
    )
    tags = columns.TagColumn(
        url_name='virtualization:clustertype_list'
    )

    class Meta(OrganizationalModelTable.Meta):
        model = ClusterType
        fields = (
            'pk', 'id', 'name', 'slug', 'cluster_count', 'description', 'comments', 'created', 'last_updated', 'tags',
            'actions',
        )
        default_columns = ('pk', 'name', 'cluster_count', 'description')


class ClusterGroupTable(ContactsColumnMixin, OrganizationalModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    cluster_count = columns.LinkedCountColumn(
        viewname='virtualization:cluster_list',
        url_params={'group_id': 'pk'},
        verbose_name=_('Clusters')
    )
    tags = columns.TagColumn(
        url_name='virtualization:clustergroup_list'
    )

    class Meta(OrganizationalModelTable.Meta):
        model = ClusterGroup
        fields = (
            'pk', 'id', 'name', 'slug', 'cluster_count', 'description', 'comments', 'contacts', 'tags', 'created',
            'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'cluster_count', 'description')


class ClusterTable(TenancyColumnsMixin, ContactsColumnMixin, PrimaryModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    type = tables.Column(
        verbose_name=_('Type'),
        linkify=True
    )
    group = tables.Column(
        verbose_name=_('Group'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    scope_type = columns.ContentTypeColumn(
        verbose_name=_('Scope Type'),
    )
    scope = tables.Column(
        verbose_name=_('Scope'),
        linkify=True,
        orderable=False
    )
    device_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'cluster_id': 'pk'},
        verbose_name=_('Devices')
    )
    vm_count = columns.LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'cluster_id': 'pk'},
        verbose_name=_('VMs')
    )
    tags = columns.TagColumn(
        url_name='virtualization:cluster_list'
    )

    class Meta(PrimaryModelTable.Meta):
        model = Cluster
        fields = (
            'pk', 'id', 'name', 'type', 'group', 'status', 'tenant', 'tenant_group', 'scope', 'scope_type',
            'description', 'comments', 'device_count', 'vm_count', 'contacts', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'type', 'group', 'status', 'tenant', 'site', 'device_count', 'vm_count')
