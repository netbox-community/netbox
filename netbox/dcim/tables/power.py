import django_tables2 as tables

from dcim.models import PowerFeed, PowerPanel
from utilities.tables import BaseTable, ChoiceFieldColumn, LinkedCountColumn, MarkdownColumn, TagColumn, ToggleColumn
from .devices import CableTerminationTable

__all__ = (
    'PowerFeedTable',
    'PowerPanelTable',
)


#
# Power panels
#

class PowerPanelTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    site = tables.Column(
        linkify=True
    )
    powerfeed_count = LinkedCountColumn(
        viewname='dcim:powerfeed_list',
        url_params={'power_panel_id': 'pk'},
        verbose_name='Feeds'
    )
    tags = TagColumn(
        url_name='dcim:powerpanel_list'
    )

    class Meta(BaseTable.Meta):
        model = PowerPanel
        fields = ('pk', 'id', 'name', 'site', 'location', 'powerfeed_count', 'tags')
        default_columns = ('pk', 'name', 'site', 'location', 'powerfeed_count')


#
# Power feeds
#

# We're not using PathEndpointTable for PowerFeed because power connections
# cannot traverse pass-through ports.
class PowerFeedTable(CableTerminationTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    power_panel = tables.Column(
        linkify=True
    )
    rack = tables.Column(
        linkify=True
    )
    status = ChoiceFieldColumn()
    type = ChoiceFieldColumn()
    max_utilization = tables.TemplateColumn(
        template_code="{{ value }}%"
    )
    available_power = tables.Column(
        verbose_name='Available power (VA)'
    )
    comments = MarkdownColumn()
    tags = TagColumn(
        url_name='dcim:powerfeed_list'
    )

    class Meta(BaseTable.Meta):
        model = PowerFeed
        fields = (
            'pk', 'id', 'name', 'power_panel', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage', 'phase',
            'max_utilization', 'mark_connected', 'cable', 'cable_color', 'link_peer', 'connection', 'available_power',
            'comments', 'tags',
        )
        default_columns = (
            'pk', 'name', 'power_panel', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage', 'phase', 'cable',
            'link_peer',
        )
