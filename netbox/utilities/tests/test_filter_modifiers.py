from django import forms
from django.conf import settings
from django.db import models
from django.http import QueryDict
from django.template import Context
from django.test import RequestFactory, TestCase

import dcim.filtersets  # noqa: F401 - Import to register Device filterset
from dcim.forms.filtersets import DeviceFilterForm
from dcim.models import Device
from netbox.filtersets import BaseFilterSet
from tenancy.models import Tenant
from users.models import User
from utilities.filtersets import register_filterset
from utilities.forms.fields import TagFilterField
from utilities.forms.mixins import FilterModifierMixin
from utilities.forms.widgets import FilterModifierWidget
from utilities.templatetags.helpers import applied_filters


# Test model for FilterModifierMixin tests
class TestModel(models.Model):
    """Dummy model for testing filter modifiers."""
    char_field = models.CharField(max_length=100, blank=True)
    integer_field = models.IntegerField(null=True, blank=True)
    decimal_field = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    date_field = models.DateField(null=True, blank=True)
    boolean_field = models.BooleanField(default=False)

    class Meta:
        app_label = 'utilities'
        managed = False  # Don't create actual database table


# Test filterset using BaseFilterSet to automatically generate lookups
@register_filterset
class TestFilterSet(BaseFilterSet):
    class Meta:
        model = TestModel
        fields = ['char_field', 'integer_field', 'decimal_field', 'date_field', 'boolean_field']


class FilterModifierWidgetTest(TestCase):
    """Tests for FilterModifierWidget value extraction and rendering."""

    def test_value_from_datadict_finds_value_in_lookup_variant(self):
        """
        Widget should find value from serial__ic when field is named serial.
        This is critical for form redisplay after validation errors.
        """
        widget = FilterModifierWidget(
            widget=forms.TextInput(),
            lookups=[('exact', 'Is'), ('ic', 'Contains'), ('isw', 'Starts With')]
        )
        data = QueryDict('serial__ic=test123')

        result = widget.value_from_datadict(data, {}, 'serial')

        self.assertEqual(result, 'test123')

    def test_value_from_datadict_handles_exact_match(self):
        """Widget should detect exact match when field name has no modifier."""
        widget = FilterModifierWidget(
            widget=forms.TextInput(),
            lookups=[('exact', 'Is'), ('ic', 'Contains')]
        )
        data = QueryDict('serial=test456')

        result = widget.value_from_datadict(data, {}, 'serial')

        self.assertEqual(result, 'test456')

    def test_value_from_datadict_returns_none_when_no_value(self):
        """Widget should return None when no data present to avoid appearing in changed_data."""
        widget = FilterModifierWidget(
            widget=forms.TextInput(),
            lookups=[('exact', 'Is'), ('ic', 'Contains')]
        )
        data = QueryDict('')

        result = widget.value_from_datadict(data, {}, 'serial')

        self.assertIsNone(result)

    def test_get_context_includes_original_widget_and_lookups(self):
        """Widget context should include original widget context and lookup choices."""
        widget = FilterModifierWidget(
            widget=forms.TextInput(),
            lookups=[('exact', 'Is'), ('ic', 'Contains'), ('isw', 'Starts With')]
        )
        value = 'test'

        context = widget.get_context('serial', value, {})

        self.assertIn('original_widget', context['widget'])
        self.assertEqual(
            context['widget']['lookups'],
            [('exact', 'Is'), ('ic', 'Contains'), ('isw', 'Starts With')]
        )
        self.assertEqual(context['widget']['field_name'], 'serial')
        self.assertEqual(context['widget']['current_modifier'], 'exact')  # Defaults to exact, JS updates from URL
        self.assertEqual(context['widget']['current_value'], 'test')

    def test_get_context_handles_null_selection(self):
        """Widget should preserve the 'null' choice when rendering."""

        null_value = settings.FILTERS_NULL_CHOICE_VALUE
        null_label = settings.FILTERS_NULL_CHOICE_LABEL

        # Simulate a query for objects with no tenant assigned (?tenant_id=null)
        query_params = QueryDict(f'tenant_id={null_value}')
        form = DeviceFilterForm(query_params)

        # Rendering the field triggers FilterModifierWidget.get_context()
        try:
            html = form['tenant_id'].as_widget()
        except ValueError as e:
            # ValueError: Field 'id' expected a number but got 'null'
            self.fail(f"FilterModifierWidget raised ValueError on 'null' selection: {e}")

        # Verify the "None" option is rendered so user selection is preserved in the UI
        self.assertIn(f'value="{null_value}"', html)
        self.assertIn(null_label, html)

    def test_get_context_handles_mixed_selection(self):
        """Widget should preserve both real objects and the 'null' choice together."""

        null_value = settings.FILTERS_NULL_CHOICE_VALUE

        # Create a tenant to simulate a real object
        tenant = Tenant.objects.create(name='Tenant A', slug='tenant-a')

        # Simulate a selection containing both a real PK and the null sentinel
        query_params = QueryDict('', mutable=True)
        query_params.setlist('tenant_id', [str(tenant.pk), null_value])
        form = DeviceFilterForm(query_params)

        # Rendering the field triggers FilterModifierWidget.get_context()
        try:
            html = form['tenant_id'].as_widget()
        except ValueError as e:
            # ValueError: Field 'id' expected a number but got 'null'
            self.fail(f"FilterModifierWidget raised ValueError on 'null' selection: {e}")

        # Verify both the real object and the null option are present in the output
        self.assertIn(f'value="{tenant.pk}"', html)
        self.assertIn(f'value="{null_value}"', html)

    def test_widget_renders_modifier_dropdown_and_input(self):
        """Widget should render modifier dropdown alongside original input."""
        widget = FilterModifierWidget(
            widget=forms.TextInput(),
            lookups=[('exact', 'Is'), ('ic', 'Contains')]
        )

        html = widget.render('serial', 'test', {})

        # Should contain modifier dropdown
        self.assertIn('class="form-select modifier-select"', html)
        self.assertIn('data-field="serial"', html)
        self.assertIn('<option value="exact" selected>Is</option>', html)
        self.assertIn('<option value="ic">Contains</option>', html)

        # Should contain original input
        self.assertIn('type="text"', html)
        self.assertIn('name="serial"', html)
        self.assertIn('value="test"', html)


