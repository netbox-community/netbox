import django_filters
from django.conf import settings
from django.db import models
from django.test import TestCase
from mptt.fields import TreeForeignKey
from taggit.managers import TaggableManager

from circuits.choices import CircuitStatusChoices
from circuits.filtersets import CircuitFilterSet
from circuits.models import Circuit, Provider, CircuitType
from dcim.choices import *
from dcim.fields import MACAddressField
from dcim.filtersets import DeviceFilterSet, SiteFilterSet
from dcim.models import (
    Device, DeviceRole, DeviceType, Interface, Manufacturer, Platform, Rack, Region, Site
)
from extras.filters import TagFilter
from extras.models import TaggedItem
from ipam.models import RIR, ASN
from netbox.filtersets import BaseFilterSet
from utilities.filters import (
    MACAddressFilter, MultiValueCharFilter, MultiValueDateFilter, MultiValueDateTimeFilter, MultiValueNumberFilter,
    MultiValueTimeFilter, TreeNodeMultipleChoiceFilter,
)


class TreeNodeMultipleChoiceFilterTest(TestCase):

    class SiteFilterSet(django_filters.FilterSet):
        region = TreeNodeMultipleChoiceFilter(
            queryset=Region.objects.all(),
            field_name='region',
            lookup_expr='in',
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


class DummyModel(models.Model):
    """
    Dummy model used by BaseFilterSetTest for filter validation. Should never appear in a schema migration.
    """
    charfield = models.CharField(
        max_length=10
    )
    choicefield = models.IntegerField(
        choices=(('A', 1), ('B', 2), ('C', 3))
    )
    datefield = models.DateField()
    datetimefield = models.DateTimeField()
    integerfield = models.IntegerField()
    macaddressfield = MACAddressField()
    timefield = models.TimeField()
    treeforeignkeyfield = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE
    )

    tags = TaggableManager(through=TaggedItem)


