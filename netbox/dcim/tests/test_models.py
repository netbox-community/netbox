from django.core.exceptions import ValidationError
from django.test import TestCase

from dcim.choices import *
from dcim.constants import CONNECTION_STATUS_CONNECTED, CONNECTION_STATUS_PLANNED
from dcim.models import *
from tenancy.models import Tenant


class RackTestCase(TestCase):

    def setUp(self):

        self.site1 = Site.objects.create(
            name='TestSite1',
            slug='test-site-1'
        )
        self.site2 = Site.objects.create(
            name='TestSite2',
            slug='test-site-2'
        )
        self.group1 = RackGroup.objects.create(
            name='TestGroup1',
            slug='test-group-1',
            site=self.site1
        )
        self.group2 = RackGroup.objects.create(
            name='TestGroup2',
            slug='test-group-2',
            site=self.site2
        )
        self.rack = Rack.objects.create(
            name='TestRack1',
            facility_id='A101',
            site=self.site1,
            group=self.group1,
            u_height=42
        )
        self.manufacturer = Manufacturer.objects.create(
            name='Acme',
            slug='acme'
        )

        self.device_type = {
            'ff2048': DeviceType.objects.create(
                manufacturer=self.manufacturer,
                model='FrameForwarder 2048',
                slug='ff2048'
            ),
            'cc5000': DeviceType.objects.create(
                manufacturer=self.manufacturer,
                model='CurrentCatapult 5000',
                slug='cc5000',
                u_height=0
            ),
        }
        self.role = {
            'Server': DeviceRole.objects.create(
                name='Server',
                slug='server',
            ),
            'Switch': DeviceRole.objects.create(
                name='Switch',
                slug='switch',
            ),
            'Console Server': DeviceRole.objects.create(
                name='Console Server',
                slug='console-server',
            ),
            'PDU': DeviceRole.objects.create(
                name='PDU',
                slug='pdu',
            ),

        }

    def test_rack_device_outside_height(self):

        rack1 = Rack(
            name='TestRack2',
            facility_id='A102',
            site=self.site1,
            u_height=42
        )
        rack1.save()

        device1 = Device(
            name='TestSwitch1',
            device_type=DeviceType.objects.get(manufacturer__slug='acme', slug='ff2048'),
            device_role=DeviceRole.objects.get(slug='switch'),
            site=self.site1,
            rack=rack1,
            position=43,
            face=DeviceFaceChoices.FACE_FRONT,
        )
        device1.save()

        with self.assertRaises(ValidationError):
            rack1.clean()

    def test_rack_group_site(self):

        rack_invalid_group = Rack(
            name='TestRack2',
            facility_id='A102',
            site=self.site1,
            u_height=42,
            group=self.group2
        )
        rack_invalid_group.save()

        with self.assertRaises(ValidationError):
            rack_invalid_group.clean()

    def test_mount_single_device(self):

        device1 = Device(
            name='TestSwitch1',
            device_type=DeviceType.objects.get(manufacturer__slug='acme', slug='ff2048'),
            device_role=DeviceRole.objects.get(slug='switch'),
            site=self.site1,
            rack=self.rack,
            position=10,
            face=DeviceFaceChoices.FACE_REAR,
        )
        device1.save()

        # Validate rack height
        self.assertEqual(list(self.rack.units), list(reversed(range(1, 43))))

        # Validate inventory (front face)
        rack1_inventory_front = self.rack.get_rack_units(face=DeviceFaceChoices.FACE_FRONT)
        self.assertEqual(rack1_inventory_front[-10]['device'], device1)
        del(rack1_inventory_front[-10])
        for u in rack1_inventory_front:
            self.assertIsNone(u['device'])

        # Validate inventory (rear face)
        rack1_inventory_rear = self.rack.get_rack_units(face=DeviceFaceChoices.FACE_REAR)
        self.assertEqual(rack1_inventory_rear[-10]['device'], device1)
        del(rack1_inventory_rear[-10])
        for u in rack1_inventory_rear:
            self.assertIsNone(u['device'])

    def test_mount_zero_ru(self):
        pdu = Device.objects.create(
            name='TestPDU',
            device_role=self.role.get('PDU'),
            device_type=self.device_type.get('cc5000'),
            site=self.site1,
            rack=self.rack,
            position=None,
            face='',
        )
        self.assertTrue(pdu)


