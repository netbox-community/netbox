from copy import deepcopy
from importlib import import_module

from django import forms
from django.conf import settings
from django.core.exceptions import EmptyResultSet
from django.http import QueryDict
from django.test import TestCase
from django.utils.datastructures import MultiValueDict
from django_filters import CharFilter, DateTimeFromToRangeFilter, FilterSet, MultipleChoiceFilter
from django_filters.widgets import QueryArrayWidget

from core.filtersets import ObjectChangeFilterSet
from core.models import ObjectChange, ObjectType
from dcim.choices import SiteStatusChoices
from dcim.filtersets import SiteFilterSet
from dcim.models import Region, Site
from extras.choices import CustomFieldFilterLogicChoices, CustomFieldTypeChoices
from extras.models import CustomField
from netbox.filtersets.utils import FilterDict, get_data_keys
from netbox.registry import registry
from utilities.filters import ContentTypeFilter, MultiValueCharFilter, MultiValueContentTypeFilter

CORE_APPS = ('circuits', 'core', 'dcim', 'extras', 'ipam', 'tenancy', 'users', 'virtualization', 'vpn', 'wireless')


def get_filterset_classes():
    """
    Return every registered FilterSet class, after importing the core FilterSets so that they're registered.
    """
    for app_label in CORE_APPS:
        import_module(f'{app_label}.filtersets')
    return list(registry['filtersets'].values())


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


def get_empty_data(filterset_class):
    """
    Return request data which supplies an empty value for every filter on the given FilterSet class.
    """
    data = QueryDict(mutable=True)
    for name, filter_ in filterset_class.get_filters().items():
        for key in get_data_keys(name, filter_):
            data[key] = ''
    return data


def get_subset(data, keys):
    """
    Return a copy of the given request data with only the given keys.
    """
    subset = QueryDict(mutable=True)
    for key in keys:
        subset.setlist(key, data.getlist(key))
    return subset


def get_sql(filterset):
    """
    Return the SQL of the given FilterSet's queryset, or None if the queryset is empty.
    """
    try:
        return str(filterset.qs.query)
    except EmptyResultSet:
        return None


def get_emptying_keys(filterset_class, data):
    """
    Return the keys of the given request data which each empty the FilterSet's queryset when supplied alone.
    """
    queryset = filterset_class._meta.model.objects.all()
    if get_sql(filterset_class(data, queryset)) is not None:
        return []
    return [key for key in data if get_sql(filterset_class(get_subset(data, [key]), queryset)) is None]


def evaluate(filterset):
    """
    Return the errors and SQL resulting from evaluation of the given FilterSet.
    """
    return list(filterset.errors), filterset.errors.get_json_data(), get_sql(filterset)


