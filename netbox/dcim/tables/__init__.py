import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, BooleanColumn
from dcim.models import ConsolePort, Interface, PowerPort
from .cables import *
from .devices import *
from .devicetypes import *
from .power import *
from .racks import *
from .sites import *


#
# Device connections
#

class ConsoleConnectionTable(BaseTable):
    console_server = tables.Column(
        accessor=Accessor('_path__destination__device'),
        orderable=False,
        linkify=True,
        verbose_name='Console Server'
    )
    console_server_port = tables.Column(
        accessor=Accessor('_path__destination'),
        orderable=False,
        linkify=True,
        verbose_name='Port'
    )
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name='Console Port'
    )
    reachable = BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name='Reachable'
    )

    class Meta(BaseTable.Meta):
        model = ConsolePort
        fields = ('device', 'name', 'console_server', 'console_server_port', 'reachable')
        exclude = ('id', )


class PowerConnectionTable(BaseTable):
    pdu = tables.Column(
        accessor=Accessor('_path__destination__device'),
        orderable=False,
        linkify=True,
        verbose_name='PDU'
    )
    outlet = tables.Column(
        accessor=Accessor('_path__destination'),
        orderable=False,
        linkify=True,
        verbose_name='Outlet'
    )
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        verbose_name='Power Port'
    )
    reachable = BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name='Reachable'
    )

    class Meta(BaseTable.Meta):
        model = PowerPort
        fields = ('device', 'name', 'pdu', 'outlet', 'reachable')
        exclude = ('id', )


class InterfaceConnectionTable(BaseTable):
    device_a = tables.Column(
        accessor=Accessor('device'),
        linkify=True,
        verbose_name='Device A'
    )
    interface_a = tables.Column(
        accessor=Accessor('name'),
        linkify=True,
        verbose_name='Interface A'
    )
    device_b = tables.Column(
        accessor=Accessor('_path__destination__device'),
        orderable=False,
        linkify=True,
        verbose_name='Device B'
    )
    interface_b = tables.Column(
        accessor=Accessor('_path__destination'),
        orderable=False,
        linkify=True,
        verbose_name='Interface B'
    )
    reachable = BooleanColumn(
        accessor=Accessor('_path__is_active'),
        verbose_name='Reachable'
    )

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('device_a', 'interface_a', 'device_b', 'interface_b', 'reachable')
        exclude = ('id', )
