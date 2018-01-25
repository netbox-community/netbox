from __future__ import unicode_literals

from django.test import TestCase

from dcim.forms import *
from dcim.models import *


def get_id(model, slug):
    return model.objects.get(slug=slug).id


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
