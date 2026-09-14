from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ValidationError
from django.test import TestCase

from utilities.jsonschema import JSONSchemaProperty


class JSONSchemaPropertyTestCase(TestCase):

    def test_array_enum_uses_multiple_choice_field(self):
        prop = JSONSchemaProperty(
            type='array',
            title='Media',
            items={
                'type': 'string',
                'enum': ['copper', 'sfp', 'qsfp28'],
            },
        )

        field = prop.to_form_field('media')

        self.assertIsInstance(field, forms.MultipleChoiceField)
        self.assertEqual(
            list(field.choices),
            [
                ('copper', 'copper'),
                ('sfp', 'sfp'),
                ('qsfp28', 'qsfp28'),
            ],
        )
        self.assertEqual(field.clean(['copper', 'qsfp28']), ['copper', 'qsfp28'])

    def test_plain_array_uses_simple_array_field(self):
        prop = JSONSchemaProperty(
            type='array',
            title='Ports',
            items={
                'type': 'string',
            },
        )

        field = prop.to_form_field('ports')

        self.assertIsInstance(field, SimpleArrayField)
        self.assertIsInstance(field.base_field, forms.CharField)
        self.assertEqual(field.clean('ge-0/0/0,ge-0/0/1'), ['ge-0/0/0', 'ge-0/0/1'])

    def test_zero_minimum_is_applied_to_form_field(self):
        prop = JSONSchemaProperty(type='number', title='Offset', minimum=0)

        field = prop.to_form_field('offset')

        self.assertEqual(field.min_value, 0)
        with self.assertRaises(ValidationError):
            field.clean(-5)
        self.assertEqual(field.clean(0), 0)

    def test_zero_maximum_is_applied_to_form_field(self):
        prop = JSONSchemaProperty(type='number', title='Offset', maximum=0)

        field = prop.to_form_field('offset')

        self.assertEqual(field.max_value, 0)
        with self.assertRaises(ValidationError):
            field.clean(5)
        self.assertEqual(field.clean(0), 0)

    def test_zero_bounds_are_applied_to_integer_form_field(self):
        prop = JSONSchemaProperty(type='integer', title='Slots', minimum=0, maximum=0)

        field = prop.to_form_field('slots')

        self.assertEqual(field.min_value, 0)
        self.assertEqual(field.max_value, 0)
        with self.assertRaises(ValidationError):
            field.clean(-1)
        with self.assertRaises(ValidationError):
            field.clean(1)
        self.assertEqual(field.clean(0), 0)

    def test_nonzero_bounds_are_applied_to_form_field(self):
        prop = JSONSchemaProperty(type='number', title='Offset', minimum=1, maximum=10)

        field = prop.to_form_field('offset')

        self.assertEqual(field.min_value, 1)
        self.assertEqual(field.max_value, 10)
        with self.assertRaises(ValidationError):
            field.clean(0)
        with self.assertRaises(ValidationError):
            field.clean(11)

    def test_omitted_bounds_are_not_applied_to_form_field(self):
        prop = JSONSchemaProperty(type='number', title='Offset')

        field = prop.to_form_field('offset')

        self.assertIsNone(field.min_value)
        self.assertIsNone(field.max_value)
        self.assertEqual(field.clean(-100), -100)

    def test_numeric_enum_with_zero_bound_builds_choice_field(self):
        """A numeric property carrying both an enum and a zero bound resolves to a ChoiceField.

        ChoiceField accepts neither min_value nor max_value, so the numeric bounds must not be
        passed through when an enum is present.
        """
        prop = JSONSchemaProperty(type='integer', title='Slots', enum=[0, 1, 2], minimum=0)

        field = prop.to_form_field('slots')

        self.assertIsInstance(field, forms.ChoiceField)
        self.assertEqual(list(field.choices), [(None, ''), (0, 0), (1, 1), (2, 2)])

    def test_numeric_enum_with_nonzero_bound_builds_choice_field(self):
        prop = JSONSchemaProperty(type='integer', title='Slots', enum=[1, 2], minimum=1, maximum=2)

        field = prop.to_form_field('slots')

        self.assertIsInstance(field, forms.ChoiceField)
        self.assertEqual(list(field.choices), [(None, ''), (1, 1), (2, 2)])

    def test_numeric_enum_with_multiple_of_builds_choice_field(self):
        prop = JSONSchemaProperty(type='integer', title='Slots', enum=[2, 4], multipleOf=2)

        field = prop.to_form_field('slots')

        self.assertIsInstance(field, forms.ChoiceField)
        self.assertEqual(list(field.choices), [(None, ''), (2, 2), (4, 4)])


