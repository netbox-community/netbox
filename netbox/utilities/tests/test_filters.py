from django.conf import settings
from django.test import TestCase
import django_filters

from dcim.models import Region, Site
from utilities.filters import TreeNodeMultipleChoiceFilter


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
