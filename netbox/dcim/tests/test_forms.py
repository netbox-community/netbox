from django.test import TestCase

from dcim.forms import *
from dcim.models import *


def get_id(model, slug):
    return model.objects.get(slug=slug).id


DEVICETYPE_DATA = {
    'manufacturer': 'Generic',
    'model': 'TEST-1000',
    'slug': 'test-1000',
    'u_height': 2,
    'console_ports': [
        {'name': 'Console Port 1'},
        {'name': 'Console Port 2'},
        {'name': 'Console Port 3'},
    ],
    'console_server_ports': [
        {'name': 'Console Server Port 1'},
        {'name': 'Console Server Port 2'},
        {'name': 'Console Server Port 3'},
    ],
    'power_ports': [
        {'name': 'Power Port 1'},
        {'name': 'Power Port 2'},
        {'name': 'Power Port 3'},
    ],
    'power_outlets': [
        {'name': 'Power Outlet 1', 'power_port': 'Power Port 1', 'feed_leg': POWERFEED_LEG_A},
        {'name': 'Power Outlet 2', 'power_port': 'Power Port 1', 'feed_leg': POWERFEED_LEG_A},
        {'name': 'Power Outlet 3', 'power_port': 'Power Port 1', 'feed_leg': POWERFEED_LEG_A},
    ],
    'interfaces': [
        {'name': 'Interface 1', 'type': IFACE_TYPE_1GE_FIXED, 'mgmt_only': True},
        {'name': 'Interface 2', 'type': IFACE_TYPE_1GE_FIXED},
        {'name': 'Interface 3', 'type': IFACE_TYPE_1GE_FIXED},
    ],
    'rear_ports': [
        {'name': 'Rear Port 1', 'type': PORT_TYPE_8P8C},
        {'name': 'Rear Port 2', 'type': PORT_TYPE_8P8C},
        {'name': 'Rear Port 3', 'type': PORT_TYPE_8P8C},
    ],
    'front_ports': [
        {'name': 'Front Port 1', 'type': PORT_TYPE_8P8C, 'rear_port': 'Rear Port 1'},
        {'name': 'Front Port 2', 'type': PORT_TYPE_8P8C, 'rear_port': 'Rear Port 2'},
        {'name': 'Front Port 3', 'type': PORT_TYPE_8P8C, 'rear_port': 'Rear Port 3'},
    ]
}


class DeviceTypeImportTestCase(TestCase):

    def setUp(self):

        Manufacturer(name='Generic', slug='generic').save()

    def test_import_devicetype_yaml(self):

        form = DeviceTypeImportForm(DEVICETYPE_DATA)

        self.assertTrue(form.is_valid(), "Form validation failed: {}".format(form.errors))

        form.save()
        dt = DeviceType.objects.get(model='TEST-1000')

        # Verify all of the components were created
        self.assertEqual(dt.consoleport_templates.count(), 3)
        cp1 = ConsolePortTemplate.objects.first()
        self.assertEqual(cp1.name, 'Console Port 1')

        self.assertEqual(dt.consoleserverport_templates.count(), 3)
        csp1 = ConsoleServerPortTemplate.objects.first()
        self.assertEqual(csp1.name, 'Console Server Port 1')

        self.assertEqual(dt.powerport_templates.count(), 3)
        pp1 = PowerPortTemplate.objects.first()
        self.assertEqual(pp1.name, 'Power Port 1')

        self.assertEqual(dt.poweroutlet_templates.count(), 3)
        po1 = PowerOutletTemplate.objects.first()
        self.assertEqual(po1.name, 'Power Outlet 1')
        self.assertEqual(po1.power_port, pp1)
        self.assertEqual(po1.feed_leg, POWERFEED_LEG_A)

        self.assertEqual(dt.interface_templates.count(), 4)
        iface1 = Interface.objects.first()
        self.assertEqual(iface1.name, 'Interface 1')
        self.assertEqual(iface1.type, IFACE_TYPE_1GE_FIXED)
        self.assertTrue(iface1.mgmt_only)

        self.assertEqual(dt.rearport_templates.count(), 3)
        rp1 = RearPortTemplate.objects.first()
        self.assertEqual(rp1.name, 'Rear Port 1')

        self.assertEqual(dt.frontport_templates.count(), 3)
        fp1 = FrontPortTemplate.objects.first()
        self.assertEqual(fp1.name, 'Front Port 1')
        self.assertEqual(fp1.rear_port, rp1)
        self.assertEqual(fp1.rear_port_position, 1)


class DeviceTestCase(TestCase):

    fixtures = ['dcim', 'ipam']

    def test_racked_device(self):
        test = DeviceForm(data={
            'name': 'test',
            'device_role': get_id(DeviceRole, 'leaf-switch'),
            'tenant': None,
            'manufacturer': get_id(Manufacturer, 'juniper'),
            'device_type': get_id(DeviceType, 'qfx5100-48s'),
            'site': get_id(Site, 'test1'),
            'rack': '1',
            'face': RACK_FACE_FRONT,
            'position': 41,
            'platform': get_id(Platform, 'juniper-junos'),
            'status': DEVICE_STATUS_ACTIVE,
        })
        self.assertTrue(test.is_valid(), test.fields['position'].choices)
        self.assertTrue(test.save())

    def test_racked_device_occupied(self):
        test = DeviceForm(data={
            'name': 'test',
            'device_role': get_id(DeviceRole, 'leaf-switch'),
            'tenant': None,
            'manufacturer': get_id(Manufacturer, 'juniper'),
            'device_type': get_id(DeviceType, 'qfx5100-48s'),
            'site': get_id(Site, 'test1'),
            'rack': '1',
            'face': RACK_FACE_FRONT,
            'position': 1,
            'platform': get_id(Platform, 'juniper-junos'),
            'status': DEVICE_STATUS_ACTIVE,
        })
        self.assertFalse(test.is_valid())

    def test_non_racked_device(self):
        test = DeviceForm(data={
            'name': 'test',
            'device_role': get_id(DeviceRole, 'pdu'),
            'tenant': None,
            'manufacturer': get_id(Manufacturer, 'servertech'),
            'device_type': get_id(DeviceType, 'cwg-24vym415c9'),
            'site': get_id(Site, 'test1'),
            'rack': '1',
            'face': None,
            'position': None,
            'platform': None,
            'status': DEVICE_STATUS_ACTIVE,
        })
        self.assertTrue(test.is_valid())
        self.assertTrue(test.save())

    def test_non_racked_device_with_face(self):
        test = DeviceForm(data={
            'name': 'test',
            'device_role': get_id(DeviceRole, 'pdu'),
            'tenant': None,
            'manufacturer': get_id(Manufacturer, 'servertech'),
            'device_type': get_id(DeviceType, 'cwg-24vym415c9'),
            'site': get_id(Site, 'test1'),
            'rack': '1',
            'face': RACK_FACE_REAR,
            'position': None,
            'platform': None,
            'status': DEVICE_STATUS_ACTIVE,
        })
        self.assertTrue(test.is_valid())
        self.assertTrue(test.save())
