from django.test import TestCase

from dcim.forms import *
from dcim.models import *
from virtualization.models import Cluster, ClusterGroup, ClusterType


def get_id(model, slug):
    return model.objects.get(slug=slug).id


class DeviceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        rack = Rack.objects.create(name='Rack 1', site=site)
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1', u_height=1
        )
        device_role = DeviceRole.objects.create(
            name='Device Role 1', slug='device-role-1', color='ff0000'
        )
        Platform.objects.create(name='Platform 1', slug='platform-1')
        Device.objects.create(
            name='Device 1', device_type=device_type, device_role=device_role, site=site, rack=rack, position=1
        )
        cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        cluster_group = ClusterGroup.objects.create(name='Cluster Group 1', slug='cluster-group-1')
        Cluster.objects.create(name='Cluster 1', type=cluster_type, group=cluster_group)

    def test_racked_device(self):
        form = DeviceForm(data={
            'name': 'New Device',
            'device_role': DeviceRole.objects.first().pk,
            'tenant': None,
            'manufacturer': Manufacturer.objects.first().pk,
            'device_type': DeviceType.objects.first().pk,
            'site': Site.objects.first().pk,
            'rack': Rack.objects.first().pk,
            'face': DeviceFaceChoices.FACE_FRONT,
            'position': 2,
            'platform': Platform.objects.first().pk,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_racked_device_occupied(self):
        form = DeviceForm(data={
            'name': 'test',
            'device_role': DeviceRole.objects.first().pk,
            'tenant': None,
            'manufacturer': Manufacturer.objects.first().pk,
            'device_type': DeviceType.objects.first().pk,
            'site': Site.objects.first().pk,
            'rack': Rack.objects.first().pk,
            'face': DeviceFaceChoices.FACE_FRONT,
            'position': 1,
            'platform': Platform.objects.first().pk,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('position', form.errors)

    def test_non_racked_device(self):
        form = DeviceForm(data={
            'name': 'New Device',
            'device_role': DeviceRole.objects.first().pk,
            'tenant': None,
            'manufacturer': Manufacturer.objects.first().pk,
            'device_type': DeviceType.objects.first().pk,
            'site': Site.objects.first().pk,
            'rack': None,
            'face': None,
            'position': None,
            'platform': Platform.objects.first().pk,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_non_racked_device_with_face_position(self):
        form = DeviceForm(data={
            'name': 'New Device',
            'device_role': DeviceRole.objects.first().pk,
            'tenant': None,
            'manufacturer': Manufacturer.objects.first().pk,
            'device_type': DeviceType.objects.first().pk,
            'site': Site.objects.first().pk,
            'rack': None,
            'face': DeviceFaceChoices.FACE_REAR,
            'position': 10,
            'platform': None,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('face', form.errors)
        self.assertIn('position', form.errors)

    def test_initial_data_population(self):
        device_type = DeviceType.objects.first()
        cluster = Cluster.objects.first()
        test = DeviceForm(initial={
            'device_type': device_type.pk,
            'device_role': DeviceRole.objects.first().pk,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
            'site': Site.objects.first().pk,
            'cluster': cluster.pk,
        })

        # Check that the initial value for the manufacturer is set automatically when assigning the device type
        self.assertEqual(test.initial['manufacturer'], device_type.manufacturer.pk)

        # Check that the initial value for the cluster group is set automatically when assigning the cluster
        self.assertEqual(test.initial['cluster_group'], cluster.group.pk)
