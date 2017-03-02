from django.test import TestCase
from dcim.models import *


class RackTestCase(TestCase):

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

    def test_mount_single_device(self):

        device1 = Device(
            name='TestSwitch1',
            device_type=DeviceType.objects.get(manufacturer__slug='acme', slug='ff2048'),
            device_role=DeviceRole.objects.get(slug='switch'),
            site=self.site,
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
            site=self.site,
            rack=self.rack,
            position=None,
            face=None,
        )
        self.assertTrue(pdu)
