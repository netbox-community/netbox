from django.conf import settings
from django.test import TestCase
import django_filters

from dcim.filters import SiteFilterSet
from dcim.models import Region, Site
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

    def setUp(self):

        super().setUp()

        self.region1 = Region.objects.create(name='Test Region 1', slug='test-region-1')
        self.region2 = Region.objects.create(name='Test Region 2', slug='test-region-2')
        self.site1 = Site.objects.create(region=self.region1, name='Test Site 1', slug='ABC-test-site1-ABC', asn=65001)
        self.site2 = Site.objects.create(region=self.region2, name='Test Site 2', slug='def-test-site2-def', asn=65101)
        self.site3 = Site.objects.create(region=None, name='Test Site 3', slug='ghi-test-site3-ghi', asn=65201)

        self.queryset = Site.objects.all()

    def test_site_name_negation(self):
        params = {'name__n': ['Test Site 1']}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 2)

    def test_site_slug_icontains(self):
        params = {'slug__ic': ['abc']}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 1)

    def test_site_slug_icontains_negation(self):
        params = {'slug__nic': ['abc']}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 2)

    def test_site_slug_startswith(self):
        params = {'slug__isw': ['abc']}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 1)

    def test_site_slug_startswith_negation(self):
        params = {'slug__nisw': ['abc']}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 2)

    def test_site_slug_endswith(self):
        params = {'slug__iew': ['abc']}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 1)

    def test_site_slug_endswith_negation(self):
        params = {'slug__niew': ['abc']}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 2)

    def test_site_asn_lt(self):
        params = {'asn__lt': [65101]}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 1)

    def test_site_asn_lte(self):
        params = {'asn__lte': [65101]}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 2)

    def test_site_asn_gt(self):
        params = {'asn__lt': [65101]}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 1)

    def test_site_asn_gte(self):
        params = {'asn__gte': [65101]}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 2)

    def test_site_region_negation(self):
        params = {'region__n': ['test-region-1']}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 2)

    def test_site_region_id_negation(self):
        params = {'region_id__n': [self.region1.pk]}
        self.assertEqual(SiteFilterSet(params, self.queryset).qs.count(), 2)
