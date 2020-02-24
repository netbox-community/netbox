from django.conf import settings
from django.test import TestCase
import django_filters

from dcim.filters import DeviceFilterSet, SiteFilterSet
from dcim.choices import *
from dcim.models import (
    Device, DeviceRole, DeviceType, Interface, Manufacturer, Platform, Rack, Region, Site
)
from ipam.models import IPAddress
from utilities.filters import BaseFilterSet, TreeNodeMultipleChoiceFilter


class TreeNodeMultipleChoiceFilterTest(TestCase):

    class SiteFilterSet(django_filters.FilterSet):
        region = TreeNodeMultipleChoiceFilter(
            queryset=Region.objects.all(),
            field_name='region__in',
            to_field_name='slug',
        )

    def setUp(self):

        super().setUp()

        self.region1 = Region.objects.create(name='Test Region 1', slug='test-region-1')
        self.region2 = Region.objects.create(name='Test Region 2', slug='test-region-2')
        self.site1 = Site.objects.create(region=self.region1, name='Test Site 1', slug='test-site1')
        self.site2 = Site.objects.create(region=self.region2, name='Test Site 2', slug='test-site2')
        self.site3 = Site.objects.create(region=None, name='Test Site 3', slug='test-site3')

        self.queryset = Site.objects.all()

    def test_filter_single(self):

        kwargs = {'region': ['test-region-1']}
        qs = self.SiteFilterSet(kwargs, self.queryset).qs

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0], self.site1)

    def test_filter_multiple(self):

        kwargs = {'region': ['test-region-1', 'test-region-2']}
        qs = self.SiteFilterSet(kwargs, self.queryset).qs

        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs[0], self.site1)
        self.assertEqual(qs[1], self.site2)

    def test_filter_null(self):

        kwargs = {'region': [settings.FILTERS_NULL_CHOICE_VALUE]}
        qs = self.SiteFilterSet(kwargs, self.queryset).qs

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0], self.site3)

    def test_filter_combined(self):

        kwargs = {'region': ['test-region-1', settings.FILTERS_NULL_CHOICE_VALUE]}
        qs = self.SiteFilterSet(kwargs, self.queryset).qs

        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs[0], self.site1)
        self.assertEqual(qs[1], self.site3)


