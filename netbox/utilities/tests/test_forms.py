import warnings
from types import SimpleNamespace

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings

from dcim.models import Site
from netbox.choices import ImportFormatChoices
from utilities.choices import Choice, ChoiceSet
from utilities.forms.bulk_import import BulkImportForm
from utilities.forms.fields import ChoiceField, MultipleChoiceField, TypedChoiceField
from utilities.forms.fields.csv import CSVSelectWidget
from utilities.forms.fields.dynamic import DynamicChoiceField, DynamicMultipleChoiceField
from utilities.forms.fields.generic import GenericObjectChoiceField
from utilities.forms.forms import BulkRenameForm
from utilities.forms.mixins import GenericObjectFormMixin
from utilities.forms.rendering import FieldSet
from utilities.forms.utils import (
    add_blank_choice,
    expand_alphanumeric_pattern,
    expand_ipnetwork_pattern,
    get_capacity_unit_label,
    get_field_value,
)
from utilities.forms.widgets.select import AvailableOptions, HTMXSelect, Select, SelectedOptions


class ExpandIPNetworkTestCase(TestCase):
    """
    Validate the operation of expand_ipnetwork_pattern().
    """
    def test_ipv4_range(self):
        input = '1.2.3.[9-10]/32'
        output = sorted([
            '1.2.3.9/32',
            '1.2.3.10/32',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 4)), output)

    def test_ipv4_set(self):
        input = '1.2.3.[4,44]/32'
        output = sorted([
            '1.2.3.4/32',
            '1.2.3.44/32',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 4)), output)

    def test_ipv4_multiple_ranges(self):
        input = '1.[9-10].3.[9-11]/32'
        output = sorted([
            '1.9.3.9/32',
            '1.9.3.10/32',
            '1.9.3.11/32',
            '1.10.3.9/32',
            '1.10.3.10/32',
            '1.10.3.11/32',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 4)), output)

    def test_ipv4_multiple_sets(self):
        input = '1.[2,22].3.[4,44]/32'
        output = sorted([
            '1.2.3.4/32',
            '1.2.3.44/32',
            '1.22.3.4/32',
            '1.22.3.44/32',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 4)), output)

    def test_ipv4_set_and_range(self):
        input = '1.[2,22].3.[9-11]/32'
        output = sorted([
            '1.2.3.9/32',
            '1.2.3.10/32',
            '1.2.3.11/32',
            '1.22.3.9/32',
            '1.22.3.10/32',
            '1.22.3.11/32',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 4)), output)

    def test_ipv6_range(self):
        input = 'fec::abcd:[9-b]/64'
        output = sorted([
            'fec::abcd:9/64',
            'fec::abcd:a/64',
            'fec::abcd:b/64',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 6)), output)

    def test_ipv6_range_multichar_field(self):
        input = 'fec::abcd:[f-11]/64'
        output = sorted([
            'fec::abcd:f/64',
            'fec::abcd:10/64',
            'fec::abcd:11/64',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 6)), output)

    def test_ipv6_set(self):
        input = 'fec::abcd:[9,ab]/64'
        output = sorted([
            'fec::abcd:9/64',
            'fec::abcd:ab/64',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 6)), output)

    def test_ipv6_multiple_ranges(self):
        input = 'fec::[1-2]bcd:[9-b]/64'
        output = sorted([
            'fec::1bcd:9/64',
            'fec::1bcd:a/64',
            'fec::1bcd:b/64',
            'fec::2bcd:9/64',
            'fec::2bcd:a/64',
            'fec::2bcd:b/64',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 6)), output)

    def test_ipv6_multiple_sets(self):
        input = 'fec::[a,f]bcd:[9,ab]/64'
        output = sorted([
            'fec::abcd:9/64',
            'fec::abcd:ab/64',
            'fec::fbcd:9/64',
            'fec::fbcd:ab/64',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 6)), output)

    def test_ipv6_set_and_range(self):
        input = 'fec::[dead,beaf]:[9-b]/64'
        output = sorted([
            'fec::dead:9/64',
            'fec::dead:a/64',
            'fec::dead:b/64',
            'fec::beaf:9/64',
            'fec::beaf:a/64',
            'fec::beaf:b/64',
        ])

        self.assertEqual(sorted(expand_ipnetwork_pattern(input, 6)), output)

    def test_invalid_address_family(self):
        with self.assertRaisesRegex(Exception, 'Invalid IP address family: 5'):
            sorted(expand_ipnetwork_pattern(None, 5))

    def test_invalid_non_pattern(self):
        with self.assertRaises(ValueError):
            sorted(expand_ipnetwork_pattern('1.2.3.4/32', 4))

    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            sorted(expand_ipnetwork_pattern('1.2.3.[4-]/32', 4))

        with self.assertRaises(ValueError):
            sorted(expand_ipnetwork_pattern('1.2.3.[-4]/32', 4))

        with self.assertRaises(ValueError):
            sorted(expand_ipnetwork_pattern('1.2.3.[4--5]/32', 4))

    def test_invalid_range_bounds(self):
        self.assertEqual(sorted(expand_ipnetwork_pattern('1.2.3.[4-3]/32', 6)), [])

    def test_invalid_set(self):
        with self.assertRaises(ValueError):
            sorted(expand_ipnetwork_pattern('1.2.3.[4]/32', 4))

        with self.assertRaises(ValueError):
            sorted(expand_ipnetwork_pattern('1.2.3.[4,]/32', 4))

        with self.assertRaises(ValueError):
            sorted(expand_ipnetwork_pattern('1.2.3.[,4]/32', 4))

        with self.assertRaises(ValueError):
            sorted(expand_ipnetwork_pattern('1.2.3.[4,,5]/32', 4))


