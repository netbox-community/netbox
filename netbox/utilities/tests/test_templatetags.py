import warnings
from unittest.mock import patch

from django import forms
from django.template.loader import render_to_string
from django.test import TestCase, override_settings

from core.models import ObjectType
from dcim.models import Site
from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField, CustomFieldChoiceSet
from utilities.forms.rendering import FieldSet, InlineFields
from utilities.templatetags.builtins.tags import badge, customfield_value, static_with_params
from utilities.templatetags.form_helpers import any_required, render_field_with_aria, render_fieldset
from utilities.templatetags.helpers import _humanize_capacity, humanize_speed


class CustomFieldValueTagTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        object_type = ObjectType.objects.get_for_model(Site)
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Choice Set 1',
            extra_choices=(('a', 'Option A'), ('b', 'Option B')),
            choice_colors={'a': 'red'},
        )

        cls.select_field = CustomField.objects.create(
            name='select_field',
            type=CustomFieldTypeChoices.TYPE_SELECT,
            choice_set=choice_set,
        )
        cls.select_field.object_types.set([object_type])

        cls.multiselect_field = CustomField.objects.create(
            name='multiselect_field',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            choice_set=choice_set,
        )
        cls.multiselect_field.object_types.set([object_type])

        cls.url_field = CustomField.objects.create(
            name='url_field',
            type=CustomFieldTypeChoices.TYPE_URL,
        )
        cls.url_field.object_types.set([object_type])

    def _render(self, customfield, value):
        return render_to_string('builtins/customfield_value.html', customfield_value(customfield, value))

    def test_select_choice_context_includes_color(self):
        context = customfield_value(self.select_field, 'a')

        self.assertEqual(context['value'], 'Option A')
        self.assertEqual(context['color'], 'red')

    def test_multiselect_choice_context_includes_colors(self):
        context = customfield_value(self.multiselect_field, ['a', 'b'])

        self.assertTrue(context['value_has_colors'])
        self.assertEqual(
            context['value'],
            [
                ('Option A', 'red'),
                ('Option B', None),
            ],
        )

    def test_multiselect_choice_context_without_colors_preserves_plain_labels(self):
        context = customfield_value(self.multiselect_field, ['b'])

        self.assertFalse(context['value_has_colors'])
        self.assertEqual(context['value'], ['Option B'])

    def test_url_allowed_scheme_rendered_as_link(self):
        html = self._render(self.url_field, 'https://example.com')
        self.assertInHTML('<a href="https://example.com">https://example.com</a>', html)

    def test_url_disallowed_scheme_not_rendered_as_link(self):
        # A dangerous scheme (e.g. one stored before validation was enforced) must not become a
        # clickable href (fixes #22640).
        html = self._render(self.url_field, 'javascript:alert(1)')
        self.assertNotIn('href', html)
        self.assertIn('javascript:alert(1)', html)


class StaticWithParamsTestCase(TestCase):
    """
    Test the static_with_params template tag functionality.
    """

    def test_static_with_params_basic(self):
        """Test basic parameter appending to static URL."""
        result = static_with_params('test.js', v='1.0.0')
        self.assertIn('test.js', result)
        self.assertIn('v=1.0.0', result)

    @override_settings(STATIC_URL='https://cdn.example.com/static/')
    def test_static_with_params_existing_query_params(self):
        """Test appending parameters to URL that already has query parameters."""
        # Mock the static() function to return a URL with existing query parameters
        with patch('utilities.templatetags.builtins.tags.static') as mock_static:
            mock_static.return_value = 'https://cdn.example.com/static/test.js?existing=param'

            result = static_with_params('test.js', v='1.0.0')

            # Should contain both existing and new parameters
            self.assertIn('existing=param', result)
            self.assertIn('v=1.0.0', result)
            # Should not have double question marks
            self.assertEqual(result.count('?'), 1)

    @override_settings(STATIC_URL='https://cdn.example.com/static/')
    def test_static_with_params_duplicate_parameter_warning(self):
        """Test that a warning is logged when parameters conflict."""
        with patch('utilities.templatetags.builtins.tags.static') as mock_static:
            mock_static.return_value = 'https://cdn.example.com/static/test.js?v=old_version'

            with self.assertLogs('netbox.utilities.templatetags.tags', level='WARNING') as cm:
                result = static_with_params('test.js', v='new_version')

                # Check that warning was logged
                self.assertIn("Parameter 'v' already exists", cm.output[0])

                # Check that new parameter value is used
                self.assertIn('v=new_version', result)
                self.assertNotIn('v=old_version', result)


