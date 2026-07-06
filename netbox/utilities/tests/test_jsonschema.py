from django import forms
from django.contrib.postgres.forms import SimpleArrayField
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
