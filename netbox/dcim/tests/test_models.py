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
        self.rear_port4 = RearPort.objects.create(device=self.patch_pannel, name='RP4', type='8p8c', positions=3)
        self.front_port4 = FrontPort.objects.create(
            device=self.patch_pannel, name='FP4', type='8p8c', rear_port=self.rear_port4, rear_port_position=1
        )
        self.provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        self.circuittype = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        self.circuit = Circuit.objects.create(provider=self.provider, type=self.circuittype, cid='1')
        self.circuittermination1 = CircuitTermination.objects.create(circuit=self.circuit, site=site, term_side='A')
        self.circuittermination2 = CircuitTermination.objects.create(circuit=self.circuit, site=site, term_side='Z')

    def test_cable_creation(self):
        """
        When a new Cable is created, it must be cached on either termination point.
        """
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        interface2 = Interface.objects.get(pk=self.interface2.pk)
        self.assertEqual(self.cable.termination_a, interface1)
        self.assertEqual(interface1._cable_peer, interface2)
        self.assertEqual(self.cable.termination_b, interface2)
        self.assertEqual(interface2._cable_peer, interface1)

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
        self.assertIsNone(interface1._cable_peer)
        interface2 = Interface.objects.get(pk=self.interface2.pk)
        self.assertIsNone(interface2.cable)
        self.assertIsNone(interface2._cable_peer)

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

    def test_rearport_connections(self):
        """
        Test various combinations of RearPort connections.
        """
        # Connecting a single-position RearPort to a multi-position RearPort is ok
        Cable(termination_a=self.rear_port1, termination_b=self.rear_port2).full_clean()

        # Connecting a single-position RearPort to an Interface is ok
        Cable(termination_a=self.rear_port1, termination_b=self.interface3).full_clean()

        # Connecting a single-position RearPort to a CircuitTermination is ok
        Cable(termination_a=self.rear_port1, termination_b=self.circuittermination1).full_clean()

        # Connecting a multi-position RearPort to another RearPort with the same number of positions is ok
        Cable(termination_a=self.rear_port3, termination_b=self.rear_port4).full_clean()

        # Connecting a multi-position RearPort to an Interface is ok
        Cable(termination_a=self.rear_port2, termination_b=self.interface3).full_clean()

        # Connecting a multi-position RearPort to a CircuitTermination is ok
        Cable(termination_a=self.rear_port2, termination_b=self.circuittermination1).full_clean()

        # Connecting a two-position RearPort to a three-position RearPort is NOT ok
        with self.assertRaises(
            ValidationError,
                msg='Connecting a 2-position RearPort to a 3-position RearPort should fail'
        ):
            Cable(termination_a=self.rear_port2, termination_b=self.rear_port3).full_clean()

    def test_cable_cannot_terminate_to_a_virtual_interface(self):
        """
        A cable cannot terminate to a virtual interface
        """
        virtual_interface = Interface(device=self.device1, name="V1", type=InterfaceTypeChoices.TYPE_VIRTUAL)
        cable = Cable(termination_a=self.interface2, termination_b=virtual_interface)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_a_wireless_interface(self):
        """
        A cable cannot terminate to a wireless interface
        """
        wireless_interface = Interface(device=self.device1, name="W1", type=InterfaceTypeChoices.TYPE_80211A)
        cable = Cable(termination_a=self.interface2, termination_b=wireless_interface)
        with self.assertRaises(ValidationError):
            cable.clean()
