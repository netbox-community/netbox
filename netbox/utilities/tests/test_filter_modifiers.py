from django import forms
from django.http import QueryDict
from django.template import Context
from django.test import RequestFactory, TestCase

from dcim.forms.filtersets import DeviceFilterForm
from dcim.models import Device
from users.models import User
from utilities.forms.fields import TagFilterField
from utilities.forms.mixins import FilterModifierMixin
from utilities.forms.widgets import FilterModifierWidget
from utilities.templatetags.helpers import applied_filters


class FilterModifierWidgetTest(TestCase):
    """Tests for FilterModifierWidget value extraction and rendering."""

    def test_value_from_datadict_finds_value_in_lookup_variant(self):
        """
        Widget should find value from serial__ic when field is named serial.
        This is critical for form redisplay after validation errors.
        """
        widget = FilterModifierWidget(
            original_widget=forms.TextInput(),
            lookups=[('exact', 'Is'), ('ic', 'Contains'), ('isw', 'Starts With')]
        )
        data = QueryDict('serial__ic=test123')

        result = widget.value_from_datadict(data, {}, 'serial')

        self.assertEqual(result, 'test123')

    def test_value_from_datadict_handles_exact_match(self):
        """Widget should detect exact match when field name has no modifier."""
        widget = FilterModifierWidget(
            original_widget=forms.TextInput(),
            lookups=[('exact', 'Is'), ('ic', 'Contains')]
        )
        data = QueryDict('serial=test456')

        result = widget.value_from_datadict(data, {}, 'serial')

        self.assertEqual(result, 'test456')

    def test_value_from_datadict_returns_none_when_no_value(self):
        """Widget should return None when no data present to avoid appearing in changed_data."""
        widget = FilterModifierWidget(
            original_widget=forms.TextInput(),
            lookups=[('exact', 'Is'), ('ic', 'Contains')]
        )
        data = QueryDict('')

        result = widget.value_from_datadict(data, {}, 'serial')

        self.assertIsNone(result)

    def test_get_context_includes_original_widget_and_lookups(self):
        """Widget context should include original widget context and lookup choices."""
        widget = FilterModifierWidget(
            original_widget=forms.TextInput(),
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

    def test_widget_renders_modifier_dropdown_and_input(self):
        """Widget should render modifier dropdown alongside original input."""
        widget = FilterModifierWidget(
            original_widget=forms.TextInput(),
            lookups=[('exact', 'Is'), ('ic', 'Contains')]
        )

        html = widget.render('serial', 'test', {})

        # Should contain modifier dropdown
        self.assertIn('class="form-select modifier-select"', html)
        self.assertIn('data-field="serial"', html)
        self.assertIn('value="exact"', html)
        self.assertIn('>Is</option>', html)
        self.assertIn('value="ic"', html)
        self.assertIn('>Contains</option>', html)

        # Should contain original input
        self.assertIn('type="text"', html)
        self.assertIn('name="serial"', html)
        self.assertIn('value="test"', html)


class FilterModifierMixinTest(TestCase):
    """Tests for FilterModifierMixin form field enhancement."""

    def test_mixin_enhances_char_field_with_modifiers(self):
        """CharField should be enhanced with contains/starts/ends modifiers."""
        class TestForm(FilterModifierMixin, forms.Form):
            name = forms.CharField(required=False)

        form = TestForm()

        self.assertIsInstance(form.fields['name'].widget, FilterModifierWidget)
        self.assertGreater(len(form.fields['name'].widget.lookups), 1)
        # Should have exact, ic, isw, iew
        lookup_codes = [lookup[0] for lookup in form.fields['name'].widget.lookups]
        self.assertIn('exact', lookup_codes)
        self.assertIn('ic', lookup_codes)

    def test_mixin_skips_boolean_fields(self):
        """Boolean fields should not be enhanced."""
        class TestForm(FilterModifierMixin, forms.Form):
            active = forms.BooleanField(required=False)

        form = TestForm()

        self.assertNotIsInstance(form.fields['active'].widget, FilterModifierWidget)

    def test_mixin_enhances_tag_filter_field(self):
        """TagFilterField should be enhanced even though it's a MultipleChoiceField."""
        class TestForm(FilterModifierMixin, forms.Form):
            tag = TagFilterField(Device)

        form = TestForm()

        self.assertIsInstance(form.fields['tag'].widget, FilterModifierWidget)
        tag_lookups = [lookup[0] for lookup in form.fields['tag'].widget.lookups]
        self.assertIn('exact', tag_lookups)
        self.assertIn('n', tag_lookups)

    def test_mixin_enhances_multi_choice_field(self):
        """Plain MultipleChoiceField should be enhanced with choice-appropriate lookups."""
        class TestForm(FilterModifierMixin, forms.Form):
            status = forms.MultipleChoiceField(choices=[('a', 'A'), ('b', 'B')], required=False)

        form = TestForm()

        self.assertIsInstance(form.fields['status'].widget, FilterModifierWidget)
        status_lookups = [lookup[0] for lookup in form.fields['status'].widget.lookups]
        # Should have choice-based lookups (not text-based like contains/regex)
        self.assertIn('exact', status_lookups)
        self.assertIn('n', status_lookups)
        self.assertIn('empty_true', status_lookups)
        # Should NOT have text-based lookups
        self.assertNotIn('ic', status_lookups)
        self.assertNotIn('regex', status_lookups)

    def test_mixin_enhances_integer_field(self):
        """IntegerField should be enhanced with comparison modifiers."""
        class TestForm(FilterModifierMixin, forms.Form):
            count = forms.IntegerField(required=False)

        form = TestForm()

        self.assertIsInstance(form.fields['count'].widget, FilterModifierWidget)
        lookup_codes = [lookup[0] for lookup in form.fields['count'].widget.lookups]
        self.assertIn('gte', lookup_codes)
        self.assertIn('lte', lookup_codes)

    def test_mixin_adds_isnull_lookup_to_all_fields(self):
        """All field types should include isnull (empty/not empty) lookup."""
        class TestForm(FilterModifierMixin, forms.Form):
            name = forms.CharField(required=False)
            count = forms.IntegerField(required=False)
            created = forms.DateField(required=False)

        form = TestForm()

        # CharField should have empty_true and empty_false
        char_lookups = [lookup[0] for lookup in form.fields['name'].widget.lookups]
        self.assertIn('empty_true', char_lookups)
        self.assertIn('empty_false', char_lookups)

        # IntegerField should have empty_true and empty_false
        int_lookups = [lookup[0] for lookup in form.fields['count'].widget.lookups]
        self.assertIn('empty_true', int_lookups)
        self.assertIn('empty_false', int_lookups)

        # DateField should have empty_true and empty_false
        date_lookups = [lookup[0] for lookup in form.fields['created'].widget.lookups]
        self.assertIn('empty_true', date_lookups)
        self.assertIn('empty_false', date_lookups)

    def test_char_field_includes_extended_lookups(self):
        """CharField should include negation, iexact, and regex lookups."""
        class TestForm(FilterModifierMixin, forms.Form):
            name = forms.CharField(required=False)

        form = TestForm()

        char_lookups = [lookup[0] for lookup in form.fields['name'].widget.lookups]
        self.assertIn('n', char_lookups)  # negation
        self.assertIn('ie', char_lookups)  # iexact
        self.assertIn('regex', char_lookups)  # regex
        self.assertIn('iregex', char_lookups)  # case-insensitive regex

    def test_numeric_fields_include_negation(self):
        """IntegerField and DecimalField should include negation lookup."""
        class TestForm(FilterModifierMixin, forms.Form):
            count = forms.IntegerField(required=False)
            weight = forms.DecimalField(required=False)

        form = TestForm()

        int_lookups = [lookup[0] for lookup in form.fields['count'].widget.lookups]
        self.assertIn('n', int_lookups)

        decimal_lookups = [lookup[0] for lookup in form.fields['weight'].widget.lookups]
        self.assertIn('n', decimal_lookups)

    def test_date_field_includes_negation(self):
        """DateField should include negation lookup."""
        class TestForm(FilterModifierMixin, forms.Form):
            created = forms.DateField(required=False)

        form = TestForm()

        date_lookups = [lookup[0] for lookup in form.fields['created'].widget.lookups]
        self.assertIn('n', date_lookups)


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