class DeviceTestCase(TestCase):

    def setUp(self):

        self.site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.device_role = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )

        # Create DeviceType components
        ConsolePortTemplate(
            device_type=self.device_type,
            name='Console Port 1'
        ).save()

        ConsoleServerPortTemplate(
            device_type=self.device_type,
            name='Console Server Port 1'
        ).save()

        ppt = PowerPortTemplate(
            device_type=self.device_type,
            name='Power Port 1',
            maximum_draw=1000,
            allocated_draw=500
        )
        ppt.save()

        PowerOutletTemplate(
            device_type=self.device_type,
            name='Power Outlet 1',
            power_port=ppt,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A
        ).save()

        InterfaceTemplate(
            device_type=self.device_type,
            name='Interface 1',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True
        ).save()

        rpt = RearPortTemplate(
            device_type=self.device_type,
            name='Rear Port 1',
            type=PortTypeChoices.TYPE_8P8C,
            positions=8
        )
        rpt.save()

        FrontPortTemplate(
            device_type=self.device_type,
            name='Front Port 1',
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rpt,
            rear_port_position=2
        ).save()

        DeviceBayTemplate(
            device_type=self.device_type,
            name='Device Bay 1'
        ).save()

    def test_device_creation(self):
        """
        Ensure that all Device components are copied automatically from the DeviceType.
        """
        d = Device(
            site=self.site,
            device_type=self.device_type,
            device_role=self.device_role,
            name='Test Device 1'
        )
        d.save()

        ConsolePort.objects.get(
            device=d,
            name='Console Port 1'
        )

        ConsoleServerPort.objects.get(
            device=d,
            name='Console Server Port 1'
        )

        pp = PowerPort.objects.get(
            device=d,
            name='Power Port 1',
            maximum_draw=1000,
            allocated_draw=500
        )

        PowerOutlet.objects.get(
            device=d,
            name='Power Outlet 1',
            power_port=pp,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A
        )

        Interface.objects.get(
            device=d,
            name='Interface 1',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True
        )

        rp = RearPort.objects.get(
            device=d,
            name='Rear Port 1',
            type=PortTypeChoices.TYPE_8P8C,
            positions=8
        )

        FrontPort.objects.get(
            device=d,
            name='Front Port 1',
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rp,
            rear_port_position=2
        )

        DeviceBay.objects.get(
            device=d,
            name='Device Bay 1'
        )

    def test_multiple_unnamed_devices(self):

        device1 = Device(
            site=self.site,
            device_type=self.device_type,
            device_role=self.device_role,
            name=''
        )
        device1.save()

        device2 = Device(
            site=device1.site,
            device_type=device1.device_type,
            device_role=device1.device_role,
            name=''
        )
        device2.full_clean()
        device2.save()

        self.assertEqual(Device.objects.filter(name='').count(), 2)

    def test_device_duplicate_names(self):

        device1 = Device(
            site=self.site,
            device_type=self.device_type,
            device_role=self.device_role,
            name='Test Device 1'
        )
        device1.save()

        device2 = Device(
            site=device1.site,
            device_type=device1.device_type,
            device_role=device1.device_role,
            name=device1.name
        )

        # Two devices assigned to the same Site and no Tenant should fail validation
        with self.assertRaises(ValidationError):
            device2.full_clean()

        tenant = Tenant.objects.create(name='Test Tenant 1', slug='test-tenant-1')
        device1.tenant = tenant
        device1.save()
        device2.tenant = tenant

        # Two devices assigned to the same Site and the same Tenant should fail validation
        with self.assertRaises(ValidationError):
            device2.full_clean()

        device2.tenant = None

        # Two devices assigned to the same Site and different Tenants should pass validation
        device2.full_clean()
        device2.save()