class ExpandAlphanumericTestCase(TestCase):
    """
    Validate the operation of expand_alphanumeric_pattern().
    """
    def test_range_numberic(self):
        input = 'r[9-11]a'
        output = sorted([
            'r9a',
            'r10a',
            'r11a',
        ])

        self.assertEqual(sorted(expand_alphanumeric_pattern(input)), output)

    def test_range_alpha(self):
        input = '[r-t]1a'
        output = sorted([
            'r1a',
            's1a',
            't1a',
        ])

        self.assertEqual(sorted(expand_alphanumeric_pattern(input)), output)

    def test_set_numeric(self):
        input = 'r[1,2]a'
        output = sorted([
            'r1a',
            'r2a',
        ])

        self.assertEqual(sorted(expand_alphanumeric_pattern(input)), output)

    def test_set_alpha(self):
        input = '[r,t]1a'
        output = sorted([
            'r1a',
            't1a',
        ])

        self.assertEqual(sorted(expand_alphanumeric_pattern(input)), output)

    def test_set_multichar(self):
        input = '[ra,tb]1a'
        output = sorted([
            'ra1a',
            'tb1a',
        ])

        self.assertEqual(sorted(expand_alphanumeric_pattern(input)), output)

    def test_multiple_ranges(self):
        input = '[r-t]1[a-b]'
        output = sorted([
            'r1a',
            'r1b',
            's1a',
            's1b',
            't1a',
            't1b',
        ])

        self.assertEqual(sorted(expand_alphanumeric_pattern(input)), output)

    def test_multiple_sets(self):
        input = '[ra,tb]1[ax,by]'
        output = sorted([
            'ra1ax',
            'ra1by',
            'tb1ax',
            'tb1by',
        ])

        self.assertEqual(sorted(expand_alphanumeric_pattern(input)), output)

    def test_set_and_range(self):
        input = '[ra,tb]1[a-c]'
        output = sorted([
            'ra1a',
            'ra1b',
            'ra1c',
            'tb1a',
            'tb1b',
            'tb1c',
        ])

        self.assertEqual(sorted(expand_alphanumeric_pattern(input)), output)

    def test_invalid_non_pattern(self):
        with self.assertRaises(ValueError):
            sorted(expand_alphanumeric_pattern('r9a'))

    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            sorted(expand_alphanumeric_pattern('r[8-]a'))

        with self.assertRaises(ValueError):
            sorted(expand_alphanumeric_pattern('r[-8]a'))

        with self.assertRaises(ValueError):
            sorted(expand_alphanumeric_pattern('r[8--9]a'))

    def test_invalid_range_alphanumeric(self):
        self.assertEqual(sorted(expand_alphanumeric_pattern('r[9-a]a')), [])
        self.assertEqual(sorted(expand_alphanumeric_pattern('r[a-9]a')), [])

    def test_invalid_range_bounds(self):
        with self.assertRaises(forms.ValidationError):
            sorted(expand_alphanumeric_pattern('r[9-8]a'))
            sorted(expand_alphanumeric_pattern('r[b-a]a'))

    def test_invalid_range_len(self):
        with self.assertRaises(forms.ValidationError):
            sorted(expand_alphanumeric_pattern('r[a-bb]a'))

    def test_invalid_set(self):
        with self.assertRaises(ValueError):
            sorted(expand_alphanumeric_pattern('r[a]a'))

        with self.assertRaises(ValueError):
            sorted(expand_alphanumeric_pattern('r[a,]a'))

        with self.assertRaises(ValueError):
            sorted(expand_alphanumeric_pattern('r[,a]a'))

        with self.assertRaises(ValueError):
            sorted(expand_alphanumeric_pattern('r[a,,b]a'))


