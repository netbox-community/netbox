from uuid import UUID

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.test import TestCase

from utilities.jsonschema import JSONSchemaProperty
from utilities.validators import MultipleOfValidator


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
        """An enum suppresses the numeric bounds but retains the multipleOf validator.

        Field.__init__() accepts validators, so a MultipleOfValidator remains applicable to a
        ChoiceField even though min_value and max_value are not.
        """
        prop = JSONSchemaProperty(type='integer', title='Slots', enum=[2, 4], multipleOf=2)

        field = prop.to_form_field('slots')

        self.assertIsInstance(field, forms.ChoiceField)
        self.assertEqual(list(field.choices), [(None, ''), (2, 2), (4, 4)])
        self.assertEqual(len(field.validators), 1)
        self.assertIsInstance(field.validators[0], MultipleOfValidator)

    def test_string_enum_with_min_length_builds_choice_field(self):
        """A string property carrying both an enum and a length bound resolves to a ChoiceField.

        ChoiceField accepts neither min_length nor max_length, so the length bounds must not be
        passed through when an enum is present.
        """
        prop = JSONSchemaProperty(type='string', title='Media', enum=['a', 'bb'], minLength=1)

        field = prop.to_form_field('media')

        self.assertIsInstance(field, forms.ChoiceField)
        self.assertEqual(list(field.choices), [(None, ''), ('a', 'a'), ('bb', 'bb')])

    def test_string_enum_with_max_length_builds_choice_field(self):
        prop = JSONSchemaProperty(type='string', title='Media', enum=['a', 'bb'], maxLength=2)

        field = prop.to_form_field('media')

        self.assertIsInstance(field, forms.ChoiceField)
        self.assertEqual(list(field.choices), [(None, ''), ('a', 'a'), ('bb', 'bb')])

    def test_string_enum_retains_pattern_validator(self):
        """Dropping the length bounds for an enum must not also drop the pattern validator.

        Field.__init__() accepts validators, so a RegexValidator remains applicable to a
        ChoiceField even though min_length and max_length are not.
        """
        prop = JSONSchemaProperty(
            type='string', title='Media', enum=['a', 'bb'], minLength=1, pattern='^[ab]+$'
        )

        field = prop.to_form_field('media')

        self.assertIsInstance(field, forms.ChoiceField)
        self.assertEqual(len(field.validators), 1)
        self.assertIsInstance(field.validators[0], RegexValidator)
        self.assertEqual(field.validators[0].regex.pattern, '^[ab]+$')

    def test_string_bounds_are_applied_without_an_enum(self):
        prop = JSONSchemaProperty(type='string', title='Media', minLength=1, maxLength=4)

        field = prop.to_form_field('media')

        self.assertIsInstance(field, forms.CharField)
        self.assertEqual(field.min_length, 1)
        self.assertEqual(field.max_length, 4)
        with self.assertRaises(ValidationError):
            field.clean('toolong')

    def test_string_format_with_length_bound_builds_format_field(self):
        """A string format resolves to a field class which accepts no length bounds.

        DateField, TimeField and DateTimeField do not subclass CharField, so passing minLength
        or maxLength to one raises TypeError.
        """
        for string_format, expected_class in (
            ('date', forms.DateField),
            ('time', forms.TimeField),
            ('datetime', forms.DateTimeField),
        ):
            with self.subTest(format=string_format):
                prop = JSONSchemaProperty(
                    type='string', title='Timestamp', format=string_format, minLength=10, maxLength=30
                )

                field = prop.to_form_field('timestamp')

                self.assertIsInstance(field, expected_class)

    def test_string_format_retains_pattern_validator(self):
        prop = JSONSchemaProperty(type='string', title='Timestamp', format='date', pattern='^x$')

        field = prop.to_form_field('timestamp')

        self.assertIsInstance(field, forms.DateField)
        self.assertEqual(len(field.validators), 1)
        self.assertIsInstance(field.validators[0], RegexValidator)

    def test_charfield_derived_format_retains_length_bounds(self):
        """EmailField and URLField clean to a string, so the length bounds apply to them."""
        for string_format, expected_class, value in (
            ('email', forms.EmailField, 'user@example.com'),
            ('uri', forms.URLField, 'https://example.com/x'),
        ):
            with self.subTest(format=string_format):
                prop = JSONSchemaProperty(
                    type='string', title='Contact', format=string_format, minLength=5, maxLength=40
                )

                field = prop.to_form_field('contact')

                self.assertIsInstance(field, expected_class)
                self.assertEqual(field.min_length, 5)
                self.assertEqual(field.max_length, 40)
                self.assertEqual(field.clean(value), value)

    def test_uuid_format_omits_length_bounds(self):
        """UUIDField subclasses CharField but cleans to a uuid.UUID, which has no length.

        CharField.__init__() installs a MinLengthValidator and MaxLengthValidator for the bounds,
        and those call len() on the cleaned value, so a UUID raises TypeError at clean time.
        """
        value = '12345678-1234-5678-1234-567812345678'
        prop = JSONSchemaProperty(type='string', title='Serial', format='uuid', minLength=5, maxLength=40)

        field = prop.to_form_field('serial')

        self.assertIsInstance(field, forms.UUIDField)
        self.assertIsNone(field.min_length)
        self.assertIsNone(field.max_length)
        self.assertEqual(field.clean(value), UUID(value))


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
