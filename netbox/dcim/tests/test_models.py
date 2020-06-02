from django.core.exceptions import ValidationError
from django.test import TestCase

from circuits.models import *
from dcim.choices import *
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
        self.interface3 = Interface.objects.create(device=self.device2, name='eth1')
        self.cable = Cable(termination_a=self.interface1, termination_b=self.interface2)
        self.cable.save()

        self.power_port1 = PowerPort.objects.create(device=self.device2, name='psu1')
        self.patch_pannel = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='TestPatchPannel', site=site
        )
        self.rear_port1 = RearPort.objects.create(device=self.patch_pannel, name='RP1', type='8p8c')
        self.front_port1 = FrontPort.objects.create(
            device=self.patch_pannel, name='FP1', type='8p8c', rear_port=self.rear_port1, rear_port_position=1
        )
        self.rear_port2 = RearPort.objects.create(device=self.patch_pannel, name='RP2', type='8p8c', positions=2)
        self.front_port2 = FrontPort.objects.create(
            device=self.patch_pannel, name='FP2', type='8p8c', rear_port=self.rear_port2, rear_port_position=1
        )
        self.rear_port3 = RearPort.objects.create(device=self.patch_pannel, name='RP3', type='8p8c', positions=3)
        self.front_port3 = FrontPort.objects.create(
            device=self.patch_pannel, name='FP3', type='8p8c', rear_port=self.rear_port3, rear_port_position=1
        )
        self.provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        self.circuittype = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        self.circuit = Circuit.objects.create(provider=self.provider, type=self.circuittype, cid='1')
        self.circuittermination1 = CircuitTermination.objects.create(circuit=self.circuit, site=site, term_side='A', port_speed=1000)
        self.circuittermination2 = CircuitTermination.objects.create(circuit=self.circuit, site=site, term_side='Z', port_speed=1000)

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

    def test_cable_validates_compatible_types(self):
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
        cable = Cable(termination_a=self.front_port1, termination_b=self.rear_port1)
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

    def test_singlepos_rearport_connections(self):
        """
        A RearPort with one position can be connected to anything as it is just a
        cable extender.
        """
        # Connecting a single-position RearPort to a multi-position RearPort is ok
        Cable(termination_a=self.rear_port1, termination_b=self.rear_port2).full_clean()

        # Connecting a single-position RearPort to an Interface is ok
        Cable(termination_a=self.rear_port1, termination_b=self.interface3).full_clean()

    def test_multipos_rearport_connections(self):
        """
        A RearPort with more than one position can only be connected to another RearPort with the same number of
        positions.
        """
        with self.assertRaises(
            ValidationError,
                msg='Connecting a 2-position RearPort to a 3-position RearPort should fail'
        ):
            Cable(termination_a=self.rear_port2, termination_b=self.rear_port3).full_clean()

        with self.assertRaises(
            ValidationError,
                msg='Connecting a multi-position RearPort to an Interface should fail'
        ):
            Cable(termination_a=self.rear_port2, termination_b=self.interface3).full_clean()

        # Connecting a multi-position RearPort to a CircuitTermination should be ok
        Cable(termination_a=self.rear_port1, termination_b=self.circuittermination1).full_clean()

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

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Device Role 1', slug='device-role-1', color='ff0000'
        )
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuittype = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        circuit = Circuit.objects.create(provider=provider, type=circuittype, cid='1')
        CircuitTermination.objects.bulk_create((
            CircuitTermination(circuit=circuit, site=site, term_side='A', port_speed=1000),
            CircuitTermination(circuit=circuit, site=site, term_side='Z', port_speed=1000),
        ))

        # Create four network devices with four interfaces each
        devices = (
            Device(device_type=devicetype, device_role=devicerole, name='Device 1', site=site),
            Device(device_type=devicetype, device_role=devicerole, name='Device 2', site=site),
            Device(device_type=devicetype, device_role=devicerole, name='Device 3', site=site),
            Device(device_type=devicetype, device_role=devicerole, name='Device 4', site=site),
        )
        Device.objects.bulk_create(devices)
        for device in devices:
            Interface.objects.bulk_create((
                Interface(device=device, name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
                Interface(device=device, name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
                Interface(device=device, name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
                Interface(device=device, name='Interface 4', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            ))

        # Create four patch panels, each with one rear port and four front ports
        patch_panels = (
            Device(device_type=devicetype, device_role=devicerole, name='Panel 1', site=site),
            Device(device_type=devicetype, device_role=devicerole, name='Panel 2', site=site),
            Device(device_type=devicetype, device_role=devicerole, name='Panel 3', site=site),
            Device(device_type=devicetype, device_role=devicerole, name='Panel 4', site=site),
            Device(device_type=devicetype, device_role=devicerole, name='Panel 5', site=site),
            Device(device_type=devicetype, device_role=devicerole, name='Panel 6', site=site),
        )
        Device.objects.bulk_create(patch_panels)

        # Create patch panels with 4 positions
        for patch_panel in patch_panels[:4]:
            rearport = RearPort.objects.create(device=patch_panel, name='Rear Port 1', positions=4, type=PortTypeChoices.TYPE_8P8C)
            FrontPort.objects.bulk_create((
                FrontPort(device=patch_panel, name='Front Port 1', rear_port=rearport, rear_port_position=1, type=PortTypeChoices.TYPE_8P8C),
                FrontPort(device=patch_panel, name='Front Port 2', rear_port=rearport, rear_port_position=2, type=PortTypeChoices.TYPE_8P8C),
                FrontPort(device=patch_panel, name='Front Port 3', rear_port=rearport, rear_port_position=3, type=PortTypeChoices.TYPE_8P8C),
                FrontPort(device=patch_panel, name='Front Port 4', rear_port=rearport, rear_port_position=4, type=PortTypeChoices.TYPE_8P8C),
            ))

        # Create 1-on-1 patch panels
        for patch_panel in patch_panels[4:]:
            rearport = RearPort.objects.create(device=patch_panel, name='Rear Port 1', positions=1, type=PortTypeChoices.TYPE_8P8C)
            FrontPort.objects.create(device=patch_panel, name='Front Port 1', rear_port=rearport, rear_port_position=1, type=PortTypeChoices.TYPE_8P8C)

    def test_direct_connection(self):
        """
        Test a direct connection between two interfaces.

        [Device 1] ----- [Device 2]
             Iface1     Iface1
        """
        # Create cable
        cable = Cable(
            termination_a=Interface.objects.get(device__name='Device 1', name='Interface 1'),
            termination_b=Interface.objects.get(device__name='Device 2', name='Interface 1')
        )
        cable.full_clean()
        cable.save()

        # Retrieve endpoints
        endpoint_a = Interface.objects.get(device__name='Device 1', name='Interface 1')
        endpoint_b = Interface.objects.get(device__name='Device 2', name='Interface 1')

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)

        # Delete cable
        cable.delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)

    def test_connection_via_one_on_one_port(self):
        """
        Test a connection which passes through a rear port with exactly one front port.

                     1               2
        [Device 1] ----- [Panel 5] ----- [Device 2]
             Iface1     FP1     RP1     Iface1
        """
        # Create cables (FP first, RP second)
        cable1 = Cable(
            termination_a=Interface.objects.get(device__name='Device 1', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 5', name='Front Port 1')
        )
        cable1.full_clean()
        cable1.save()
        cable2 = Cable(
            termination_a=RearPort.objects.get(device__name='Panel 5', name='Rear Port 1'),
            termination_b=Interface.objects.get(device__name='Device 2', name='Interface 1')
        )
        self.assertEqual(cable2.termination_a.positions, 1)  # Sanity check
        cable2.full_clean()
        cable2.save()

        # Retrieve endpoints
        endpoint_a = Interface.objects.get(device__name='Device 1', name='Interface 1')
        endpoint_b = Interface.objects.get(device__name='Device 2', name='Interface 1')

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)

        # Delete cable 1
        cable1.delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)

        # Recreate cable 1 to test creating the cables in reverse order (RP first, FP second)
        cable1 = Cable(
            termination_a=Interface.objects.get(device__name='Device 1', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 5', name='Front Port 1')
        )
        cable1.full_clean()
        cable1.save()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)

        # Delete cable 2
        cable2.delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)

    def test_connection_via_nested_one_on_one_port(self):
        """
        Test a connection which passes through a single front/rear port pair between two multi-position rear ports.

        Test two connections via patched rear ports:
            Device 1 <---> Device 2
            Device 3 <---> Device 4

                        1                                           2
        [Device 1] -----------+                               +----------- [Device 2]
              Iface1          |                               |          Iface1
                          FP1 |       3               4       | FP1
                          [Panel 1] ----- [Panel 5] ----- [Panel 2]
                          FP2 |  RP1     RP1     FP1     RP1  | FP2
              Iface1          |                               |          Iface1
        [Device 3] -----------+                               +----------- [Device 4]
                        5                                           6
        """
        # Create cables (Panel 5 RP first, FP second)
        cable1 = Cable(
            termination_a=Interface.objects.get(device__name='Device 1', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 1', name='Front Port 1')
        )
        cable1.full_clean()
        cable1.save()
        cable2 = Cable(
            termination_b=FrontPort.objects.get(device__name='Panel 2', name='Front Port 1'),
            termination_a=Interface.objects.get(device__name='Device 2', name='Interface 1')
        )
        cable2.full_clean()
        cable2.save()
        cable3 = Cable(
            termination_b=RearPort.objects.get(device__name='Panel 1', name='Rear Port 1'),
            termination_a=RearPort.objects.get(device__name='Panel 5', name='Rear Port 1')
        )
        cable3.full_clean()
        cable3.save()
        cable4 = Cable(
            termination_b=FrontPort.objects.get(device__name='Panel 5', name='Front Port 1'),
            termination_a=RearPort.objects.get(device__name='Panel 2', name='Rear Port 1')
        )
        cable4.full_clean()
        cable4.save()
        cable5 = Cable(
            termination_b=FrontPort.objects.get(device__name='Panel 1', name='Front Port 2'),
            termination_a=Interface.objects.get(device__name='Device 3', name='Interface 1')
        )
        cable5.full_clean()
        cable5.save()
        cable6 = Cable(
            termination_b=FrontPort.objects.get(device__name='Panel 2', name='Front Port 2'),
            termination_a=Interface.objects.get(device__name='Device 4', name='Interface 1')
        )
        cable6.full_clean()
        cable6.save()

        # Retrieve endpoints
        endpoint_a = Interface.objects.get(device__name='Device 1', name='Interface 1')
        endpoint_b = Interface.objects.get(device__name='Device 2', name='Interface 1')
        endpoint_c = Interface.objects.get(device__name='Device 3', name='Interface 1')
        endpoint_d = Interface.objects.get(device__name='Device 4', name='Interface 1')

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertEqual(endpoint_c.connected_endpoint, endpoint_d)
        self.assertEqual(endpoint_d.connected_endpoint, endpoint_c)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)
        self.assertTrue(endpoint_c.connection_status)
        self.assertTrue(endpoint_d.connection_status)

        # Delete cable 3
        cable3.delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()
        endpoint_c.refresh_from_db()
        endpoint_d.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_c.connected_endpoint)
        self.assertIsNone(endpoint_d.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)
        self.assertIsNone(endpoint_c.connection_status)
        self.assertIsNone(endpoint_d.connection_status)

        # Recreate cable 3 to test reverse order (Panel 5 FP first, RP second)
        cable3 = Cable(
            termination_b=RearPort.objects.get(device__name='Panel 1', name='Rear Port 1'),
            termination_a=RearPort.objects.get(device__name='Panel 5', name='Rear Port 1')
        )
        cable3.full_clean()
        cable3.save()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()
        endpoint_c.refresh_from_db()
        endpoint_d.refresh_from_db()

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertEqual(endpoint_c.connected_endpoint, endpoint_d)
        self.assertEqual(endpoint_d.connected_endpoint, endpoint_c)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)
        self.assertTrue(endpoint_c.connection_status)
        self.assertTrue(endpoint_d.connection_status)

        # Delete cable 4
        cable4.delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()
        endpoint_c.refresh_from_db()
        endpoint_d.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_c.connected_endpoint)
        self.assertIsNone(endpoint_d.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)
        self.assertIsNone(endpoint_c.connection_status)
        self.assertIsNone(endpoint_d.connection_status)

    def test_connections_via_patch(self):
        """
        Test two connections via patched rear ports:
            Device 1 <---> Device 2
            Device 3 <---> Device 4

                        1                           2
        [Device 1] -----------+               +----------- [Device 2]
              Iface1          |               |          Iface1
                          FP1 |       3       | FP1
                          [Panel 1] ----- [Panel 2]
                          FP2 |   RP1   RP1   | FP2
              Iface1          |               |          Iface1
        [Device 3] -----------+               +----------- [Device 4]
                        4                           5
        """
        # Create cables
        cable1 = Cable(
            termination_a=Interface.objects.get(device__name='Device 1', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 1', name='Front Port 1')
        )
        cable1.full_clean()
        cable1.save()
        cable2 = Cable(
            termination_a=Interface.objects.get(device__name='Device 2', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 2', name='Front Port 1')
        )
        cable2.full_clean()
        cable2.save()

        cable3 = Cable(
            termination_a=RearPort.objects.get(device__name='Panel 1', name='Rear Port 1'),
            termination_b=RearPort.objects.get(device__name='Panel 2', name='Rear Port 1')
        )
        cable3.full_clean()
        cable3.save()

        cable4 = Cable(
            termination_a=Interface.objects.get(device__name='Device 3', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 1', name='Front Port 2')
        )
        cable4.full_clean()
        cable4.save()
        cable5 = Cable(
            termination_a=Interface.objects.get(device__name='Device 4', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 2', name='Front Port 2')
        )
        cable5.full_clean()
        cable5.save()

        # Retrieve endpoints
        endpoint_a = Interface.objects.get(device__name='Device 1', name='Interface 1')
        endpoint_b = Interface.objects.get(device__name='Device 2', name='Interface 1')
        endpoint_c = Interface.objects.get(device__name='Device 3', name='Interface 1')
        endpoint_d = Interface.objects.get(device__name='Device 4', name='Interface 1')

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertEqual(endpoint_c.connected_endpoint, endpoint_d)
        self.assertEqual(endpoint_d.connected_endpoint, endpoint_c)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)
        self.assertTrue(endpoint_c.connection_status)
        self.assertTrue(endpoint_d.connection_status)

        # Delete cable 3
        cable3.delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()
        endpoint_c.refresh_from_db()
        endpoint_d.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_c.connected_endpoint)
        self.assertIsNone(endpoint_d.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)
        self.assertIsNone(endpoint_c.connection_status)
        self.assertIsNone(endpoint_d.connection_status)

    def test_connections_via_multiple_patches(self):
        """
        Test two connections via patched rear ports:
            Device 1 <---> Device 2
            Device 3 <---> Device 4

                        1                             2                             3
        [Device 1] -----------+               +---------------+               +----------- [Device 2]
              Iface1          |               |               |               |          Iface1
                          FP1 |       4       | FP1       FP1 |       5       | FP1
                          [Panel 1] ----- [Panel 2]       [Panel 3] ----- [Panel 4]
                          FP2 |   RP1   RP1   | FP2       FP2 |   RP1   RP1   | FP2
              Iface1          |               |               |               |          Iface1
        [Device 3] -----------+               +---------------+               +----------- [Device 4]
                        6                             7                             8
        """
        # Create cables
        cable1 = Cable(
            termination_a=Interface.objects.get(device__name='Device 1', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 1', name='Front Port 1')
        )
        cable1.full_clean()
        cable1.save()
        cable2 = Cable(
            termination_a=FrontPort.objects.get(device__name='Panel 2', name='Front Port 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 3', name='Front Port 1')
        )
        cable2.full_clean()
        cable2.save()
        cable3 = Cable(
            termination_a=FrontPort.objects.get(device__name='Panel 4', name='Front Port 1'),
            termination_b=Interface.objects.get(device__name='Device 2', name='Interface 1')
        )
        cable3.full_clean()
        cable3.save()

        cable4 = Cable(
            termination_a=RearPort.objects.get(device__name='Panel 1', name='Rear Port 1'),
            termination_b=RearPort.objects.get(device__name='Panel 2', name='Rear Port 1')
        )
        cable4.full_clean()
        cable4.save()
        cable5 = Cable(
            termination_a=RearPort.objects.get(device__name='Panel 3', name='Rear Port 1'),
            termination_b=RearPort.objects.get(device__name='Panel 4', name='Rear Port 1')
        )
        cable5.full_clean()
        cable5.save()

        cable6 = Cable(
            termination_a=Interface.objects.get(device__name='Device 3', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 1', name='Front Port 2')
        )
        cable6.full_clean()
        cable6.save()
        cable7 = Cable(
            termination_a=FrontPort.objects.get(device__name='Panel 2', name='Front Port 2'),
            termination_b=FrontPort.objects.get(device__name='Panel 3', name='Front Port 2')
        )
        cable7.full_clean()
        cable7.save()
        cable8 = Cable(
            termination_a=FrontPort.objects.get(device__name='Panel 4', name='Front Port 2'),
            termination_b=Interface.objects.get(device__name='Device 4', name='Interface 1')
        )
        cable8.full_clean()
        cable8.save()

        # Retrieve endpoints
        endpoint_a = Interface.objects.get(device__name='Device 1', name='Interface 1')
        endpoint_b = Interface.objects.get(device__name='Device 2', name='Interface 1')
        endpoint_c = Interface.objects.get(device__name='Device 3', name='Interface 1')
        endpoint_d = Interface.objects.get(device__name='Device 4', name='Interface 1')

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertEqual(endpoint_c.connected_endpoint, endpoint_d)
        self.assertEqual(endpoint_d.connected_endpoint, endpoint_c)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)
        self.assertTrue(endpoint_c.connection_status)
        self.assertTrue(endpoint_d.connection_status)

        # Delete cables 4 and 5
        cable4.delete()
        cable5.delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()
        endpoint_c.refresh_from_db()
        endpoint_d.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_c.connected_endpoint)
        self.assertIsNone(endpoint_d.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)
        self.assertIsNone(endpoint_c.connection_status)
        self.assertIsNone(endpoint_d.connection_status)

    def test_connections_via_nested_rear_ports(self):
        """
        Test two connections via nested rear ports:
            Device 1 <---> Device 2
            Device 3 <---> Device 4

                        1                                                           2
        [Device 1] -----------+                                               +----------- [Device 2]
              Iface1          |                                               |          Iface1
                          FP1 |       3               4               5       | FP1
                          [Panel 1] ----- [Panel 2] ----- [Panel 3] ----- [Panel 4]
                          FP2 |   RP1   FP1       RP1   RP1       FP1   RP1   | FP2
              Iface1          |                                               |          Iface1
        [Device 3] -----------+                                               +----------- [Device 4]
                        6                                                           7
        """
        # Create cables
        cable1 = Cable(
            termination_a=Interface.objects.get(device__name='Device 1', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 1', name='Front Port 1')
        )
        cable1.full_clean()
        cable1.save()
        cable2 = Cable(
            termination_a=FrontPort.objects.get(device__name='Panel 4', name='Front Port 1'),
            termination_b=Interface.objects.get(device__name='Device 2', name='Interface 1')
        )
        cable2.full_clean()
        cable2.save()

        cable3 = Cable(
            termination_a=RearPort.objects.get(device__name='Panel 1', name='Rear Port 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 2', name='Front Port 1')
        )
        cable3.full_clean()
        cable3.save()
        cable4 = Cable(
            termination_a=RearPort.objects.get(device__name='Panel 2', name='Rear Port 1'),
            termination_b=RearPort.objects.get(device__name='Panel 3', name='Rear Port 1')
        )
        cable4.full_clean()
        cable4.save()
        cable5 = Cable(
            termination_a=FrontPort.objects.get(device__name='Panel 3', name='Front Port 1'),
            termination_b=RearPort.objects.get(device__name='Panel 4', name='Rear Port 1')
        )
        cable5.full_clean()
        cable5.save()

        cable6 = Cable(
            termination_a=Interface.objects.get(device__name='Device 3', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 1', name='Front Port 2')
        )
        cable6.full_clean()
        cable6.save()
        cable7 = Cable(
            termination_a=FrontPort.objects.get(device__name='Panel 4', name='Front Port 2'),
            termination_b=Interface.objects.get(device__name='Device 4', name='Interface 1')
        )
        cable7.full_clean()
        cable7.save()

        # Retrieve endpoints
        endpoint_a = Interface.objects.get(device__name='Device 1', name='Interface 1')
        endpoint_b = Interface.objects.get(device__name='Device 2', name='Interface 1')
        endpoint_c = Interface.objects.get(device__name='Device 3', name='Interface 1')
        endpoint_d = Interface.objects.get(device__name='Device 4', name='Interface 1')

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertEqual(endpoint_c.connected_endpoint, endpoint_d)
        self.assertEqual(endpoint_d.connected_endpoint, endpoint_c)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)
        self.assertTrue(endpoint_c.connection_status)
        self.assertTrue(endpoint_d.connection_status)

        # Delete cable 4
        cable4.delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()
        endpoint_c.refresh_from_db()
        endpoint_d.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_c.connected_endpoint)
        self.assertIsNone(endpoint_d.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)
        self.assertIsNone(endpoint_c.connection_status)
        self.assertIsNone(endpoint_d.connection_status)

    def test_connection_via_circuit(self):
        """
                     1               2
        [Device 1] ----- [Circuit] ----- [Device 2]
             Iface1     A         Z     Iface1

        """
        # Create cables
        cable1 = Cable(
            termination_a=Interface.objects.get(device__name='Device 1', name='Interface 1'),
            termination_b=CircuitTermination.objects.get(term_side='A')
        )
        cable1.full_clean()
        cable1.save()
        cable2 = Cable(
            termination_a=CircuitTermination.objects.get(term_side='Z'),
            termination_b=Interface.objects.get(device__name='Device 2', name='Interface 1')
        )
        cable2.full_clean()
        cable2.save()

        # Retrieve endpoints
        endpoint_a = Interface.objects.get(device__name='Device 1', name='Interface 1')
        endpoint_b = Interface.objects.get(device__name='Device 2', name='Interface 1')

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)

        # Delete circuit
        circuit = Circuit.objects.first().delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)

    def test_connection_via_patched_circuit(self):
        """
                     1               2               3               4
        [Device 1] ----- [Panel 5] ----- [Circuit] ----- [Panel 6] ----- [Device 2]
             Iface1     FP1     RP1     A         Z     RP1     FP1     Iface1

        """
        # Create cables
        cable1 = Cable(
            termination_a=Interface.objects.get(device__name='Device 1', name='Interface 1'),
            termination_b=FrontPort.objects.get(device__name='Panel 5', name='Front Port 1')
        )
        cable1.full_clean()
        cable1.save()
        cable2 = Cable(
            termination_a=RearPort.objects.get(device__name='Panel 5', name='Rear Port 1'),
            termination_b=CircuitTermination.objects.get(term_side='A')
        )
        cable2.full_clean()
        cable2.save()
        cable3 = Cable(
            termination_a=CircuitTermination.objects.get(term_side='Z'),
            termination_b=RearPort.objects.get(device__name='Panel 6', name='Rear Port 1')
        )
        cable3.full_clean()
        cable3.save()
        cable4 = Cable(
            termination_a=FrontPort.objects.get(device__name='Panel 6', name='Front Port 1'),
            termination_b=Interface.objects.get(device__name='Device 2', name='Interface 1')
        )
        cable4.full_clean()
        cable4.save()

        # Retrieve endpoints
        endpoint_a = Interface.objects.get(device__name='Device 1', name='Interface 1')
        endpoint_b = Interface.objects.get(device__name='Device 2', name='Interface 1')

        # Validate connections
        self.assertEqual(endpoint_a.connected_endpoint, endpoint_b)
        self.assertEqual(endpoint_b.connected_endpoint, endpoint_a)
        self.assertTrue(endpoint_a.connection_status)
        self.assertTrue(endpoint_b.connection_status)

        # Delete circuit
        circuit = Circuit.objects.first().delete()

        # Refresh endpoints
        endpoint_a.refresh_from_db()
        endpoint_b.refresh_from_db()

        # Check that connections have been nullified
        self.assertIsNone(endpoint_a.connected_endpoint)
        self.assertIsNone(endpoint_b.connected_endpoint)
        self.assertIsNone(endpoint_a.connection_status)
        self.assertIsNone(endpoint_b.connection_status)