class ImportFormTestCase(TestCase):

    def test_format_detection(self):
        form = BulkImportForm()

        data = (
            "a,b,c\n"
            "1,2,3\n"
            "4,5,6\n"
        )
        self.assertEqual(form._detect_format(data), ImportFormatChoices.CSV)

        data = '{"a": 1, "b": 2, "c": 3"}'
        self.assertEqual(form._detect_format(data), ImportFormatChoices.JSON)

        data = '[{"a": 1, "b": 2, "c": 3"}, {"a": 4, "b": 5, "c": 6"}]'
        self.assertEqual(form._detect_format(data), ImportFormatChoices.JSON)

        data = (
            "- a: 1\n"
            "  b: 2\n"
            "  c: 3\n"
            "- a: 4\n"
            "  b: 5\n"
            "  c: 6\n"
        )
        self.assertEqual(form._detect_format(data), ImportFormatChoices.YAML)

        data = (
            "---\n"
            "a: 1\n"
            "b: 2\n"
            "c: 3\n"
            "---\n"
            "a: 4\n"
            "b: 5\n"
            "c: 6\n"
        )
        self.assertEqual(form._detect_format(data), ImportFormatChoices.YAML)

        # Invalid data
        with self.assertRaises(forms.ValidationError):
            form._detect_format('')
        with self.assertRaises(forms.ValidationError):
            form._detect_format('?')

    def test_csv_delimiters(self):
        form = BulkImportForm()

        data = (
            "a,b,c\n"
            "1,2,3\n"
            "4,5,6\n"
        )
        self.assertEqual(form._clean_csv(data, delimiter=','), [
            {'a': '1', 'b': '2', 'c': '3'},
            {'a': '4', 'b': '5', 'c': '6'},
        ])

        data = (
            "a;b;c\n"
            "1;2;3\n"
            "4;5;6\n"
        )
        self.assertEqual(form._clean_csv(data, delimiter=';'), [
            {'a': '1', 'b': '2', 'c': '3'},
            {'a': '4', 'b': '5', 'c': '6'},
        ])

        data = (
            "a\tb\tc\n"
            "1\t2\t3\n"
            "4\t5\t6\n"
        )
        self.assertEqual(form._clean_csv(data, delimiter='\t'), [
            {'a': '1', 'b': '2', 'c': '3'},
            {'a': '4', 'b': '5', 'c': '6'},
        ])