class BadgeTestCase(TestCase):
    """
    Test the badge template tag functionality.
    """

    def test_badge_with_hex_color_and_url(self):
        html = render_to_string('builtins/badge.html', badge('Role', hex_color='ff0000', url='/dcim/device-roles/1/'))

        self.assertIn('href="/dcim/device-roles/1/"', html)
        self.assertIn('background-color: #ff0000', html)
        self.assertIn('color: #ffffff', html)
        self.assertIn('>Role<', html)


class HumanizeCapacityTestCase(TestCase):
    """
    Test the _humanize_capacity function for correct SI/IEC unit label selection.
    """

    # Tests with divisor=1000 (SI/decimal units)

    def test_si_megabytes(self):
        self.assertEqual(_humanize_capacity(500, divisor=1000), '500 MB')

    def test_si_gigabytes(self):
        self.assertEqual(_humanize_capacity(2000, divisor=1000), '2.00 GB')

    def test_si_terabytes(self):
        self.assertEqual(_humanize_capacity(2000000, divisor=1000), '2.00 TB')

    def test_si_petabytes(self):
        self.assertEqual(_humanize_capacity(2000000000, divisor=1000), '2.00 PB')

    # Tests with divisor=1024 (IEC/binary units)

    def test_iec_megabytes(self):
        self.assertEqual(_humanize_capacity(500, divisor=1024), '500 MiB')

    def test_iec_gigabytes(self):
        self.assertEqual(_humanize_capacity(2048, divisor=1024), '2.00 GiB')

    def test_iec_terabytes(self):
        self.assertEqual(_humanize_capacity(2097152, divisor=1024), '2.00 TiB')

    def test_iec_petabytes(self):
        self.assertEqual(_humanize_capacity(2147483648, divisor=1024), '2.00 PiB')

    # Edge cases

    def test_empty_value(self):
        self.assertEqual(_humanize_capacity(0, divisor=1000), '')
        self.assertEqual(_humanize_capacity(None, divisor=1000), '')

    def test_default_divisor_is_1000(self):
        self.assertEqual(_humanize_capacity(2000), '2.00 GB')


class HumanizeSpeedTestCase(TestCase):
    """
    Test the humanize_speed filter for correct unit selection and decimal formatting.
    """

    # Falsy / empty inputs

    def test_none(self):
        self.assertEqual(humanize_speed(None), '')

    def test_zero(self):
        self.assertEqual(humanize_speed(0), '')

    def test_empty_string(self):
        self.assertEqual(humanize_speed(''), '')

    # Kbps (below 1000)

    def test_kbps(self):
        self.assertEqual(humanize_speed(100), '100 Kbps')

    def test_kbps_low(self):
        self.assertEqual(humanize_speed(1), '1 Kbps')

    # Mbps (1,000 – 999,999)

    def test_mbps_whole(self):
        self.assertEqual(humanize_speed(100_000), '100 Mbps')

    def test_mbps_decimal(self):
        self.assertEqual(humanize_speed(1_544), '1.544 Mbps')

    def test_mbps_10(self):
        self.assertEqual(humanize_speed(10_000), '10 Mbps')

    # Gbps (1,000,000 – 999,999,999)

    def test_gbps_whole(self):
        self.assertEqual(humanize_speed(1_000_000), '1 Gbps')

    def test_gbps_decimal(self):
        self.assertEqual(humanize_speed(2_500_000), '2.5 Gbps')

    def test_gbps_10(self):
        self.assertEqual(humanize_speed(10_000_000), '10 Gbps')

    def test_gbps_25(self):
        self.assertEqual(humanize_speed(25_000_000), '25 Gbps')

    def test_gbps_40(self):
        self.assertEqual(humanize_speed(40_000_000), '40 Gbps')

    def test_gbps_100(self):
        self.assertEqual(humanize_speed(100_000_000), '100 Gbps')

    def test_gbps_400(self):
        self.assertEqual(humanize_speed(400_000_000), '400 Gbps')

    def test_gbps_800(self):
        self.assertEqual(humanize_speed(800_000_000), '800 Gbps')

    # Tbps (1,000,000,000+)

    def test_tbps_whole(self):
        self.assertEqual(humanize_speed(1_000_000_000), '1 Tbps')

    def test_tbps_decimal(self):
        self.assertEqual(humanize_speed(1_600_000_000), '1.6 Tbps')

    # Edge cases

    def test_string_input(self):
        """Ensure string values are cast to int correctly."""
        self.assertEqual(humanize_speed('2500000'), '2.5 Gbps')

    def test_non_round_remainder_preserved(self):
        """Ensure fractional parts with interior zeros are preserved."""
        self.assertEqual(humanize_speed(1_001_000), '1.001 Gbps')

    def test_trailing_zeros_stripped(self):
        """Ensure trailing fractional zeros are stripped (5.500 → 5.5)."""
        self.assertEqual(humanize_speed(5_500_000), '5.5 Gbps')