class DynamicFilterLookupExpressionTest(TestCase):
    """
    These tests ensure of the utilities.filters.BaseFilterSet.get_filters() method
    correctly generates dynamic filter expressions
    """
    device_queryset = Device.objects.all()
    device_filterset = DeviceFilterSet
    site_queryset = Site.objects.all()
    site_filterset = SiteFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        device_types = (
            DeviceType(manufacturer=manufacturers[0], model='Model 1', slug='model-1', is_full_depth=True),
            DeviceType(manufacturer=manufacturers[1], model='Model 2', slug='model-2', is_full_depth=True),
            DeviceType(manufacturer=manufacturers[2], model='Model 3', slug='model-3', is_full_depth=False),
        )
        DeviceType.objects.bulk_create(device_types)

        device_roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(device_roles)

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
            Platform(name='Platform 3', slug='platform-3'),
        )
        Platform.objects.bulk_create(platforms)

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        sites = (
            Site(name='Site 1', slug='abc-site-1', region=regions[0], asn=65001),
            Site(name='Site 2', slug='def-site-2', region=regions[1], asn=65101),
            Site(name='Site 3', slug='ghi-site-3', region=regions[2], asn=65201),
        )
        Site.objects.bulk_create(sites)

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], device_role=device_roles[0], platform=platforms[0], serial='ABC', asset_tag='1001', site=sites[0], rack=racks[0], position=1, face=DeviceFaceChoices.FACE_FRONT, status=DeviceStatusChoices.STATUS_ACTIVE, local_context_data={"foo": 123}),
            Device(name='Device 2', device_type=device_types[1], device_role=device_roles[1], platform=platforms[1], serial='DEF', asset_tag='1002', site=sites[1], rack=racks[1], position=2, face=DeviceFaceChoices.FACE_FRONT, status=DeviceStatusChoices.STATUS_STAGED),
            Device(name='Device 3', device_type=device_types[2], device_role=device_roles[2], platform=platforms[2], serial='GHI', asset_tag='1003', site=sites[2], rack=racks[2], position=3, face=DeviceFaceChoices.FACE_REAR, status=DeviceStatusChoices.STATUS_FAILED),
        )
        Device.objects.bulk_create(devices)

        interfaces = (
            Interface(device=devices[0], name='Interface 1', mac_address='00-00-00-00-00-01'),
            Interface(device=devices[0], name='Interface 2', mac_address='aa-00-00-00-00-01'),
            Interface(device=devices[1], name='Interface 3', mac_address='00-00-00-00-00-02'),
            Interface(device=devices[1], name='Interface 4', mac_address='bb-00-00-00-00-02'),
            Interface(device=devices[2], name='Interface 5', mac_address='00-00-00-00-00-03'),
            Interface(device=devices[2], name='Interface 6', mac_address='cc-00-00-00-00-03'),
        )
        Interface.objects.bulk_create(interfaces)

    def test_site_name_negation(self):
        params = {'name__n': ['Site 1']}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 2)

    def test_site_slug_icontains(self):
        params = {'slug__ic': ['-1']}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 1)

    def test_site_slug_icontains_negation(self):
        params = {'slug__nic': ['-1']}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 2)

    def test_site_slug_startswith(self):
        params = {'slug__isw': ['abc']}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 1)

    def test_site_slug_startswith_negation(self):
        params = {'slug__nisw': ['abc']}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 2)

    def test_site_slug_endswith(self):
        params = {'slug__iew': ['-1']}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 1)

    def test_site_slug_endswith_negation(self):
        params = {'slug__niew': ['-1']}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 2)

    def test_site_asn_lt(self):
        params = {'asn__lt': [65101]}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 1)

    def test_site_asn_lte(self):
        params = {'asn__lte': [65101]}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 2)

    def test_site_asn_gt(self):
        params = {'asn__lt': [65101]}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 1)

    def test_site_asn_gte(self):
        params = {'asn__gte': [65101]}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 2)

    def test_site_region_negation(self):
        params = {'region__n': ['region-1']}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 2)

    def test_site_region_id_negation(self):
        params = {'region_id__n': [Region.objects.first().pk]}
        self.assertEqual(SiteFilterSet(params, self.site_queryset).qs.count(), 2)

    def test_device_name_eq(self):
        params = {'name': ['Device 1']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 1)

    def test_device_name_negation(self):
        params = {'name__n': ['Device 1']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 2)

    def test_device_name_startswith(self):
        params = {'name__isw': ['Device']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 3)

    def test_device_name_startswith_negation(self):
        params = {'name__nisw': ['Device 1']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 2)

    def test_device_name_endswith(self):
        params = {'name__iew': [' 1']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 1)

    def test_device_name_endswith_negation(self):
        params = {'name__niew': [' 1']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 2)

    def test_device_name_icontains(self):
        params = {'name__ic': [' 2']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 1)

    def test_device_name_icontains_negation(self):
        params = {'name__nic': [' ']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 0)

    def test_device_mac_address_negation(self):
        params = {'mac_address__n': ['00-00-00-00-00-01', 'aa-00-00-00-00-01']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 2)

    def test_device_mac_address_startswith(self):
        params = {'mac_address__isw': ['aa:']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 1)

    def test_device_mac_address_startswith_negation(self):
        params = {'mac_address__nisw': ['aa:']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 2)

    def test_device_mac_address_endswith(self):
        params = {'mac_address__iew': [':02']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 1)

    def test_device_mac_address_endswith_negation(self):
        params = {'mac_address__niew': [':02']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 2)

    def test_device_mac_address_icontains(self):
        params = {'mac_address__ic': ['aa:', 'bb']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 2)

    def test_device_mac_address_icontains_negation(self):
        params = {'mac_address__nic': ['aa:', 'bb']}
        self.assertEqual(DeviceFilterSet(params, self.device_queryset).qs.count(), 1)