class BulkRenameFormTestCase(TestCase):
    def test_no_strip_whitespace(self):
        # Tests to make sure Bulk Rename Form isn't stripping whitespaces
        # See: https://github.com/netbox-community/netbox/issues/13791
        form = BulkRenameForm(data={
            "find": " hello ",
            "replace": " world "
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["find"], " hello ")
        self.assertEqual(form.cleaned_data["replace"], " world ")


class GetFieldValueTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        class TestForm(forms.Form):
            site = forms.ModelChoiceField(
                queryset=Site.objects.all(),
                required=False
            )
        cls.form_class = TestForm

        cls.sites = (
            Site(name='Test Site 1', slug='test-site-1'),
            Site(name='Test Site 2', slug='test-site-2'),
        )
        Site.objects.bulk_create(cls.sites)

    def test_unbound_without_initial(self):
        form = self.form_class()
        self.assertEqual(
            get_field_value(form, 'site'),
            None
        )

    def test_unbound_with_initial(self):
        form = self.form_class(initial={'site': self.sites[0].pk})
        self.assertEqual(
            get_field_value(form, 'site'),
            self.sites[0].pk
        )

    def test_bound_value_without_initial(self):
        form = self.form_class({'site': self.sites[0].pk})
        self.assertEqual(
            get_field_value(form, 'site'),
            self.sites[0].pk
        )

    def test_bound_value_with_initial(self):
        form = self.form_class({'site': self.sites[0].pk}, initial={'site': self.sites[1].pk})
        self.assertEqual(
            get_field_value(form, 'site'),
            self.sites[0].pk
        )

    def test_bound_null_without_initial(self):
        form = self.form_class({'site': None})
        self.assertEqual(
            get_field_value(form, 'site'),
            None
        )

    def test_bound_null_with_initial(self):
        form = self.form_class({'site': None}, initial={'site': self.sites[1].pk})
        self.assertEqual(
            get_field_value(form, 'site'),
            None
        )


class CSVSelectWidgetTestCase(TestCase):
    """
    Validate that CSVSelectWidget treats blank values as omitted.
    This allows model defaults to be applied when CSV fields are present but empty.
    Related to issue #20645.
    """

    def test_blank_value_treated_as_omitted(self):
        """Test that blank string values are treated as omitted"""
        widget = CSVSelectWidget()
        data = {'test_field': ''}
        self.assertTrue(widget.value_omitted_from_data(data, {}, 'test_field'))

    def test_none_value_treated_as_omitted(self):
        """Test that None values are treated as omitted"""
        widget = CSVSelectWidget()
        data = {'test_field': None}
        self.assertTrue(widget.value_omitted_from_data(data, {}, 'test_field'))

    def test_missing_field_treated_as_omitted(self):
        """Test that missing fields are treated as omitted"""
        widget = CSVSelectWidget()
        data = {}
        self.assertTrue(widget.value_omitted_from_data(data, {}, 'test_field'))

    def test_valid_value_not_omitted(self):
        """Test that valid values are not treated as omitted"""
        widget = CSVSelectWidget()
        data = {'test_field': 'valid_value'}
        self.assertFalse(widget.value_omitted_from_data(data, {}, 'test_field'))


class SelectMultipleWidgetTestCase(TestCase):
    """
    Validate filtering behavior of AvailableOptions and SelectedOptions widgets.
    """

    def test_available_options_flat_choices(self):
        """AvailableOptions should exclude selected values from flat choices"""
        widget = AvailableOptions(choices=[
            (1, 'Option 1'),
            (2, 'Option 2'),
            (3, 'Option 3'),
        ])
        widget.optgroups('test', ['2'], None)

        self.assertEqual(len(widget.choices), 2)
        self.assertEqual(widget.choices[0], (1, 'Option 1'))
        self.assertEqual(widget.choices[1], (3, 'Option 3'))

    def test_available_options_optgroups(self):
        """AvailableOptions should exclude selected values from optgroups"""
        widget = AvailableOptions(choices=[
            ('Group A', [(1, 'Option 1'), (2, 'Option 2')]),
            ('Group B', [(3, 'Option 3'), (4, 'Option 4')]),
        ])

        # Select options 2 and 3
        widget.optgroups('test', ['2', '3'], None)

        # Should have 2 groups with filtered choices
        self.assertEqual(len(widget.choices), 2)
        self.assertEqual(widget.choices[0][0], 'Group A')
        self.assertEqual(widget.choices[0][1], [(1, 'Option 1')])
        self.assertEqual(widget.choices[1][0], 'Group B')
        self.assertEqual(widget.choices[1][1], [(4, 'Option 4')])

    def test_selected_options_flat_choices(self):
        """SelectedOptions should include only selected values from flat choices"""
        widget = SelectedOptions(choices=[
            (1, 'Option 1'),
            (2, 'Option 2'),
            (3, 'Option 3'),
        ])

        # Select option 2
        widget.optgroups('test', ['2'], None)

        # Should only have option 2
        self.assertEqual(len(widget.choices), 1)
        self.assertEqual(widget.choices[0], (2, 'Option 2'))

    def test_selected_options_optgroups(self):
        """SelectedOptions should include only selected values from optgroups"""
        widget = SelectedOptions(choices=[
            ('Group A', [(1, 'Option 1'), (2, 'Option 2')]),
            ('Group B', [(3, 'Option 3'), (4, 'Option 4')]),
        ])

        # Select options 2 and 3
        widget.optgroups('test', ['2', '3'], None)

        # Should have 2 groups with only selected choices
        self.assertEqual(len(widget.choices), 2)
        self.assertEqual(widget.choices[0][0], 'Group A')
        self.assertEqual(widget.choices[0][1], [(2, 'Option 2')])
        self.assertEqual(widget.choices[1][0], 'Group B')
        self.assertEqual(widget.choices[1][1], [(3, 'Option 3')])


class DynamicChoiceFieldTestCase(TestCase):
    """
    Validate that DynamicChoiceField.get_bound_field() limits choices to the current
    selection and clears them when nothing is selected.
    """
    CHOICES = [('a', 'Option A'), ('b', 'Option B'), ('c', 'Option C')]

    def _make_form(self, data=None):
        class TestForm(forms.Form):
            field = DynamicChoiceField(choices=self.CHOICES, required=False)
        return TestForm(data=data)

    def test_unbound_clears_choices(self):
        form = self._make_form()
        form.fields['field'].get_bound_field(form, 'field')
        self.assertEqual(form.fields['field'].choices, [])

    def test_bound_with_value_filters_to_selection(self):
        form = self._make_form(data={'field': 'b'})
        form.fields['field'].get_bound_field(form, 'field')
        self.assertEqual(form.fields['field'].choices, [('b', 'Option B')])

    def test_bound_with_no_value_clears_choices(self):
        form = self._make_form(data={})
        form.fields['field'].get_bound_field(form, 'field')
        self.assertEqual(form.fields['field'].choices, [])


class DynamicMultipleChoiceFieldTestCase(TestCase):
    """
    Validate that DynamicMultipleChoiceField.get_bound_field() limits choices to
    the current selection and clears them when nothing is selected.
    """
    CHOICES = [('a', 'Option A'), ('b', 'Option B'), ('c', 'Option C')]

    def _make_form(self, data=None):
        class TestForm(forms.Form):
            field = DynamicMultipleChoiceField(choices=self.CHOICES, required=False)
        return TestForm(data=data)

    def test_unbound_clears_choices(self):
        """Regression test for #22328: unbound form must not retain the full choices list."""
        form = self._make_form()
        form.fields['field'].get_bound_field(form, 'field')
        self.assertEqual(form.fields['field'].choices, [])

    def test_bound_with_values_filters_to_selection(self):
        form = self._make_form(data={'field': ['a', 'c']})
        form.fields['field'].get_bound_field(form, 'field')
        self.assertEqual(form.fields['field'].choices, [('a', 'Option A'), ('c', 'Option C')])

    def test_bound_with_no_values_clears_choices(self):
        form = self._make_form(data={})
        form.fields['field'].get_bound_field(form, 'field')
        self.assertEqual(form.fields['field'].choices, [])


class GenericObjectChoiceFieldTestCase(TestCase):
    """Validate generic foreign key object selection via a content type plus an API-backed object selector."""

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        cls.site_type = ContentType.objects.get_for_model(Site)
        cls.invalid_type = ContentType.objects.get_for_model(ContentType)

    def _make_form(self, data=None, initial=None, required=False):
        site_type = self.site_type

        class TestForm(forms.Form):
            obj = GenericObjectChoiceField(
                content_type_queryset=ContentType.objects.filter(pk=site_type.pk),
                required=required,
                selector=True,
            )

        return TestForm(data=data, initial=initial)

    def test_valid_value_returns_selected_object(self):
        form = self._make_form(
            data={'obj_content_type': str(self.site_type.pk), 'obj_object_id': str(self.site.pk)},
            required=True,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['obj'], self.site)

    def test_optional_empty_value_returns_none(self):
        form = self._make_form(data={'obj_content_type': '', 'obj_object_id': ''})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data['obj'])

    def test_required_empty_value_is_invalid(self):
        form = self._make_form(data={'obj_content_type': '', 'obj_object_id': ''}, required=True)
        self.assertFalse(form.is_valid())
        self.assertIn('obj', form.errors)

    def test_incomplete_value_is_invalid(self):
        for data in (
            {'obj_content_type': str(self.site_type.pk), 'obj_object_id': ''},
            {'obj_content_type': '', 'obj_object_id': str(self.site.pk)},
        ):
            form = self._make_form(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn('obj', form.errors)

    def test_invalid_content_type_is_rejected(self):
        form = self._make_form(
            data={'obj_content_type': str(self.invalid_type.pk), 'obj_object_id': str(self.site.pk)}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('obj', form.errors)

    def test_invalid_object_id_is_rejected(self):
        form = self._make_form(
            data={'obj_content_type': str(self.site_type.pk), 'obj_object_id': str(self.site.pk + 1000)}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('obj', form.errors)

    def test_initial_object_configures_object_selector(self):
        form = self._make_form(initial={'obj': self.site})
        field = form.fields['obj']
        bound_field = field.get_bound_field(form, 'obj')
        self.assertEqual(field.selected_model, Site)
        self.assertEqual(list(field.object_field.queryset), [self.site])
        self.assertEqual(field.object_field.widget.attrs['selector'], Site._meta.label_lower)
        self.assertIn('data-url', field.object_field.widget.attrs)
        self.assertIn('obj_content_type', str(bound_field))
        self.assertIn('obj_object_id', str(bound_field))

    def test_unbound_htmx_rerender_preserves_selection(self):
        # Simulates an HTMX content-type change: the view passes the submitted subwidget values
        # via `initial` (form is unbound). The object selector must reconfigure for the new type.
        form = self._make_form(initial={
            'obj_content_type': str(self.site_type.pk),
            'obj_object_id': str(self.site.pk),
        })
        field = form.fields['obj']
        field.get_bound_field(form, 'obj')
        self.assertEqual(field.selected_model, Site)
        self.assertIn('data-url', field.object_field.widget.attrs)
        self.assertEqual(field.initial, [str(self.site_type.pk), str(self.site.pk)])

    def test_initial_content_type_is_selected_on_render(self):
        # The content-type subwidget must render its options and mark the current type selected on edit forms.
        form = self._make_form(initial={'obj': self.site})
        content_type_html = str(form['obj']).split('name="obj_object_id"')[0]
        self.assertRegex(content_type_html, rf'value="{self.site_type.pk}"\s+selected')

    def test_queryset_property_proxies_object_field(self):
        """The top-level queryset proxy reads and writes the nested object field's queryset."""
        form = self._make_form()
        field = form.fields['obj']
        self.assertIs(field.queryset, field.object_field.queryset)
        field.queryset = Site.objects.all()
        self.assertIs(field.object_field.queryset, field.queryset)
        self.assertEqual(list(field.queryset), list(Site.objects.all()))

    def test_queryset_setter_syncs_rendered_subwidget(self):
        """Assigning queryset (as restrict_form_fields does, pre-render) populates the rendered subwidget."""
        form = self._make_form()
        field = form.fields['obj']
        field.queryset = Site.objects.all()
        self.assertIs(field.object_field.widget, field.widget.widgets[1])
        rendered_values = [getattr(value, 'value', value) for value, label in field.object_field.widget.choices]
        self.assertIn(self.site.pk, rendered_values)

    def test_restricted_queryset_rejects_unviewable_object(self):
        """An object outside the restricted queryset is rejected, mirroring restrict_form_fields()."""
        form = self._make_form(
            data={'obj_content_type': str(self.site_type.pk), 'obj_object_id': str(self.site.pk)},
            required=True,
        )
        # restrict_form_fields() narrows the nested queryset via the top-level proxy before validation.
        form.fields['obj'].queryset = Site.objects.exclude(pk=self.site.pk)
        self.assertFalse(form.is_valid())
        self.assertIn('obj', form.errors)

    def test_restricted_queryset_allows_viewable_object(self):
        """An object within the restricted queryset still validates."""
        form = self._make_form(
            data={'obj_content_type': str(self.site_type.pk), 'obj_object_id': str(self.site.pk)},
            required=True,
        )
        form.fields['obj'].queryset = Site.objects.all()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['obj'], self.site)

    def test_incomplete_value_names_selected_type(self):
        """When a type is chosen but no object, the error names the selected type."""
        form = self._make_form(
            data={'obj_content_type': str(self.site_type.pk), 'obj_object_id': ''},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('Please select a site.', form.errors['obj'])

    def test_content_type_change_clears_stale_object_id(self):
        """The content-type selector clears its paired object_id client-side on change (stale-PK guard)."""
        form = self._make_form(initial={'obj': self.site})
        field = form.fields['obj']
        field.get_bound_field(form, 'obj')
        self.assertEqual(
            field.content_type_field.widget.attrs.get('hx-on::config-request'),
            "event.detail.parameters['obj_object_id'] = ''",
        )

    def test_content_type_lookup_is_cached(self):
        """Repeated content-type resolution hits the database only once per field instance."""
        field = self._make_form().fields['obj']
        with self.assertNumQueries(1):
            first = field._get_content_type(str(self.site_type.pk))
            second = field._get_content_type(str(self.site_type.pk))
        self.assertEqual(first, self.site_type)
        self.assertEqual(second, self.site_type)

    def test_content_type_outside_queryset_returns_none(self):
        """A content type outside the allowed queryset still resolves to None (constraint preserved)."""
        field = self._make_form().fields['obj']
        self.assertIsNone(field._get_content_type(str(self.invalid_type.pk)))

    def test_compress_is_not_implemented(self):
        """compress() is intentionally unreachable and raises to signal clean() owns the conversion."""
        field = self._make_form().fields['obj']
        with self.assertRaises(NotImplementedError):
            field.compress([self.site_type, self.site])


class GenericObjectFormMixinTestCase(TestCase):
    """Validate the DEBUG warning emitted when an HTMX target has no matching FieldSet."""

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Mixin Test Site', slug='mixin-test-site')
        cls.site_type = ContentType.objects.get_for_model(Site)

    def _field(self):
        return GenericObjectChoiceField(
            content_type_queryset=ContentType.objects.filter(pk=self.site_type.pk),
            required=False,
            hx_target_id='scope',
        )

    @override_settings(DEBUG=True)
    def test_missing_htmx_fieldset_warns(self):
        field = self._field()

        class MissingFieldsetForm(GenericObjectFormMixin, forms.Form):
            obj = field

        with self.assertWarns(UserWarning):
            MissingFieldsetForm()

    @override_settings(DEBUG=True)
    def test_present_htmx_fieldset_does_not_warn(self):
        field = self._field()

        class PresentFieldsetForm(GenericObjectFormMixin, forms.Form):
            obj = field
            fieldsets = (FieldSet('obj', name='Scope', html_id='scope'),)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            PresentFieldsetForm()
        self.assertEqual([w for w in caught if 'html_id' in str(w.message)], [])

    def test_gfk_name_routes_assignment(self):
        """When gfk_name differs from the field name, the cleaned object is assigned to that attribute."""
        site_type = self.site_type

        class TargetForm(GenericObjectFormMixin, forms.Form):
            target = GenericObjectChoiceField(
                content_type_queryset=ContentType.objects.filter(pk=site_type.pk),
                required=False,
                gfk_name='assigned_object',
            )

        form = TargetForm(data={'target_content_type': str(site_type.pk), 'target_object_id': str(self.site.pk)})
        form.instance = SimpleNamespace()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.assigned_object, self.site)


class GetCapacityUnitLabelTestCase(TestCase):
    """
    Test the get_capacity_unit_label function for correct base unit label.
    """

    def test_si_label(self):
        self.assertEqual(get_capacity_unit_label(1000), 'MB')

    def test_iec_label(self):
        self.assertEqual(get_capacity_unit_label(1024), 'MiB')


class FieldSetTestCase(TestCase):

    def test_html_id_defaults_to_none(self):
        fs = FieldSet('field1', 'field2', name='Test')
        self.assertIsNone(fs.html_id)

    def test_html_id_stored(self):
        fs = FieldSet('field1', 'field2', name='Test', html_id='my-fieldset')
        self.assertEqual(fs.html_id, 'my-fieldset')

    @override_settings(DEBUG=True)
    def test_html_id_invalid_css_identifier_raises(self):
        with self.assertRaises(ValueError):
            FieldSet('field1', html_id='123-bad')

    @override_settings(DEBUG=False)
    def test_html_id_invalid_css_identifier_ignored_outside_debug(self):
        fs = FieldSet('field1', html_id='123-bad')
        self.assertEqual(fs.html_id, '123-bad')


class HTMXSelectTestCase(TestCase):

    def test_default_targets_form_fields(self):
        widget = HTMXSelect()
        self.assertEqual(widget.attrs['hx-target'], '#form_fields')
        self.assertEqual(widget.attrs['hx-include'], '#form_fields')
        self.assertNotIn('hx-select', widget.attrs)
        self.assertNotIn('hx-swap', widget.attrs)

    def test_hx_target_id_sets_target_select_and_swap(self):
        widget = HTMXSelect(hx_target_id='my-fieldset')
        self.assertEqual(widget.attrs['hx-target'], '#my-fieldset')
        self.assertEqual(widget.attrs['hx-select'], '#my-fieldset')
        self.assertEqual(widget.attrs['hx-swap'], 'outerHTML')

    def test_hx_target_id_include_stays_on_form_fields(self):
        widget = HTMXSelect(hx_target_id='my-fieldset')
        self.assertEqual(widget.attrs['hx-include'], '#form_fields')


class DescriptionSelectTestCase(TestCase):
    """
    Validate the rendering of option descriptions in static select fields.
    """
    class ExampleChoices(ChoiceSet):
        FOO = 'foo'
        BAR = 'bar'
        CHOICES = (
            Choice(FOO, 'Foo', description='Description of foo'),
            Choice(BAR, 'Bar'),
        )

    def test_choiceset_descriptions_populate_widget(self):
        field = ChoiceField(choices=self.ExampleChoices)
        self.assertEqual(field.widget.descriptions, {self.ExampleChoices.FOO: 'Description of foo'})

    def test_multiplechoicefield_descriptions_populate_widget(self):
        field = MultipleChoiceField(choices=self.ExampleChoices)
        self.assertEqual(field.widget.descriptions, {self.ExampleChoices.FOO: 'Description of foo'})

    def test_show_descriptions_false_suppresses_descriptions(self):
        field = ChoiceField(choices=self.ExampleChoices, show_descriptions=False)
        self.assertEqual(field.widget.descriptions, {})

    def test_add_blank_choice_preserves_descriptions(self):
        field = ChoiceField(choices=add_blank_choice(self.ExampleChoices))
        self.assertEqual(field.widget.descriptions, {self.ExampleChoices.FOO: 'Description of foo'})

    def test_data_description_rendered_on_option(self):
        field = ChoiceField(choices=self.ExampleChoices)
        html = field.widget.render('test', None)
        self.assertInHTML(
            '<option value="foo" data-description="Description of foo">Foo</option>',
            html
        )
        # Options without a description should not receive the attribute
        self.assertInHTML('<option value="bar">Bar</option>', html)

    def test_choiceset_without_descriptions(self):
        class NoDescriptions(ChoiceSet):
            CHOICES = (('a', 'A'),)

        field = ChoiceField(choices=NoDescriptions)
        self.assertEqual(field.widget.descriptions, {})

    def test_descriptions_refresh_when_choices_reassigned(self):
        """Reassigning a field's choices after construction should refresh the widget's description map."""
        class OtherChoices(ChoiceSet):
            CHOICES = (
                Choice('baz', 'Baz', description='Description of baz'),
            )

        field = ChoiceField(choices=self.ExampleChoices)
        self.assertEqual(field.widget.descriptions, {self.ExampleChoices.FOO: 'Description of foo'})

        field.choices = OtherChoices
        self.assertEqual(field.widget.descriptions, {'baz': 'Description of baz'})

    def test_show_descriptions_false_suppresses_on_reassignment(self):
        field = ChoiceField(choices=self.ExampleChoices, show_descriptions=False)
        field.choices = self.ExampleChoices
        self.assertEqual(field.widget.descriptions, {})

    def test_typedchoicefield_populates_descriptions(self):
        field = TypedChoiceField(choices=self.ExampleChoices)
        self.assertEqual(field.widget.descriptions, {self.ExampleChoices.FOO: 'Description of foo'})

    def test_typedchoicefield_empty_value_defaults_to_none(self):
        """A blank selection on a TypedChoiceField resolves to None (for storage as NULL) rather than ''."""
        field = TypedChoiceField(choices=add_blank_choice(self.ExampleChoices), required=False)
        self.assertIsNone(field.empty_value)
        self.assertIsNone(field.clean(''))

    def test_explicit_descriptions_mapping(self):
        widget = Select(choices=[('x', 'X'), ('y', 'Y')], descriptions={'x': 'Description X'})
        html = widget.render('test', None)
        self.assertInHTML('<option value="x" data-description="Description X">X</option>', html)
        self.assertInHTML('<option value="y">Y</option>', html)

    def test_choices_setter_delegates_through_mro(self):
        """
        AttrChoiceMixin must delegate to the parent field's choices setter via the MRO, not a hardcoded base,
        so a setter override on an intermediate class is not bypassed.
        """
        from django import forms

        from utilities.forms.fields.choices import AttrChoiceMixin
        from utilities.forms.widgets import Select as DescriptionSelect

        calls = []

        class OverridingChoiceField(forms.ChoiceField):
            def _set_choices(self, value):
                calls.append(value)
                forms.ChoiceField.choices.fset(self, value)
            choices = property(forms.ChoiceField.choices.fget, _set_choices)

        class CustomField(AttrChoiceMixin, OverridingChoiceField):
            widget = DescriptionSelect

        field = CustomField(choices=self.ExampleChoices)
        # The intermediate class's setter must have been invoked (delegation not bypassed)
        self.assertTrue(calls)
        # And descriptions are still collected as normal
        self.assertEqual(field.widget.descriptions, {self.ExampleChoices.FOO: 'Description of foo'})
