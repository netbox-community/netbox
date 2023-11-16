from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from dcim.models import PowerFeed, PowerPanel
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from netbox.tables import NetBoxTable, columns

from .devices import CableTerminationTable

__all__ = (
    'PowerFeedTable',
    'PowerPanelTable',
)


#
# Power panels
#

class PowerPanelTable(ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    site = tables.Column(
        verbose_name=_('Site'),
        linkify=True
    )
    location = tables.Column(
        verbose_name=_('Location'),
        linkify=True
    )
    powerfeed_count = columns.LinkedCountColumn(
        viewname='dcim:powerfeed_list',
        url_params={'power_panel_id': 'pk'},
        verbose_name=_('Power Feeds')
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='dcim:powerpanel_list'
    )

    class Meta(NetBoxTable.Meta):
        model = PowerPanel
        fields = (
            'pk', 'id', 'name', 'site', 'location', 'powerfeed_count', 'contacts', 'description', 'comments', 'tags',
            'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'site', 'location', 'powerfeed_count')


#
# Power feeds
#

# We're not using PathEndpointTable for PowerFeed because power connections
# cannot traverse pass-through ports.
class PowerFeedTable(TenancyColumnsMixin, CableTerminationTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    power_panel = tables.Column(
        verbose_name=_('Power Panel'),
        linkify=True
    )
    rack = tables.Column(
        verbose_name=_('Rack'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    type = columns.ChoiceFieldColumn(
        verbose_name=_('Type'),
    )
    max_utilization = tables.TemplateColumn(
        verbose_name=_('Max Utilization'),
        template_code="{{ value }}%"
    )
    available_power = tables.Column(
        verbose_name=_('Available Power (VA)')
    )
    tenant = tables.Column(
        linkify=True,
        verbose_name=_('Tenant')
    )
    site = tables.Column(
        accessor='rack__site',
        linkify=True,
        verbose_name=_('Site'),
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    tags = columns.TagColumn(
        url_name='dcim:powerfeed_list'
    )

    class Meta(NetBoxTable.Meta):
        model = PowerFeed
        fields = (
            'pk', 'id', 'name', 'power_panel', 'site', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage',
            'phase', 'max_utilization', 'mark_connected', 'cable', 'cable_color', 'link_peer', 'available_power',
            'tenant', 'tenant_group', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'power_panel', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage', 'phase', 'cable',
            'link_peer',
        )
