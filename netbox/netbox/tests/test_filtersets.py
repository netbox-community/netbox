from copy import deepcopy
from importlib import import_module

from django import forms
from django.conf import settings
from django.core.exceptions import EmptyResultSet
from django.http import QueryDict
from django.test import TestCase

from core.filtersets import ObjectChangeFilterSet
from core.models import ObjectChange, ObjectType
from dcim.choices import SiteStatusChoices
from dcim.filtersets import SiteFilterSet
from dcim.models import Region, Site
from extras.choices import CustomFieldFilterLogicChoices, CustomFieldTypeChoices
from extras.models import CustomField
from netbox.filtersets import FilterDict, get_data_keys
from netbox.registry import registry
from utilities.filters import ContentTypeFilter, MultiValueCharFilter, MultiValueContentTypeFilter

CORE_APPS = ('circuits', 'core', 'dcim', 'extras', 'ipam', 'tenancy', 'users', 'virtualization', 'vpn', 'wireless')


def get_sample_value(field):
    """
    Return a representative value for the given form field.
    """
    if isinstance(field, (forms.BooleanField, forms.NullBooleanField)):
        return 'true'
    if isinstance(field, (forms.ModelChoiceField, forms.ModelMultipleChoiceField)):
        return settings.FILTERS_NULL_CHOICE_VALUE
    if isinstance(field, forms.ChoiceField):
        for value, label in field.choices:
            # Descend into grouped choices
            if isinstance(label, (list, tuple)):
                value = label[0][0]
            if value not in ('', None, settings.FILTERS_NULL_CHOICE_VALUE):
                return str(value)
    if isinstance(field, forms.DateTimeField):
        return '2026-01-01 00:00:00'
    if isinstance(field, forms.DateField):
        return '2026-01-01'
    if isinstance(field, forms.TimeField):
        return '00:00:00'
    if isinstance(field, forms.DurationField):
        return '00:01:00'
    if isinstance(field, forms.UUIDField):
        return '00000000-0000-0000-0000-000000000001'
    if isinstance(field, (forms.IntegerField, forms.DecimalField, forms.FloatField)):
        return '1'
    return 'x'


def get_sample_data(filterset_class):
    """
    Return request data which supplies a value for every filter on the given FilterSet class.
    """
    data = QueryDict(mutable=True)
    for name, filter_ in filterset_class.get_filters().items():
        field = deepcopy(filter_).field
        if isinstance(filter_, (ContentTypeFilter, MultiValueContentTypeFilter)):
            data[name] = 'dcim.site'
        elif isinstance(field, forms.MultiValueField):
            for key, subfield in zip(get_data_keys(name, filter_), field.fields):
                data[key] = get_sample_value(subfield)
        elif filter_.method and isinstance(field, (forms.ModelChoiceField, forms.ModelMultipleChoiceField)):
            # Filter methods expect model instances, which this test doesn't create
            continue
        else:
            data[name] = get_sample_value(field)
    return data


def evaluate(filterset):
    """
    Return the errors and SQL resulting from evaluation of the given FilterSet.
    """
    try:
        sql = str(filterset.qs.query)
    except EmptyResultSet:
        sql = None
    except Exception as e:
        sql = repr(e)
    return list(filterset.errors), filterset.errors.get_json_data(), sql


class FilterSetEvaluationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.region = Region.objects.create(name='Region 1', slug='region-1')
        Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_ACTIVE),
            Site(name='Site 2', slug='site-2', status=SiteStatusChoices.STATUS_PLANNED),
            Site(name='Site 3', slug='site-3', status=SiteStatusChoices.STATUS_ACTIVE),
        ))

    def test_only_supplied_filters_are_copied(self):
        filterset = SiteFilterSet({'status': ['active'], 'limit': ['10']}, Site.objects.all())
        self.assertEqual(filterset.qs.count(), 2)
        self.assertEqual(list(filterset.filters.filters), ['status'])
        self.assertNotIn('_form', vars(filterset))

    def test_unbound(self):
        filterset = SiteFilterSet(queryset=Site.objects.all())
        self.assertFalse(filterset.is_valid())
        self.assertEqual(filterset.qs.count(), 3)

    def test_invalid_value(self):
        filterset = SiteFilterSet({'region_id': ['999999'], 'status': ['active']}, Site.objects.all())
        self.assertFalse(filterset.is_valid())
        self.assertEqual(list(filterset.errors), ['region_id'])
        # Valid filters are still applied
        self.assertEqual(filterset.qs.count(), 2)

    def test_legacy_evaluation(self):
        class LegacySiteFilterSet(SiteFilterSet):
            legacy_evaluation = True

        filterset = LegacySiteFilterSet({'status': ['active']}, Site.objects.all())
        self.assertEqual(filterset.qs.count(), 2)
        self.assertNotIsInstance(filterset.filters, FilterDict)
        self.assertIn('_form', vars(filterset))

    def test_form(self):
        filterset = SiteFilterSet({'status': ['active']}, Site.objects.all())
        self.assertEqual(list(filterset.form.fields), list(filterset.filters))
        self.assertEqual(filterset.form.cleaned_data['status'], ['active'])

    def test_filter_changes_are_per_instance(self):
        data = {'region_id': [self.region.pk]}
        filterset = SiteFilterSet(data, Site.objects.all())
        filterset.filters['region_id'].queryset = Region.objects.none()
        self.assertFalse(filterset.is_valid())
        self.assertTrue(SiteFilterSet(data, Site.objects.all()).is_valid())

    def test_added_filter(self):
        class ExtendedSiteFilterSet(SiteFilterSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.filters['label'] = MultiValueCharFilter(field_name='name')

        self.assertEqual(ExtendedSiteFilterSet({'label': ['Site 1']}, Site.objects.all()).qs.count(), 1)

    def test_get_filters_override(self):
        calls = []

        class CustomSiteFilterSet(SiteFilterSet):
            @classmethod
            def get_filters(cls):
                calls.append(cls)
                return super().get_filters()

        # A class which overrides get_filters() regenerates its filters on every instantiation
        calls.clear()
        CustomSiteFilterSet({}, Site.objects.all())
        CustomSiteFilterSet({}, Site.objects.all())
        self.assertEqual(len(calls), 2)

    def test_custom_field_filters(self):
        custom_field = CustomField.objects.create(
            name='cf1',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            filter_logic=CustomFieldFilterLogicChoices.FILTER_EXACT
        )
        custom_field.object_types.set([ObjectType.objects.get_for_model(Site)])
        Site.objects.filter(slug='site-1').update(custom_field_data={'cf1': 'foo'})

        self.assertEqual(SiteFilterSet({'cf_cf1': ['foo']}, Site.objects.all()).qs.count(), 1)
        self.assertEqual(SiteFilterSet({'cf_cf1__n': ['foo']}, Site.objects.all()).qs.count(), 2)
        self.assertIn('cf_cf1__ic', SiteFilterSet().filters)

    def test_custom_field_filters_not_loaded(self):
        # Custom fields aren't queried unless a cf_* filter is needed
        with self.assertNumQueries(0):
            SiteFilterSet({'status': ['active']}, Site.objects.all()).qs

    def test_widget_suffixed_data_keys(self):
        filterset = ObjectChangeFilterSet({'time_after': '2026-01-01 00:00:00'}, ObjectChange.objects.all())
        self.assertEqual(list(filterset.cleaned_data), ['time'])
        self.assertIn('"time" >=', str(filterset.qs.query))


class LegacyEvaluationParityTestCase(TestCase):

    def test_parity(self):
        """
        Evaluate every registered FilterSet with all of its filters supplied, and check that the result matches
        legacy evaluation.
        """
        # Import every core FilterSet so that it's registered
        for app_label in CORE_APPS:
            import_module(f'{app_label}.filtersets')

        for filterset_class in registry['filtersets'].values():
            with self.subTest(filterset=filterset_class.__name__):
                legacy_class = type(filterset_class.__name__, (filterset_class,), {'legacy_evaluation': True})
                data = get_sample_data(filterset_class)
                queryset = filterset_class._meta.model.objects.all()
                self.assertEqual(
                    evaluate(filterset_class(data, queryset)),
                    evaluate(legacy_class(data, queryset))
                )