class FilterModifierMixinTest(TestCase):
    """Tests for FilterModifierMixin form field enhancement."""

    def test_mixin_enhances_char_field_with_modifiers(self):
        """CharField should be enhanced with contains/starts/ends modifiers."""
        class TestForm(FilterModifierMixin, forms.Form):
            char_field = forms.CharField(required=False)
            model = TestModel

        form = TestForm()

        self.assertIsInstance(form.fields['char_field'].widget, FilterModifierWidget)
        lookup_codes = [lookup[0] for lookup in form.fields['char_field'].widget.lookups]
        expected_lookups = ['exact', 'n', 'ic', 'isw', 'iew', 'ie', 'regex', 'iregex', 'empty_true', 'empty_false']
        self.assertEqual(lookup_codes, expected_lookups)

    def test_mixin_skips_boolean_fields(self):
        """Boolean fields should not be enhanced."""
        class TestForm(FilterModifierMixin, forms.Form):
            boolean_field = forms.BooleanField(required=False)
            model = TestModel

        form = TestForm()

        self.assertNotIsInstance(form.fields['boolean_field'].widget, FilterModifierWidget)

    def test_mixin_enhances_tag_filter_field(self):
        """TagFilterField should be enhanced even though it's a MultipleChoiceField."""
        class TestForm(FilterModifierMixin, forms.Form):
            tag = TagFilterField(Device)
            model = Device

        form = TestForm()

        self.assertIsInstance(form.fields['tag'].widget, FilterModifierWidget)
        tag_lookups = [lookup[0] for lookup in form.fields['tag'].widget.lookups]
        # Device filterset has tag and tag__n but not tag__empty
        expected_lookups = ['exact', 'n']
        self.assertEqual(tag_lookups, expected_lookups)

    def test_mixin_enhances_integer_field(self):
        """IntegerField should be enhanced with comparison modifiers."""
        class TestForm(FilterModifierMixin, forms.Form):
            integer_field = forms.IntegerField(required=False)
            model = TestModel

        form = TestForm()

        self.assertIsInstance(form.fields['integer_field'].widget, FilterModifierWidget)
        lookup_codes = [lookup[0] for lookup in form.fields['integer_field'].widget.lookups]
        expected_lookups = ['exact', 'n', 'gt', 'gte', 'lt', 'lte', 'empty_true', 'empty_false']
        self.assertEqual(lookup_codes, expected_lookups)

    def test_mixin_enhances_decimal_field(self):
        """DecimalField should be enhanced with comparison modifiers."""
        class TestForm(FilterModifierMixin, forms.Form):
            decimal_field = forms.DecimalField(required=False)
            model = TestModel

        form = TestForm()

        self.assertIsInstance(form.fields['decimal_field'].widget, FilterModifierWidget)
        lookup_codes = [lookup[0] for lookup in form.fields['decimal_field'].widget.lookups]
        expected_lookups = ['exact', 'n', 'gt', 'gte', 'lt', 'lte', 'empty_true', 'empty_false']
        self.assertEqual(lookup_codes, expected_lookups)

    def test_mixin_enhances_date_field(self):
        """DateField should be enhanced with date-appropriate modifiers."""
        class TestForm(FilterModifierMixin, forms.Form):
            date_field = forms.DateField(required=False)
            model = TestModel

        form = TestForm()

        self.assertIsInstance(form.fields['date_field'].widget, FilterModifierWidget)
        lookup_codes = [lookup[0] for lookup in form.fields['date_field'].widget.lookups]
        expected_lookups = ['exact', 'n', 'gt', 'gte', 'lt', 'lte', 'empty_true', 'empty_false']
        self.assertEqual(lookup_codes, expected_lookups)


