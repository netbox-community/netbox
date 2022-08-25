import django_tables2 as tables
from django_tables2.utils import Accessor

from netbox.tables import BaseTable, columns
from dcim.models import ConsolePort, Interface, PowerPort
from .devices import PathEndpointTable

__all__ = (
    'ConsoleConnectionTable',
    'InterfaceConnectionTable',
    'PowerConnectionTable',
)


#
# Device connections
#

class ConsoleConnectionTable(PathEndpointTable):
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name='Console Port'
    )
    reachable = columns.BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name='Reachable'
    )

    class Meta(BaseTable.Meta):
        model = ConsolePort
        fields = ('device', 'name', 'connection', 'reachable')


class PowerConnectionTable(PathEndpointTable):
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name='Power Port'
    )
    reachable = columns.BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name='Reachable'
    )

    class Meta(BaseTable.Meta):
        model = PowerPort
        fields = ('device', 'name', 'connection', 'reachable')


class InterfaceConnectionTable(PathEndpointTable):
    device = tables.Column(
        accessor=Accessor('device'),
        linkify=True
    )
    interface = tables.Column(
        accessor=Accessor('name'),
        linkify=True
    )
    reachable = columns.BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name='Reachable'
    )

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('device', 'interface', 'connection', 'reachable')
