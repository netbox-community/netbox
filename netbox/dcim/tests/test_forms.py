from django.test import TestCase

from dcim.forms import *
from dcim.models import *


def get_id(model, slug):
    return model.objects.get(slug=slug).id


class DeviceTestCase(TestCase):

    fixtures = ['dcim', 'ipam', 'virtualization']

    def test_racked_device(self):
        test = DeviceForm(data={
            'name': 'test',
            'device_role': get_id(DeviceRole, 'leaf-switch'),
            'tenant': None,
            'manufacturer': get_id(Manufacturer, 'juniper'),
            'device_type': get_id(DeviceType, 'qfx5100-48s'),
            'site': get_id(Site, 'test1'),
            'rack': '1',
            'face': DeviceFaceChoices.FACE_FRONT,
            'position': 41,
            'platform': get_id(Platform, 'juniper-junos'),
            'status': DeviceStatusChoices.STATUS_ACTIVE,
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
            'face': DeviceFaceChoices.FACE_FRONT,
            'position': 1,
            'platform': get_id(Platform, 'juniper-junos'),
            'status': DeviceStatusChoices.STATUS_ACTIVE,
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
            'face': '',
            'position': None,
            'platform': None,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
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
            'face': DeviceFaceChoices.FACE_REAR,
            'position': None,
            'platform': None,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertTrue(test.is_valid())
        self.assertTrue(test.save())

    def test_cloned_cluster_device_initial_data(self):
        test = DeviceForm(initial={
            'device_type': get_id(DeviceType, 'poweredge-r640'),
            'device_role': get_id(DeviceRole, 'server'),
            'status': DeviceStatusChoices.STATUS_ACTIVE,
            'site': get_id(Site, 'test1'),
            "cluster": Cluster.objects.get(id=4).id,
        })
        self.assertEqual(test.initial['manufacturer'], get_id(Manufacturer, 'dell'))
        self.assertIn('cluster_group', test.initial)
        self.assertEqual(test.initial['cluster_group'], get_id(ClusterGroup, 'vm-host'))
