from __future__ import unicode_literals

from django.test import TestCase

from dcim.models import *


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
            face=RACK_FACE_FRONT,
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
            face=RACK_FACE_REAR,
        )
        device1.save()

        # Validate rack height
        self.assertEqual(list(self.rack.units), list(reversed(range(1, 43))))

        # Validate inventory (front face)
        rack1_inventory_front = self.rack.get_front_elevation()
        self.assertEqual(rack1_inventory_front[-10]['device'], device1)
        del(rack1_inventory_front[-10])
        for u in rack1_inventory_front:
            self.assertIsNone(u['device'])

        # Validate inventory (rear face)
        rack1_inventory_rear = self.rack.get_rear_elevation()
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
            face=None,
        )
        self.assertTrue(pdu)


class InterfaceTestCase(TestCase):

    def setUp(self):

        self.site = Site.objects.create(
            name='TestSite1',
            slug='my-test-site'
        )
        self.rack = Rack.objects.create(
            name='TestRack1',
            facility_id='A101',
            site=self.site,
            u_height=42
        )
        self.manufacturer = Manufacturer.objects.create(
            name='Acme',
            slug='acme'
        )

        self.device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer,
            model='FrameForwarder 2048',
            slug='ff2048'
        )
        self.role = DeviceRole.objects.create(
            name='Switch',
            slug='switch',
        )

    def test_interface_order_natural(self):
        device1 = Device.objects.create(
            name='TestSwitch1',
            device_type=self.device_type,
            device_role=self.role,
            site=self.site,
            rack=self.rack,
            position=10,
            face=RACK_FACE_REAR,
        )
        interface1 = Interface.objects.create(
            device=device1,
            name='Ethernet1/3/1'
        )
        interface2 = Interface.objects.create(
            device=device1,
            name='Ethernet1/5/1'
        )
        interface3 = Interface.objects.create(
            device=device1,
            name='Ethernet1/4'
        )
        interface4 = Interface.objects.create(
            device=device1,
            name='Ethernet1/3/2/4'
        )
        interface5 = Interface.objects.create(
            device=device1,
            name='Ethernet1/3/2/1'
        )
        interface6 = Interface.objects.create(
            device=device1,
            name='Loopback1'
        )

        self.assertEqual(
            list(Interface.objects.all().order_naturally()),
            [interface1, interface5, interface4, interface3, interface2, interface6]
        )

    def test_interface_order_natural_subinterfaces(self):
        device1 = Device.objects.create(
            name='TestSwitch1',
            device_type=self.device_type,
            device_role=self.role,
            site=self.site,
            rack=self.rack,
            position=10,
            face=RACK_FACE_REAR,
        )
        interface1 = Interface.objects.create(
            device=device1,
            name='GigabitEthernet0/0/3'
        )
        interface2 = Interface.objects.create(
            device=device1,
            name='GigabitEthernet0/0/2.2'
        )
        interface3 = Interface.objects.create(
            device=device1,
            name='GigabitEthernet0/0/0.120'
        )
        interface4 = Interface.objects.create(
            device=device1,
            name='GigabitEthernet0/0/0'
        )
        interface5 = Interface.objects.create(
            device=device1,
            name='GigabitEthernet0/0/1.117'
        )
        interface6 = Interface.objects.create(
            device=device1,
            name='GigabitEthernet0'
        )
        self.assertEqual(
            list(Interface.objects.all().order_naturally()),
            [interface4, interface3, interface5, interface2, interface1, interface6]
        )