class ExtendedLookupFilterPillsTest(TestCase):
    """Tests for filter pill rendering of extended lookups."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='test_user')

    def test_negation_lookup_filter_pill(self):
        """Filter pill should show 'is not' for negation lookup."""
        query_params = QueryDict('serial__n=ABC123')
        form = DeviceFilterForm(query_params)

        request = RequestFactory().get('/', query_params)
        request.user = self.user
        context = Context({'request': request})
        result = applied_filters(context, Device, form, query_params)

        self.assertGreater(len(result['applied_filters']), 0)
        filter_pill = result['applied_filters'][0]
        self.assertIn('is not', filter_pill['link_text'].lower())
        self.assertIn('ABC123', filter_pill['link_text'])

    def test_regex_lookup_filter_pill(self):
        """Filter pill should show 'matches pattern' for regex lookup."""
        query_params = QueryDict('serial__regex=^ABC.*')
        form = DeviceFilterForm(query_params)

        request = RequestFactory().get('/', query_params)
        request.user = self.user
        context = Context({'request': request})
        result = applied_filters(context, Device, form, query_params)

        self.assertGreater(len(result['applied_filters']), 0)
        filter_pill = result['applied_filters'][0]
        self.assertIn('matches pattern', filter_pill['link_text'].lower())

    def test_exact_lookup_filter_pill(self):
        """Filter pill should show field label and value without lookup modifier for exact match."""
        query_params = QueryDict('serial=ABC123')
        form = DeviceFilterForm(query_params)

        request = RequestFactory().get('/', query_params)
        request.user = self.user
        context = Context({'request': request})
        result = applied_filters(context, Device, form, query_params)

        self.assertGreater(len(result['applied_filters']), 0)
        filter_pill = result['applied_filters'][0]
        # Should not contain lookup modifier text
        self.assertNotIn('is not', filter_pill['link_text'].lower())
        self.assertNotIn('matches pattern', filter_pill['link_text'].lower())
        self.assertNotIn('contains', filter_pill['link_text'].lower())
        # Should contain field label and value
        self.assertIn('Serial', filter_pill['link_text'])
        self.assertIn('ABC123', filter_pill['link_text'])


class EmptyLookupTest(TestCase):
    """Tests for empty (is empty/not empty) lookup support."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='test_user')

    def test_empty_true_appears_in_filter_pills(self):
        """Filter pill should show 'Is Empty' for empty=true."""
        query_params = QueryDict('serial__empty=true')
        form = DeviceFilterForm(query_params)

        request = RequestFactory().get('/', query_params)
        request.user = self.user
        context = Context({'request': request})
        result = applied_filters(context, Device, form, query_params)

        self.assertGreater(len(result['applied_filters']), 0)
        filter_pill = result['applied_filters'][0]
        self.assertIn('empty', filter_pill['link_text'].lower())

    def test_empty_false_appears_in_filter_pills(self):
        """Filter pill should show 'Is Not Empty' for empty=false."""
        query_params = QueryDict('serial__empty=false')
        form = DeviceFilterForm(query_params)

        request = RequestFactory().get('/', query_params)
        request.user = self.user
        context = Context({'request': request})
        result = applied_filters(context, Device, form, query_params)

        self.assertGreater(len(result['applied_filters']), 0)
        filter_pill = result['applied_filters'][0]
        self.assertIn('not empty', filter_pill['link_text'].lower())