class CableTestCase(TestCase):

    def setUp(self):

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='TestDevice1', site=site
        )
        self.device2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='TestDevice2', site=site
        )
        self.interface1 = Interface.objects.create(device=self.device1, name='eth0')
        self.interface2 = Interface.objects.create(device=self.device2, name='eth0')
        self.cable = Cable(termination_a=self.interface1, termination_b=self.interface2)
        self.cable.save()

        self.power_port1 = PowerPort.objects.create(device=self.device2, name='psu1')
        self.patch_pannel = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='TestPatchPannel', site=site
        )
        self.rear_port = RearPort.objects.create(device=self.patch_pannel, name='R1', type=1000)
        self.front_port = FrontPort.objects.create(
            device=self.patch_pannel, name='F1', type=1000, rear_port=self.rear_port
        )

    def test_cable_creation(self):
        """
        When a new Cable is created, it must be cached on either termination point.
        """
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        self.assertEqual(self.cable.termination_a, interface1)
        interface2 = Interface.objects.get(pk=self.interface2.pk)
        self.assertEqual(self.cable.termination_b, interface2)

    def test_cable_deletion(self):
        """
        When a Cable is deleted, the `cable` field on its termination points must be nullified. The str() method
        should still return the PK of the string even after being nullified.
        """
        self.cable.delete()
        self.assertIsNone(self.cable.pk)
        self.assertNotEqual(str(self.cable), '#None')
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        self.assertIsNone(interface1.cable)
        interface2 = Interface.objects.get(pk=self.interface2.pk)
        self.assertIsNone(interface2.cable)

    def test_cabletermination_deletion(self):
        """
        When a CableTermination object is deleted, its attached Cable (if any) must also be deleted.
        """
        self.interface1.delete()
        cable = Cable.objects.filter(pk=self.cable.pk).first()
        self.assertIsNone(cable)

    def test_cable_validates_compatibale_types(self):
        """
        The clean method should have a check to ensure only compatible port types can be connected by a cable
        """
        # An interface cannot be connected to a power port
        cable = Cable(termination_a=self.interface1, termination_b=self.power_port1)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_have_the_same_terminination_on_both_ends(self):
        """
        A cable cannot be made with the same A and B side terminations
        """
        cable = Cable(termination_a=self.interface1, termination_b=self.interface1)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_front_port_cannot_connect_to_corresponding_rear_port(self):
        """
        A cable cannot connect a front port to its corresponding rear port
        """
        cable = Cable(termination_a=self.front_port, termination_b=self.rear_port)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_an_existing_connection(self):
        """
        Either side of a cable cannot be terminated when that side already has a connection
        """
        # Try to create a cable with the same interface terminations
        cable = Cable(termination_a=self.interface2, termination_b=self.interface1)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_a_virtual_inteface(self):
        """
        A cable cannot terminate to a virtual interface
        """
        virtual_interface = Interface(device=self.device1, name="V1", type=InterfaceTypeChoices.TYPE_VIRTUAL)
        cable = Cable(termination_a=self.interface2, termination_b=virtual_interface)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_a_wireless_inteface(self):
        """
        A cable cannot terminate to a wireless interface
        """
        wireless_interface = Interface(device=self.device1, name="W1", type=InterfaceTypeChoices.TYPE_80211A)
        cable = Cable(termination_a=self.interface2, termination_b=wireless_interface)
        with self.assertRaises(ValidationError):
            cable.clean()


