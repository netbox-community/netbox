import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from ipam.models import *
from netbox.tables import NetBoxTable, PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin

__all__ = (
    'ServicePortMappingTable',
    'ServiceTable',
    'ServiceTemplatePortMappingTable',
    'ServiceTemplateTable',
)


class ServiceTemplateTable(PrimaryModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    ports = tables.Column(
        verbose_name=_('Ports'),
        accessor=tables.A('port_list'),
        orderable=False,
    )
    tags = columns.TagColumn(
        url_name='ipam:servicetemplate_list'
    )

    class Meta(PrimaryModelTable.Meta):
        model = ServiceTemplate
        fields = (
            'pk', 'id', 'name', 'ports', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'ports', 'description')


class ServiceTable(ContactsColumnMixin, PrimaryModelTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    parent = tables.Column(
        verbose_name=_('Parent'),
        linkify=True,
        order_by=('device', 'virtual_machine')
    )
    ports = tables.Column(
        verbose_name=_('Ports'),
        accessor=tables.A('port_list'),
        orderable=False,
    )
    tags = columns.TagColumn(
        url_name='ipam:service_list'
    )

    class Meta(PrimaryModelTable.Meta):
        model = Service
        fields = (
            'pk', 'id', 'name', 'parent', 'ports', 'ipaddresses', 'description', 'contacts', 'comments',
            'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'parent', 'ports', 'description')


class ServiceTemplatePortMappingTable(NetBoxTable):
    service_template = tables.Column(
        verbose_name=_('Service Template'),
        linkify=True
    )
    protocol = columns.ChoiceFieldColumn(
        verbose_name=_('Protocol'),
    )
    ports = tables.Column(
        verbose_name=_('Ports'),
        accessor=tables.A('port_list'),
        orderable=False,
    )

    class Meta(NetBoxTable.Meta):
        model = ServiceTemplatePortMapping
        fields = ('pk', 'id', 'service_template', 'protocol', 'ports', 'created', 'last_updated')
        default_columns = ('protocol', 'ports')


class ServicePortMappingTable(NetBoxTable):
    service = tables.Column(
        verbose_name=_('Service'),
        linkify=True
    )
    protocol = columns.ChoiceFieldColumn(
        verbose_name=_('Protocol'),
    )
    ports = tables.Column(
        verbose_name=_('Ports'),
        accessor=tables.A('port_list'),
        orderable=False,
    )

    class Meta(NetBoxTable.Meta):
        model = ServicePortMapping
        fields = ('pk', 'id', 'service', 'protocol', 'ports', 'created', 'last_updated')
        default_columns = ('protocol', 'ports')
