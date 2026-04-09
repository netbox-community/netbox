from dcim.models import ConsolePort, Interface, PowerPort
from dcim.tables import *
from utilities.testing import TableTestCases

#
# Sites
#


class RegionTableTest(TableTestCases.StandardTableTestCase):
    table = RegionTable


class SiteGroupTableTest(TableTestCases.StandardTableTestCase):
    table = SiteGroupTable


class SiteTableTest(TableTestCases.StandardTableTestCase):
    table = SiteTable


class LocationTableTest(TableTestCases.StandardTableTestCase):
    table = LocationTable


#
# Racks
#

class RackRoleTableTest(TableTestCases.StandardTableTestCase):
    table = RackRoleTable


class RackTypeTableTest(TableTestCases.StandardTableTestCase):
    table = RackTypeTable


class RackTableTest(TableTestCases.StandardTableTestCase):
    table = RackTable


class RackReservationTableTest(TableTestCases.StandardTableTestCase):
    table = RackReservationTable


#
# Device types
#

class ManufacturerTableTest(TableTestCases.StandardTableTestCase):
    table = ManufacturerTable


class DeviceTypeTableTest(TableTestCases.StandardTableTestCase):
    table = DeviceTypeTable


#
# Module types
#

class ModuleTypeProfileTableTest(TableTestCases.StandardTableTestCase):
    table = ModuleTypeProfileTable


class ModuleTypeTableTest(TableTestCases.StandardTableTestCase):
    table = ModuleTypeTable


class ModuleTableTest(TableTestCases.StandardTableTestCase):
    table = ModuleTable


#
# Devices
#

class DeviceRoleTableTest(TableTestCases.StandardTableTestCase):
    table = DeviceRoleTable


class PlatformTableTest(TableTestCases.StandardTableTestCase):
    table = PlatformTable


class DeviceTableTest(TableTestCases.StandardTableTestCase):
    table = DeviceTable


#
# Device components
#

class ConsolePortTableTest(TableTestCases.StandardTableTestCase):
    table = ConsolePortTable


class ConsoleServerPortTableTest(TableTestCases.StandardTableTestCase):
    table = ConsoleServerPortTable


class PowerPortTableTest(TableTestCases.StandardTableTestCase):
    table = PowerPortTable


class PowerOutletTableTest(TableTestCases.StandardTableTestCase):
    table = PowerOutletTable


class InterfaceTableTest(TableTestCases.StandardTableTestCase):
    table = InterfaceTable


class FrontPortTableTest(TableTestCases.StandardTableTestCase):
    table = FrontPortTable


class RearPortTableTest(TableTestCases.StandardTableTestCase):
    table = RearPortTable


class ModuleBayTableTest(TableTestCases.StandardTableTestCase):
    table = ModuleBayTable


class DeviceBayTableTest(TableTestCases.StandardTableTestCase):
    table = DeviceBayTable


class InventoryItemTableTest(TableTestCases.StandardTableTestCase):
    table = InventoryItemTable


class InventoryItemRoleTableTest(TableTestCases.StandardTableTestCase):
    table = InventoryItemRoleTable


#
# Connections
#

class ConsoleConnectionTableTest(TableTestCases.StandardTableTestCase):
    table = ConsoleConnectionTable
    queryset_sources = [
        ('ConsoleConnectionsListView', ConsolePort.objects.filter(_path__is_complete=True)),
    ]


class PowerConnectionTableTest(TableTestCases.StandardTableTestCase):
    table = PowerConnectionTable
    queryset_sources = [
        ('PowerConnectionsListView', PowerPort.objects.filter(_path__is_complete=True)),
    ]


class InterfaceConnectionTableTest(TableTestCases.StandardTableTestCase):
    table = InterfaceConnectionTable
    queryset_sources = [
        ('InterfaceConnectionsListView', Interface.objects.filter(_path__is_complete=True)),
    ]


#
# Cables
#

class CableTableTest(TableTestCases.StandardTableTestCase):
    table = CableTable


#
# Power
#

class PowerPanelTableTest(TableTestCases.StandardTableTestCase):
    table = PowerPanelTable


class PowerFeedTableTest(TableTestCases.StandardTableTestCase):
    table = PowerFeedTable


#
# Virtual chassis
#

class VirtualChassisTableTest(TableTestCases.StandardTableTestCase):
    table = VirtualChassisTable


#
# Virtual device contexts
#

class VirtualDeviceContextTableTest(TableTestCases.StandardTableTestCase):
    table = VirtualDeviceContextTable


#
# MAC addresses
#

class MACAddressTableTest(TableTestCases.StandardTableTestCase):
    table = MACAddressTable