class CablePathTestCase(TestCase):

    def setUp(self):

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        self.device2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 2', site=site
        )
        self.interface1 = Interface.objects.create(device=self.device1, name='eth0')
        self.interface2 = Interface.objects.create(device=self.device2, name='eth0')
        self.panel1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Panel 1', site=site
        )
        self.panel2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Panel 2', site=site
        )
        self.rear_port1 = RearPort.objects.create(
            device=self.panel1, name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C
        )
        self.front_port1 = FrontPort.objects.create(
            device=self.panel1, name='Front Port 1', type=PortTypeChoices.TYPE_8P8C, rear_port=self.rear_port1
        )
        self.rear_port2 = RearPort.objects.create(
            device=self.panel2, name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C
        )
        self.front_port2 = FrontPort.objects.create(
            device=self.panel2, name='Front Port 2', type=PortTypeChoices.TYPE_8P8C, rear_port=self.rear_port2
        )

    def test_path_completion(self):

        # First segment
        cable1 = Cable(termination_a=self.interface1, termination_b=self.front_port1)
        cable1.save()
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        self.assertIsNone(interface1.connected_endpoint)
        self.assertIsNone(interface1.connection_status)

        # Second segment
        cable2 = Cable(termination_a=self.rear_port1, termination_b=self.rear_port2)
        cable2.save()
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        self.assertIsNone(interface1.connected_endpoint)
        self.assertIsNone(interface1.connection_status)

        # Third segment
        cable3 = Cable(
            termination_a=self.front_port2,
            termination_b=self.interface2,
            status=CableStatusChoices.STATUS_PLANNED
        )
        cable3.save()
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        self.assertEqual(interface1.connected_endpoint, self.interface2)
        self.assertEqual(interface1.connection_status, CONNECTION_STATUS_PLANNED)

        # Switch third segment from planned to connected
        cable3.status = CableStatusChoices.STATUS_CONNECTED
        cable3.save()
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        self.assertEqual(interface1.connected_endpoint, self.interface2)
        self.assertEqual(interface1.connection_status, CONNECTION_STATUS_CONNECTED)

    def test_path_teardown(self):

        # Build the path
        cable1 = Cable(termination_a=self.interface1, termination_b=self.front_port1)
        cable1.save()
        cable2 = Cable(termination_a=self.rear_port1, termination_b=self.rear_port2)
        cable2.save()
        cable3 = Cable(termination_a=self.front_port2, termination_b=self.interface2)
        cable3.save()
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        self.assertEqual(interface1.connected_endpoint, self.interface2)
        self.assertEqual(interface1.connection_status, CONNECTION_STATUS_CONNECTED)

        # Remove a cable
        cable2.delete()
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        self.assertIsNone(interface1.connected_endpoint)
        self.assertIsNone(interface1.connection_status)
        interface2 = Interface.objects.get(pk=self.interface2.pk)
        self.assertIsNone(interface2.connected_endpoint)
        self.assertIsNone(interface2.connection_status)