class RenderFieldWithAriaTestCase(TestCase):
    """
    Test the render_field_with_aria template tag.
    """

    def test_aria_describedby_includes_errors_and_helptext(self):
        class TestForm(forms.Form):
            name = forms.CharField(help_text='Hello', required=True)

        form = TestForm({'name': ''})
        self.assertFalse(form.is_valid())

        html = render_field_with_aria(form['name'])

        self.assertIn('aria-invalid="true"', html)
        self.assertIn('id_name_errors', html)
        self.assertIn('id_name_helptext', html)

    def test_element_id_overrides_widget_id(self):
        class TestForm(forms.Form):
            name = forms.CharField()

        form = TestForm()
        html = render_field_with_aria(form['name'], element_id='custom-id')

        self.assertIn('id="custom-id"', html)
        self.assertNotIn('id="id_name"', html)

    @override_settings(DEBUG=True)
    def test_missing_label_emits_debug_warning(self):
        class TestForm(forms.Form):
            dns_name = forms.CharField(label='')

        form = TestForm()

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            html = render_field_with_aria(form['dns_name'])

        messages = [str(w.message) for w in caught]
        self.assertTrue(
            any('TestForm.dns_name' in m for m in messages),
            f'Expected a warning naming TestForm.dns_name; got: {messages}',
        )
        # No aria-label should be synthesized — an untranslated English fallback
        # would degrade accessibility under non-English locales.
        self.assertNotIn('aria-label', html)


class AnyRequiredTestCase(TestCase):
    """
    Test the any_required template filter.
    """

    class TestForm(forms.Form):
        required_field = forms.CharField(required=True)
        optional_field = forms.CharField(required=False)

    def test_returns_true_when_any_field_required(self):
        form = self.TestForm()
        self.assertTrue(any_required([form['optional_field'], form['required_field']]))

    def test_returns_false_when_no_field_required(self):
        form = self.TestForm()
        self.assertFalse(any_required([form['optional_field']]))

    def test_returns_false_for_empty_list(self):
        self.assertFalse(any_required([]))


class RenderFieldsetInlineRequiredTestCase(TestCase):
    """
    Verify the shared label for an InlineFields row receives the `required`
    CSS class when at least one inline field is required.
    """

    class TestForm(forms.Form):
        required_field = forms.CharField(required=True)
        optional_field = forms.CharField(required=False)
        another_optional = forms.CharField(required=False)

    def _render(self, fieldset):
        context = render_fieldset(self.TestForm(), fieldset)
        return render_to_string('form_helpers/render_fieldset.html', context)

    def test_inline_label_marked_required_when_any_field_required(self):
        fieldset = FieldSet(
            InlineFields('optional_field', 'required_field', label='Combined'),
        )
        html = self._render(fieldset)
        self.assertIn('col-form-label text-lg-end required', html)

    def test_inline_label_not_marked_required_when_no_field_required(self):
        fieldset = FieldSet(
            InlineFields('optional_field', 'another_optional', label='Combined'),
        )
        html = self._render(fieldset)
        self.assertNotIn('col-form-label text-lg-end required', html)
