from dcim.models import ConsolePort, Interface, PowerPort
from dcim.tables import *
from utilities.testing import TableTestCases

#
# Sites
#


class RegionTableTestCase(TableTestCases.StandardTableTestCase):
    table = RegionTable


class SiteGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = SiteGroupTable


class SiteTableTestCase(TableTestCases.StandardTableTestCase):
    table = SiteTable


class LocationTableTestCase(TableTestCases.StandardTableTestCase):
    table = LocationTable


#
# Racks
#

class RackRoleTableTestCase(TableTestCases.StandardTableTestCase):
    table = RackRoleTable


class RackGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = RackGroupTable


class RackTypeTableTestCase(TableTestCases.StandardTableTestCase):
    table = RackTypeTable


class RackTableTestCase(TableTestCases.StandardTableTestCase):
    table = RackTable


class RackReservationTableTestCase(TableTestCases.StandardTableTestCase):
    table = RackReservationTable


#
# Device types
#

class ManufacturerTableTestCase(TableTestCases.StandardTableTestCase):
    table = ManufacturerTable


class DeviceTypeTableTestCase(TableTestCases.StandardTableTestCase):
    table = DeviceTypeTable


#
# Module types
#

class ModuleTypeProfileTableTestCase(TableTestCases.StandardTableTestCase):
    table = ModuleTypeProfileTable


class ModuleTypeTableTestCase(TableTestCases.StandardTableTestCase):
    table = ModuleTypeTable


class ModuleTableTestCase(TableTestCases.StandardTableTestCase):
    table = ModuleTable

    def test_profile_column_available(self):
        self.assertIn('profile', self.table.base_columns)


#
# Devices
#

class DeviceRoleTableTestCase(TableTestCases.StandardTableTestCase):
    table = DeviceRoleTable


class PlatformTableTestCase(TableTestCases.StandardTableTestCase):
    table = PlatformTable


class DeviceTableTestCase(TableTestCases.StandardTableTestCase):
    table = DeviceTable


#
# Device components
#

class ConsolePortTableTestCase(TableTestCases.StandardTableTestCase):
    table = ConsolePortTable


class ConsoleServerPortTableTestCase(TableTestCases.StandardTableTestCase):
    table = ConsoleServerPortTable


class PowerPortTableTestCase(TableTestCases.StandardTableTestCase):
    table = PowerPortTable


class PowerOutletTableTestCase(TableTestCases.StandardTableTestCase):
    table = PowerOutletTable


class InterfaceTableTestCase(TableTestCases.StandardTableTestCase):
    table = InterfaceTable


class FrontPortTableTestCase(TableTestCases.StandardTableTestCase):
    table = FrontPortTable


class RearPortTableTestCase(TableTestCases.StandardTableTestCase):
    table = RearPortTable


class ModuleBayTableTestCase(TableTestCases.StandardTableTestCase):
    table = ModuleBayTable


class DeviceBayTableTestCase(TableTestCases.StandardTableTestCase):
    table = DeviceBayTable


class InventoryItemTableTestCase(TableTestCases.StandardTableTestCase):
    table = InventoryItemTable


class InventoryItemRoleTableTestCase(TableTestCases.StandardTableTestCase):
    table = InventoryItemRoleTable


#
# Connections
#

class ConsoleConnectionTableTestCase(TableTestCases.StandardTableTestCase):
    table = ConsoleConnectionTable
    queryset_sources = [
        ('ConsoleConnectionsListView', ConsolePort.objects.filter(_path__is_complete=True)),
    ]


class PowerConnectionTableTestCase(TableTestCases.StandardTableTestCase):
    table = PowerConnectionTable
    queryset_sources = [
        ('PowerConnectionsListView', PowerPort.objects.filter(_path__is_complete=True)),
    ]


class InterfaceConnectionTableTestCase(TableTestCases.StandardTableTestCase):
    table = InterfaceConnectionTable
    queryset_sources = [
        ('InterfaceConnectionsListView', Interface.objects.filter(_path__is_complete=True)),
    ]


#
# Cables
#

class CableTableTestCase(TableTestCases.StandardTableTestCase):
    table = CableTable


class CableBundleTableTestCase(TableTestCases.StandardTableTestCase):
    table = CableBundleTable


#
# Power
#

class PowerPanelTableTestCase(TableTestCases.StandardTableTestCase):
    table = PowerPanelTable


class PowerFeedTableTestCase(TableTestCases.StandardTableTestCase):
    table = PowerFeedTable


#
# Virtual chassis
#

class VirtualChassisTableTestCase(TableTestCases.StandardTableTestCase):
    table = VirtualChassisTable


#
# Virtual device contexts
#

class VirtualDeviceContextTableTestCase(TableTestCases.StandardTableTestCase):
    table = VirtualDeviceContextTable


#
# MAC addresses
#

class MACAddressTableTestCase(TableTestCases.StandardTableTestCase):
    table = MACAddressTable
