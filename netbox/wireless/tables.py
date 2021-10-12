import django_tables2 as tables

from .models import SSID
from utilities.tables import BaseTable, TagColumn, ToggleColumn

__all__ = (
    'SSIDTable',
)


class SSIDTable(BaseTable):
    pk = ToggleColumn()
    id = tables.Column(
        linkify=True,
        verbose_name='ID'
    )
    tags = TagColumn(
        url_name='dcim:cable_list'
    )

    class Meta(BaseTable.Meta):
        model = SSID
        fields = ('pk', 'id', 'name', 'description', 'vlan')
        default_columns = ('pk', 'name', 'description', 'vlan')