class PowerCalculationTestCase(TestCase):

    def setUp(self):
        """
        The power toplogy:

            power_feed --> power_port1
                power_outlet12 --> power_port21
                power_outlet13 --> power_port31
                    power_outlet34 --> power_port43

        The two numbers at the end denote the direction, so power_outlet12 is from device 1 to device 2.
        """

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        device_role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1', color='ff0000')
        power_panel = PowerPanel.objects.create(name='Power Panel 1', site=site)

        self.device1 = Device.objects.create(
            site=site,
            device_type=device_type,
            device_role=device_role,
            name='Device 1'
        )
        self.device2 = Device.objects.create(
            site=site,
            device_type=device_type,
            device_role=device_role,
            name='Device 2'
        )
        self.device3 = Device.objects.create(
            site=site,
            device_type=device_type,
            device_role=device_role,
            name='Device 3'
        )
        self.device4 = Device.objects.create(
            site=site,
            device_type=device_type,
            device_role=device_role,
            name='Device 4'
        )

        # Power from power feed to device 1
        self.power_feed = PowerFeed.objects.create(
            name='Power Feed 1',
            power_panel=power_panel,
            phase=PowerFeedPhaseChoices.PHASE_3PHASE
        )
        self.power_port1 = PowerPort.objects.create(device=self.device1, name='Power Port 1')
        self.power_feed_cable = Cable.objects.create(termination_a=self.power_port1, termination_b=self.power_feed)

        # Power from device 1 to device 2
        self.power_outlet12 = PowerOutlet.objects.create(
            device=self.device1,
            name='Power Outlet 12',
            power_port=self.power_port1,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A,
        )
        self.power_port21 = PowerPort.objects.create(
            device=self.device2,
            name='Power Port 21',
            maximum_draw=25,
            allocated_draw=10,
        )
        Cable.objects.create(termination_a=self.power_outlet12, termination_b=self.power_port21)

        # Power from device 1 to device 3
        self.power_outlet13 = PowerOutlet.objects.create(
            device=self.device1,
            name='Power Outlet 13',
            power_port=self.power_port1,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_B,
        )
        self.power_port31 = PowerPort.objects.create(
            device=self.device3,
            name='Power Port 31',
            maximum_draw=7,
            allocated_draw=5,
        )
        Cable.objects.create(termination_a=self.power_outlet13, termination_b=self.power_port31)

        # Power from device 3 to device 4
        self.power_outlet34 = PowerOutlet.objects.create(
            device=self.device3,
            name='Power Outlet 34',
            power_port=self.power_port31,
        )
        self.power_port43 = PowerPort.objects.create(
            device=self.device4,
            name='Power Port 43',
            maximum_draw=4,
            allocated_draw=3,
        )
        Cable.objects.create(termination_a=self.power_outlet34, termination_b=self.power_port43)

    def test_power_cascade(self):
        """
        Ensure the power calculation cascades over all children. The outlet count is local-only.
        """
        stats = self.power_port1.get_power_draw()

        # Global stats: all devices/feeds
        self.assertEqual(stats['maximum'], 25 + 7 + 4)
        self.assertEqual(stats['allocated'], 10 + 5 + 3)
        self.assertEqual(stats['outlet_count'], 2)

        # Feed A stats: device 2
        self.assertEqual(stats['legs'][0]['maximum'], 25)
        self.assertEqual(stats['legs'][0]['allocated'], 10)
        self.assertEqual(stats['legs'][0]['outlet_count'], 1)

        # Feed B stats: devices 3 and 4 (through 3)
        self.assertEqual(stats['legs'][1]['maximum'], 7 + 4)
        self.assertEqual(stats['legs'][1]['allocated'], 5 + 3)
        self.assertEqual(stats['legs'][1]['outlet_count'], 1)

        # Feed C stats: no devices
        self.assertEqual(stats['legs'][2]['maximum'], 0)
        self.assertEqual(stats['legs'][2]['allocated'], 0)
        self.assertEqual(stats['legs'][2]['outlet_count'], 0)

    def test_power_loop(self):
        """
        Remove the connection between the power feed and device 1. Instead connect device 4 back to 1. The
        calculation should continue to be correct and the code should not infinitely loop. The children outlets should
        have their downstream power ports updated.

        The power toplogy becomes:

            power_outlet41 -> power_port1 (loop)
                power_outlet12 -> power_port21
                power_outlet13 -> power_port31
                    power_outlet34 -> power_port43
                        power_outlet41 -> power_port1 (loop)
        """
        # Power from device 4 to device 1
        self.power_outlet41 = PowerOutlet.objects.create(
            device=self.device4,
            name='Power Outlet 43',
            power_port=self.power_port43,
        )
        self.power_feed_cable.delete()
        loop_cable = Cable.objects.create(termination_a=self.power_outlet41, termination_b=self.power_port1)

        stats = self.power_port1.get_power_draw()

        self.assertEqual(stats['maximum'], 25 + 7 + 4)
        self.assertEqual(stats['allocated'], 10 + 5 + 3)

        # With a loop in the topology, all of the outlets affected by the loop have the same children. power_outlet12
        # is not part of the loop and should only have one child, power_port21.
        self.assertEqual(self.power_outlet12.downstream_powerports.count(), 1)
        self.assertEqual(self.power_outlet13.downstream_powerports.count(), 4)
        self.assertEqual(self.power_outlet34.downstream_powerports.count(), 4)
        self.assertEqual(self.power_outlet41.downstream_powerports.count(), 4)

        # When a loop-causing cable is removed, the downstream_powerports of the other outlets in the loop should be
        # updated appropriately. This test is necessary because, in a loop, each outlet is upstream and downstream of
        # every other outlet in that loop.

        # TODO: remove once loop-clearing is fixed
        return
        loop_cable.delete()

        self.assertEqual(self.power_outlet12.downstream_powerports.count(), 1)
        self.assertEqual(self.power_outlet13.downstream_powerports.count(), 2)
        self.assertEqual(self.power_outlet34.downstream_powerports.count(), 1)
        self.assertEqual(self.power_outlet41.downstream_powerports.count(), 0)