class BaseFilterSetTest(TestCase):
    """
    Ensure that a BaseFilterSet automatically creates the expected set of filters for each filter type.
    """
    class DummyFilterSet(BaseFilterSet):
        charfield = django_filters.CharFilter()
        macaddressfield = MACAddressFilter()
        modelchoicefield = django_filters.ModelChoiceFilter(
            field_name='integerfield',  # We're pretending this is a ForeignKey field
            queryset=Site.objects.all()
        )
        modelmultiplechoicefield = django_filters.ModelMultipleChoiceFilter(
            field_name='integerfield',  # We're pretending this is a ForeignKey field
            queryset=Site.objects.all()
        )
        multiplechoicefield = django_filters.MultipleChoiceFilter(
            field_name='choicefield'
        )
        multivaluecharfield = MultiValueCharFilter(
            field_name='charfield'
        )
        tagfield = TagFilter()
        treeforeignkeyfield = TreeNodeMultipleChoiceFilter(
            queryset=DummyModel.objects.all()
        )

        class Meta:
            model = DummyModel
            fields = (
                'charfield',
                'choicefield',
                'datefield',
                'datetimefield',
                'integerfield',
                'macaddressfield',
                'modelchoicefield',
                'modelmultiplechoicefield',
                'multiplechoicefield',
                'tagfield',
                'timefield',
                'treeforeignkeyfield',
            )

    @classmethod
    def setUpTestData(cls):
        cls.filters = cls.DummyFilterSet().filters

    def test_char_filter(self):
        self.assertIsInstance(self.filters['charfield'], django_filters.CharFilter)
        self.assertEqual(self.filters['charfield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['charfield'].exclude, False)
        self.assertEqual(self.filters['charfield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['charfield__n'].exclude, True)
        self.assertEqual(self.filters['charfield__ie'].lookup_expr, 'iexact')
        self.assertEqual(self.filters['charfield__ie'].exclude, False)
        self.assertEqual(self.filters['charfield__nie'].lookup_expr, 'iexact')
        self.assertEqual(self.filters['charfield__nie'].exclude, True)
        self.assertEqual(self.filters['charfield__ic'].lookup_expr, 'icontains')
        self.assertEqual(self.filters['charfield__ic'].exclude, False)
        self.assertEqual(self.filters['charfield__nic'].lookup_expr, 'icontains')
        self.assertEqual(self.filters['charfield__nic'].exclude, True)
        self.assertEqual(self.filters['charfield__isw'].lookup_expr, 'istartswith')
        self.assertEqual(self.filters['charfield__isw'].exclude, False)
        self.assertEqual(self.filters['charfield__nisw'].lookup_expr, 'istartswith')
        self.assertEqual(self.filters['charfield__nisw'].exclude, True)
        self.assertEqual(self.filters['charfield__iew'].lookup_expr, 'iendswith')
        self.assertEqual(self.filters['charfield__iew'].exclude, False)
        self.assertEqual(self.filters['charfield__niew'].lookup_expr, 'iendswith')
        self.assertEqual(self.filters['charfield__niew'].exclude, True)

    def test_mac_address_filter(self):
        self.assertIsInstance(self.filters['macaddressfield'], MACAddressFilter)
        self.assertEqual(self.filters['macaddressfield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['macaddressfield'].exclude, False)
        self.assertEqual(self.filters['macaddressfield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['macaddressfield__n'].exclude, True)
        self.assertEqual(self.filters['macaddressfield__ie'].lookup_expr, 'iexact')
        self.assertEqual(self.filters['macaddressfield__ie'].exclude, False)
        self.assertEqual(self.filters['macaddressfield__nie'].lookup_expr, 'iexact')
        self.assertEqual(self.filters['macaddressfield__nie'].exclude, True)
        self.assertEqual(self.filters['macaddressfield__ic'].lookup_expr, 'icontains')
        self.assertEqual(self.filters['macaddressfield__ic'].exclude, False)
        self.assertEqual(self.filters['macaddressfield__nic'].lookup_expr, 'icontains')
        self.assertEqual(self.filters['macaddressfield__nic'].exclude, True)
        self.assertEqual(self.filters['macaddressfield__isw'].lookup_expr, 'istartswith')
        self.assertEqual(self.filters['macaddressfield__isw'].exclude, False)
        self.assertEqual(self.filters['macaddressfield__nisw'].lookup_expr, 'istartswith')
        self.assertEqual(self.filters['macaddressfield__nisw'].exclude, True)
        self.assertEqual(self.filters['macaddressfield__iew'].lookup_expr, 'iendswith')
        self.assertEqual(self.filters['macaddressfield__iew'].exclude, False)
        self.assertEqual(self.filters['macaddressfield__niew'].lookup_expr, 'iendswith')
        self.assertEqual(self.filters['macaddressfield__niew'].exclude, True)

    def test_model_choice_filter(self):
        self.assertIsInstance(self.filters['modelchoicefield'], django_filters.ModelChoiceFilter)
        self.assertEqual(self.filters['modelchoicefield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['modelchoicefield'].exclude, False)
        self.assertEqual(self.filters['modelchoicefield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['modelchoicefield__n'].exclude, True)

    def test_model_multiple_choice_filter(self):
        self.assertIsInstance(self.filters['modelmultiplechoicefield'], django_filters.ModelMultipleChoiceFilter)
        self.assertEqual(self.filters['modelmultiplechoicefield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['modelmultiplechoicefield'].exclude, False)
        self.assertEqual(self.filters['modelmultiplechoicefield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['modelmultiplechoicefield__n'].exclude, True)

    def test_multi_value_char_filter(self):
        self.assertIsInstance(self.filters['multivaluecharfield'], MultiValueCharFilter)
        self.assertEqual(self.filters['multivaluecharfield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['multivaluecharfield'].exclude, False)
        self.assertEqual(self.filters['multivaluecharfield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['multivaluecharfield__n'].exclude, True)
        self.assertEqual(self.filters['multivaluecharfield__ie'].lookup_expr, 'iexact')
        self.assertEqual(self.filters['multivaluecharfield__ie'].exclude, False)
        self.assertEqual(self.filters['multivaluecharfield__nie'].lookup_expr, 'iexact')
        self.assertEqual(self.filters['multivaluecharfield__nie'].exclude, True)
        self.assertEqual(self.filters['multivaluecharfield__ic'].lookup_expr, 'icontains')
        self.assertEqual(self.filters['multivaluecharfield__ic'].exclude, False)
        self.assertEqual(self.filters['multivaluecharfield__nic'].lookup_expr, 'icontains')
        self.assertEqual(self.filters['multivaluecharfield__nic'].exclude, True)
        self.assertEqual(self.filters['multivaluecharfield__isw'].lookup_expr, 'istartswith')
        self.assertEqual(self.filters['multivaluecharfield__isw'].exclude, False)
        self.assertEqual(self.filters['multivaluecharfield__nisw'].lookup_expr, 'istartswith')
        self.assertEqual(self.filters['multivaluecharfield__nisw'].exclude, True)
        self.assertEqual(self.filters['multivaluecharfield__iew'].lookup_expr, 'iendswith')
        self.assertEqual(self.filters['multivaluecharfield__iew'].exclude, False)
        self.assertEqual(self.filters['multivaluecharfield__niew'].lookup_expr, 'iendswith')
        self.assertEqual(self.filters['multivaluecharfield__niew'].exclude, True)

    def test_multi_value_date_filter(self):
        self.assertIsInstance(self.filters['datefield'], MultiValueDateFilter)
        self.assertEqual(self.filters['datefield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['datefield'].exclude, False)
        self.assertEqual(self.filters['datefield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['datefield__n'].exclude, True)
        self.assertEqual(self.filters['datefield__lt'].lookup_expr, 'lt')
        self.assertEqual(self.filters['datefield__lt'].exclude, False)
        self.assertEqual(self.filters['datefield__lte'].lookup_expr, 'lte')
        self.assertEqual(self.filters['datefield__lte'].exclude, False)
        self.assertEqual(self.filters['datefield__gt'].lookup_expr, 'gt')
        self.assertEqual(self.filters['datefield__gt'].exclude, False)
        self.assertEqual(self.filters['datefield__gte'].lookup_expr, 'gte')
        self.assertEqual(self.filters['datefield__gte'].exclude, False)

    def test_multi_value_datetime_filter(self):
        self.assertIsInstance(self.filters['datetimefield'], MultiValueDateTimeFilter)
        self.assertEqual(self.filters['datetimefield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['datetimefield'].exclude, False)
        self.assertEqual(self.filters['datetimefield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['datetimefield__n'].exclude, True)
        self.assertEqual(self.filters['datetimefield__lt'].lookup_expr, 'lt')
        self.assertEqual(self.filters['datetimefield__lt'].exclude, False)
        self.assertEqual(self.filters['datetimefield__lte'].lookup_expr, 'lte')
        self.assertEqual(self.filters['datetimefield__lte'].exclude, False)
        self.assertEqual(self.filters['datetimefield__gt'].lookup_expr, 'gt')
        self.assertEqual(self.filters['datetimefield__gt'].exclude, False)
        self.assertEqual(self.filters['datetimefield__gte'].lookup_expr, 'gte')
        self.assertEqual(self.filters['datetimefield__gte'].exclude, False)

    def test_multi_value_number_filter(self):
        self.assertIsInstance(self.filters['integerfield'], MultiValueNumberFilter)
        self.assertEqual(self.filters['integerfield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['integerfield'].exclude, False)
        self.assertEqual(self.filters['integerfield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['integerfield__n'].exclude, True)
        self.assertEqual(self.filters['integerfield__lt'].lookup_expr, 'lt')
        self.assertEqual(self.filters['integerfield__lt'].exclude, False)
        self.assertEqual(self.filters['integerfield__lte'].lookup_expr, 'lte')
        self.assertEqual(self.filters['integerfield__lte'].exclude, False)
        self.assertEqual(self.filters['integerfield__gt'].lookup_expr, 'gt')
        self.assertEqual(self.filters['integerfield__gt'].exclude, False)
        self.assertEqual(self.filters['integerfield__gte'].lookup_expr, 'gte')
        self.assertEqual(self.filters['integerfield__gte'].exclude, False)

    def test_multi_value_time_filter(self):
        self.assertIsInstance(self.filters['timefield'], MultiValueTimeFilter)
        self.assertEqual(self.filters['timefield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['timefield'].exclude, False)
        self.assertEqual(self.filters['timefield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['timefield__n'].exclude, True)
        self.assertEqual(self.filters['timefield__lt'].lookup_expr, 'lt')
        self.assertEqual(self.filters['timefield__lt'].exclude, False)
        self.assertEqual(self.filters['timefield__lte'].lookup_expr, 'lte')
        self.assertEqual(self.filters['timefield__lte'].exclude, False)
        self.assertEqual(self.filters['timefield__gt'].lookup_expr, 'gt')
        self.assertEqual(self.filters['timefield__gt'].exclude, False)
        self.assertEqual(self.filters['timefield__gte'].lookup_expr, 'gte')
        self.assertEqual(self.filters['timefield__gte'].exclude, False)

    def test_multiple_choice_filter(self):
        self.assertIsInstance(self.filters['multiplechoicefield'], django_filters.MultipleChoiceFilter)
        self.assertEqual(self.filters['multiplechoicefield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['multiplechoicefield'].exclude, False)
        self.assertEqual(self.filters['multiplechoicefield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['multiplechoicefield__n'].exclude, True)
        self.assertEqual(self.filters['multiplechoicefield__ie'].lookup_expr, 'iexact')
        self.assertEqual(self.filters['multiplechoicefield__ie'].exclude, False)
        self.assertEqual(self.filters['multiplechoicefield__nie'].lookup_expr, 'iexact')
        self.assertEqual(self.filters['multiplechoicefield__nie'].exclude, True)
        self.assertEqual(self.filters['multiplechoicefield__ic'].lookup_expr, 'icontains')
        self.assertEqual(self.filters['multiplechoicefield__ic'].exclude, False)
        self.assertEqual(self.filters['multiplechoicefield__nic'].lookup_expr, 'icontains')
        self.assertEqual(self.filters['multiplechoicefield__nic'].exclude, True)
        self.assertEqual(self.filters['multiplechoicefield__isw'].lookup_expr, 'istartswith')
        self.assertEqual(self.filters['multiplechoicefield__isw'].exclude, False)
        self.assertEqual(self.filters['multiplechoicefield__nisw'].lookup_expr, 'istartswith')
        self.assertEqual(self.filters['multiplechoicefield__nisw'].exclude, True)
        self.assertEqual(self.filters['multiplechoicefield__iew'].lookup_expr, 'iendswith')
        self.assertEqual(self.filters['multiplechoicefield__iew'].exclude, False)
        self.assertEqual(self.filters['multiplechoicefield__niew'].lookup_expr, 'iendswith')
        self.assertEqual(self.filters['multiplechoicefield__niew'].exclude, True)

    def test_tag_filter(self):
        self.assertIsInstance(self.filters['tagfield'], TagFilter)
        self.assertEqual(self.filters['tagfield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['tagfield'].exclude, False)
        self.assertEqual(self.filters['tagfield__n'].lookup_expr, 'exact')
        self.assertEqual(self.filters['tagfield__n'].exclude, True)

    def test_tree_node_multiple_choice_filter(self):
        self.assertIsInstance(self.filters['treeforeignkeyfield'], TreeNodeMultipleChoiceFilter)
        # TODO: lookup_expr different for negation?
        self.assertEqual(self.filters['treeforeignkeyfield'].lookup_expr, 'exact')
        self.assertEqual(self.filters['treeforeignkeyfield'].exclude, False)
        self.assertEqual(self.filters['treeforeignkeyfield__n'].lookup_expr, 'in')
        self.assertEqual(self.filters['treeforeignkeyfield__n'].exclude, True)


class DynamicFilterLookupExpressionTest(TestCase):
    """
    Validate function of automatically generated filters using the Device model as an example.
    """
    device_queryset = Device.objects.all()
    device_filterset = DeviceFilterSet
    site_queryset = Site.objects.all()
    site_filterset = SiteFilterSet
    circuit_queryset = Circuit.objects.all()
    circuit_filterset = CircuitFilterSet

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

        rir = RIR.objects.create(name='RFC 6996', is_private=True)

        asns = [
            ASN(asn=65001, rir=rir),
            ASN(asn=65101, rir=rir),
            ASN(asn=65201, rir=rir)
        ]
        ASN.objects.bulk_create(asns)

        asns[0].sites.add(sites[0])
        asns[1].sites.add(sites[1])
        asns[2].sites.add(sites[2])

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