class JSONSchemaPropertyDescriptionSanitizationTestCase(TestCase):
    """
    A property's description becomes the form field's help_text, which is rendered through the
    `safe` filter in form_helpers/render_field.html. It is passed through render_markdown(), which
    applies the HTML_ALLOWED_TAGS allowlist, matching the custom field path in
    extras.models.customfields.CustomField.to_form_field().

    Each test compares the entire help text, so a payload surviving anywhere in it fails the
    assertion. Asserting only on the absence of a substring would not, because stripping an
    element leaves its text behind as character data.
    """

    def test_disallowed_element_is_stripped(self):
        prop = JSONSchemaProperty(
            type='integer',
            title='Capacity (GB)',
            description='Gross disk size <iframe src="https://example.com"></iframe>',
        )

        field = prop.to_form_field('capacity')

        self.assertHTMLEqual(
            '<div class="rendered-markdown"><p>Gross disk size</p></div>',
            field.help_text,
        )

    def test_script_element_is_stripped(self):
        prop = JSONSchemaProperty(
            type='string',
            description='Vendor code <script>alert(1)</script>',
        )

        field = prop.to_form_field('vendor_code')

        self.assertHTMLEqual(
            '<div class="rendered-markdown"><p>Vendor code</p></div>',
            field.help_text,
        )

    def test_event_handler_attribute_is_stripped(self):
        """An allowed tag carrying a disallowed attribute keeps the tag but loses the attribute."""
        prop = JSONSchemaProperty(
            type='string',
            description='<b onmouseover="alert(1)">Vendor code</b>',
        )

        field = prop.to_form_field('vendor_code')

        self.assertHTMLEqual(
            '<div class="rendered-markdown"><p><b>Vendor code</b></p></div>',
            field.help_text,
        )

    def test_javascript_uri_is_stripped(self):
        prop = JSONSchemaProperty(
            type='string',
            description='<a href="javascript:alert(1)">Vendor code</a>',
        )

        field = prop.to_form_field('vendor_code')

        self.assertHTMLEqual(
            '<div class="rendered-markdown">'
            '<p><a rel="noopener noreferrer">Vendor code</a></p></div>',
            field.help_text,
        )

    def test_disallowed_element_is_stripped_from_mixed_markup(self):
        """A disallowed element is dropped while its allowed siblings are kept."""
        prop = JSONSchemaProperty(
            type='string',
            description='<b>Vendor</b> code <iframe src="https://example.com"></iframe>',
        )

        field = prop.to_form_field('vendor_code')

        self.assertHTMLEqual(
            '<div class="rendered-markdown"><p><b>Vendor</b> code</p></div>',
            field.help_text,
        )

    def test_allowed_markup_is_preserved(self):
        """
        render_markdown() applies the HTML_ALLOWED_TAGS allowlist, so markup inside it survives.
        This is the behavior that keeps schema descriptions consistent with custom field
        descriptions.
        """
        prop = JSONSchemaProperty(
            type='integer',
            description='Gross disk size in <code>GB</code>',
        )

        field = prop.to_form_field('capacity')

        self.assertHTMLEqual(
            '<div class="rendered-markdown"><p>Gross disk size in <code>GB</code></p></div>',
            field.help_text,
        )

    def test_markdown_is_rendered(self):
        """Descriptions are interpreted as Markdown, matching the custom field path."""
        prop = JSONSchemaProperty(
            type='integer',
            description='Gross disk size in **GB**',
        )

        field = prop.to_form_field('capacity')

        self.assertHTMLEqual(
            '<div class="rendered-markdown">'
            '<p>Gross disk size in <strong>GB</strong></p></div>',
            field.help_text,
        )

    def test_description_text_is_retained(self):
        """Sanitization must not discard the author's actual help text."""
        prop = JSONSchemaProperty(
            type='string',
            description='Gross disk size in gigabytes',
        )

        field = prop.to_form_field('capacity')

        self.assertHTMLEqual(
            '<div class="rendered-markdown"><p>Gross disk size in gigabytes</p></div>',
            field.help_text,
        )

    def test_absent_description_yields_no_help_text(self):
        """A property without a description must not gain help text from the sanitizer."""
        prop = JSONSchemaProperty(type='string', title='Vendor Code')

        field = prop.to_form_field('vendor_code')

        self.assertFalse(field.help_text)