class RecordingQueryDict(QueryDict):
    """
    An empty QueryDict which records the keys read from it, and whether its keys were enumerated.
    """
    def __init__(self):
        super().__init__()
        self.keys_read = set()
        self.enumerated = False

    def __contains__(self, key):
        self.keys_read.add(key)
        return super().__contains__(key)

    def __getitem__(self, key):
        self.keys_read.add(key)
        return super().__getitem__(key)

    def _getlist(self, key, *args, **kwargs):
        self.keys_read.add(key)
        return super()._getlist(key, *args, **kwargs)

    def __iter__(self):
        self.enumerated = True
        return super().__iter__()

    def keys(self):
        self.enumerated = True
        return super().keys()

    def lists(self):
        self.enumerated = True
        return super().lists()


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

    def test_replaced_filter(self):
        class ExtendedSiteFilterSet(SiteFilterSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.filters['created'] = DateTimeFromToRangeFilter(field_name='created')

        # The replacement's data keys supersede those of the class filter
        filterset = ExtendedSiteFilterSet({'created_after': '2100-01-01 00:00:00'}, Site.objects.all())
        self.assertEqual(list(filterset.cleaned_data), ['created'])
        self.assertEqual(filterset.qs.count(), 0)

    def test_required_added_filter(self):
        class ExtendedSiteFilterSet(SiteFilterSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.filters['label'] = CharFilter(field_name='name', required=True)

        filterset = ExtendedSiteFilterSet({'status': ['active']}, Site.objects.all())
        self.assertFalse(filterset.is_valid())
        self.assertEqual(list(filterset.errors), ['label'])

    def test_changed_filters(self):
        class ChangedSiteFilterSet(SiteFilterSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.filters['q'].extra['required'] = True
                self.filters['created_by_request'].field.required = True
                self.filters['status'].extra['widget'] = QueryArrayWidget

        # Changes to the instance's filters, or to their fields, supersede the class's filters
        filterset = ChangedSiteFilterSet(QueryDict('status[]=planned'), Site.objects.all())
        self.assertEqual(set(filterset.errors), {'q', 'created_by_request'})
        self.assertEqual(filterset.qs.count(), 1)

    def test_removed_filters(self):
        class ReducedSiteFilterSet(SiteFilterSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.filters['created'] = DateTimeFromToRangeFilter(field_name='created')
                del self.filters['created']
                del self.filters['status']

        data = {'status': ['planned'], 'created_after': '2100-01-01 00:00:00'}
        filterset = ReducedSiteFilterSet(data, Site.objects.all())
        self.assertNotIn('status', filterset.filters)
        self.assertNotIn('created', filterset.filters)
        self.assertEqual(filterset.cleaned_data, {})
        self.assertEqual(filterset.qs.count(), 3)
        # Other instances are unaffected
        self.assertEqual(SiteFilterSet(data, Site.objects.all()).qs.count(), 1)

    def test_copy(self):
        filterset = SiteFilterSet({'status': ['active']}, Site.objects.all())
        filters = filterset.filters.copy()
        self.assertIs(type(filters), dict)
        self.assertEqual(list(filters), list(filterset.filters))
        del filters['status']
        self.assertIn('status', filterset.filters)

    def test_overrides_after_base(self):
        class StatusMixin(FilterSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.initialized = True

            def filter_queryset(self, queryset):
                return super().filter_queryset(queryset).filter(status=SiteStatusChoices.STATUS_ACTIVE)

        # A mixin which follows BaseFilterSet in the MRO forces legacy evaluation, so that its overrides are called
        class MixedSiteFilterSet(SiteFilterSet, StatusMixin):
            pass

        filterset = MixedSiteFilterSet({'name': ['Site 1', 'Site 2']}, Site.objects.all())
        self.assertNotIsInstance(filterset.filters, FilterDict)
        self.assertTrue(filterset.initialized)
        self.assertEqual(filterset.qs.count(), 1)

    def test_form_override(self):
        class RequiredSearchMixin(FilterSet):
            @property
            def form(self):
                form = super().form
                form.fields['q'].required = True
                return form

        # Overriding the form forces legacy evaluation, which validates via the form, whether the override precedes
        # or follows BaseFilterSet in the MRO
        for bases in ((RequiredSearchMixin, SiteFilterSet), (SiteFilterSet, RequiredSearchMixin)):
            with self.subTest(bases=[base.__name__ for base in bases]):
                filterset_class = type('CustomSiteFilterSet', bases, {})
                filterset = filterset_class({'status': ['active']}, Site.objects.all())
                self.assertNotIsInstance(filterset.filters, FilterDict)
                self.assertEqual(list(filterset.errors), ['q'])

    def test_query_array_widget(self):
        class ExtendedSiteFilterSet(SiteFilterSet):
            status_array = MultipleChoiceFilter(field_name='status', choices=SiteStatusChoices, widget=QueryArrayWidget)

        filterset = ExtendedSiteFilterSet(QueryDict('status_array[]=planned'), Site.objects.all())
        self.assertEqual(filterset.qs.count(), 1)

    def test_disabled_filters(self):
        class DeclaredSiteFilterSet(SiteFilterSet):
            label = CharFilter(field_name='name', lookup_expr='istartswith', disabled=True, initial='Site 2')

        class AddedSiteFilterSet(SiteFilterSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.filters['label'] = CharFilter(field_name='name', disabled=True, initial='Site 2')

        # A disabled filter takes its initial value, whether or not the request supplies one
        for filterset_class in (DeclaredSiteFilterSet, AddedSiteFilterSet):
            for data in ({'label': 'Site 1'}, {}):
                with self.subTest(filterset=filterset_class.__name__, data=data):
                    filterset = filterset_class(data, Site.objects.all())
                    self.assertEqual(list(filterset.qs.values_list('name', flat=True)), ['Site 2'])

    def test_custom_widget(self):
        class AliasWidget(forms.TextInput):
            def value_from_datadict(self, data, files, name):
                return data.get(f'{name}_alias')

        class ExtendedSiteFilterSet(SiteFilterSet):
            label = CharFilter(field_name='name', widget=AliasWidget)

        # A filter whose widget reads unknown keys is cleaned on every request
        filterset = ExtendedSiteFilterSet({'label_alias': 'Site 1'}, Site.objects.all())
        self.assertIn('label', filterset.cleaned_data)
        self.assertEqual(filterset.qs.count(), 1)

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
        Evaluate every registered FilterSet with all of its filters supplied, with all of them supplied but empty, and
        with none of them supplied, and check that each result matches legacy evaluation. A supplied value which
        empties the queryset is evaluated alone, so that it doesn't mask the SQL of the others.
        """
        for filterset_class in get_filterset_classes():
            legacy_class = type(filterset_class.__name__, (filterset_class,), {'legacy_evaluation': True})
            queryset = filterset_class._meta.model.objects.all()
            sample_data = get_sample_data(filterset_class)
            emptying_keys = get_emptying_keys(filterset_class, sample_data)
            datasets = {
                'supplied': get_subset(sample_data, [key for key in sample_data if key not in emptying_keys]),
                **{f'{key} only': get_subset(sample_data, [key]) for key in emptying_keys},
                'empty': get_empty_data(filterset_class),
                'absent': QueryDict(),
            }
            for dataset, data in datasets.items():
                with self.subTest(filterset=filterset_class.__name__, data=dataset):
                    result = evaluate(filterset_class(data, queryset))
                    self.assertEqual(result, evaluate(legacy_class(data, queryset)))
                    if dataset == 'supplied':
                        # The remaining values mustn't empty the queryset (leaving no SQL) in combination
                        self.assertIsNotNone(result[2])

    def test_data_keys(self):
        """
        Check that get_data_keys() includes every key of request data which each filter's widget reads.
        """
        for filterset_class in get_filterset_classes():
            for name, filter_ in filterset_class.get_filters().items():
                with self.subTest(filterset=filterset_class.__name__, filter=name):
                    keys = get_data_keys(name, filter_)
                    # Every core filter's widget should be recognized
                    self.assertIsNotNone(keys)
                    # Supply no data, so that widgets also read any keys they fall back to
                    data = RecordingQueryDict()
                    deepcopy(filter_).field.widget.value_from_datadict(data, MultiValueDict(), name)
                    self.assertFalse(data.enumerated)
                    self.assertEqual(data.keys_read - set(keys), set())
