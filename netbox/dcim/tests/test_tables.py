from dcim.choices import CableEndChoices, CableProfileChoices, InterfaceTypeChoices
from dcim.models import (
    Cable,
    ConsolePort,
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    Manufacturer,
    PowerPort,
    Site,
)
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


class ModuleBayTypeTableTestCase(TableTestCases.StandardTableTestCase):
    table = ModuleBayTypeTable


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

    def test_termination_columns_follow_connector_order(self):
        """Termination & parent columns must render in connector order, not an arbitrary one."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(model='Device Type 1', manufacturer=manufacturer)
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        switch = Device.objects.create(name='switch1', site=site, device_type=device_type, role=role)
        uplink = Interface.objects.create(
            device=switch, name='et-0/0/0', type=InterfaceTypeChoices.TYPE_100GE_QSFP28
        )
        # Create the servers in ascending order, then cable them in descending order, so that
        # connector order and primary key order disagree.
        servers = [
            Device.objects.create(name=f'server{i}', site=site, device_type=device_type, role=role)
            for i in range(1, 5)
        ]
        interfaces = [
            Interface.objects.create(device=device, name='eth0', type=InterfaceTypeChoices.TYPE_25GE_SFP28)
            for device in servers
        ]
        cable = Cable(
            a_terminations=[uplink],
            b_terminations=list(reversed(interfaces)),
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
        )
        cable.save()

        table = CableTable(Cable.objects.filter(pk=cable.pk))
        table.columns.show('device_b')
        row = list(table.rows)[0]

        self.assertEqual(row.get_cell_value('device_b'), 'server4,server3,server2,server1')
        self.assertEqual(
            [ct.termination for ct in cable.terminations.filter(cable_end=CableEndChoices.SIDE_B)],
            list(reversed(interfaces))
        )


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
# Cooling
#

class CoolingSourceTableTestCase(TableTestCases.StandardTableTestCase):
    table = CoolingSourceTable


class CoolingFeedTableTestCase(TableTestCases.StandardTableTestCase):
    table = CoolingFeedTable


class CoolingIntakeTableTestCase(TableTestCases.StandardTableTestCase):
    table = CoolingIntakeTable


class CoolingOutflowTableTestCase(TableTestCases.StandardTableTestCase):
    table = CoolingOutflowTable


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
