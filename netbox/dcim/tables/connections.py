from django.utils.translation import gettext_lazy as _
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
        verbose_name=_('Device'),
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name=_('Console Port')
    )
    reachable = columns.BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name=_('Reachable')
    )

    class Meta(BaseTable.Meta):
        model = ConsolePort
        fields = ('device', 'name', 'connection', 'reachable')


class PowerConnectionTable(PathEndpointTable):
    device = tables.Column(
        verbose_name=_('Device'),
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name=_('Power Port')
    )
    reachable = columns.BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name=_('Reachable')
    )

    class Meta(BaseTable.Meta):
        model = PowerPort
        fields = ('device', 'name', 'connection', 'reachable')


class InterfaceConnectionTable(PathEndpointTable):
    device = tables.Column(
        verbose_name=_('Device'),
        accessor=Accessor('device'),
        linkify=True
    )
    interface = tables.Column(
        verbose_name=_('Interface'),
        accessor=Accessor('name'),
        linkify=True
    )
    reachable = columns.BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name=_('Reachable')
    )

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('device', 'interface', 'connection', 'reachable')
