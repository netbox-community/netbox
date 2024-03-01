import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status

from core.models import ObjectType
from dcim.filtersets import SiteFilterSet
from dcim.forms import SiteImportForm
from dcim.models import Manufacturer, Rack, Site
from extras.choices import *
from extras.models import CustomField, CustomFieldChoiceSet
from ipam.models import VLAN
from utilities.choices import CSVDelimiterChoices, ImportFormatChoices
from utilities.testing import APITestCase, TestCase
from virtualization.models import VirtualMachine


class CustomFieldTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        Site.objects.bulk_create([
            Site(name='Site A', slug='site-a'),
            Site(name='Site B', slug='site-b'),
            Site(name='Site C', slug='site-c'),
        ])

        cls.object_type = ObjectType.objects.get_for_model(Site)

    def test_invalid_name(self):
        """
        Try creating a CustomField with an invalid name.
        """
        with self.assertRaises(ValidationError):
            # Invalid character
            CustomField(name='?', type=CustomFieldTypeChoices.TYPE_TEXT).full_clean()
        with self.assertRaises(ValidationError):
            # Double underscores not permitted
            CustomField(name='foo__bar', type=CustomFieldTypeChoices.TYPE_TEXT).full_clean()

    def test_text_field(self):
        value = 'Foobar!'

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='text_field',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_longtext_field(self):
        value = 'A' * 256

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='longtext_field',
            type=CustomFieldTypeChoices.TYPE_LONGTEXT,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_integer_field(self):

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='integer_field',
            type=CustomFieldTypeChoices.TYPE_INTEGER,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        for value in (123456, 0, -123456):

            # Assign a value and check that it is saved
            instance.custom_field_data[cf.name] = value
            instance.save()
            instance.refresh_from_db()
            self.assertEqual(instance.custom_field_data[cf.name], value)

            # Delete the stored value and check that it is now null
            instance.custom_field_data.pop(cf.name)
            instance.save()
            instance.refresh_from_db()
            self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_decimal_field(self):

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='decimal_field',
            type=CustomFieldTypeChoices.TYPE_DECIMAL,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        for value in (123456.54, 0, -123456.78):

            # Assign a value and check that it is saved
            instance.custom_field_data[cf.name] = value
            instance.save()
            instance.refresh_from_db()
            self.assertEqual(instance.custom_field_data[cf.name], value)

            # Delete the stored value and check that it is now null
            instance.custom_field_data.pop(cf.name)
            instance.save()
            instance.refresh_from_db()
            self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_boolean_field(self):

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='boolean_field',
            type=CustomFieldTypeChoices.TYPE_INTEGER,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        for value in (True, False):

            # Assign a value and check that it is saved
            instance.custom_field_data[cf.name] = value
            instance.save()
            instance.refresh_from_db()
            self.assertEqual(instance.custom_field_data[cf.name], value)

            # Delete the stored value and check that it is now null
            instance.custom_field_data.pop(cf.name)
            instance.save()
            instance.refresh_from_db()
            self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_date_field(self):
        value = datetime.date(2016, 6, 23)

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='date_field',
            type=CustomFieldTypeChoices.TYPE_DATE,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = cf.serialize(value)
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.cf[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_datetime_field(self):
        value = datetime.datetime(2016, 6, 23, 9, 45, 0)

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='date_field',
            type=CustomFieldTypeChoices.TYPE_DATETIME,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = cf.serialize(value)
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.cf[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_url_field(self):
        value = 'http://example.com/'

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='url_field',
            type=CustomFieldTypeChoices.TYPE_URL,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_json_field(self):
        value = '{"foo": 1, "bar": 2}'

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='json_field',
            type=CustomFieldTypeChoices.TYPE_JSON,
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_select_field(self):
        CHOICES = (
            ('a', 'Option A'),
            ('b', 'Option B'),
            ('c', 'Option C'),
        )
        value = 'a'

        # Create a set of custom field choices
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=CHOICES
        )

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='select_field',
            type=CustomFieldTypeChoices.TYPE_SELECT,
            required=False,
            choice_set=choice_set
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_multiselect_field(self):
        CHOICES = (
            ('a', 'Option A'),
            ('b', 'Option B'),
            ('c', 'Option C'),
        )
        value = ['a', 'b']

        # Create a set of custom field choices
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=CHOICES
        )

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='multiselect_field',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            required=False,
            choice_set=choice_set
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_object_field(self):
        value = VLAN.objects.create(name='VLAN 1', vid=1).pk

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='object_field',
            type=CustomFieldTypeChoices.TYPE_OBJECT,
            object_type=ObjectType.objects.get_for_model(VLAN),
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_multiobject_field(self):
        vlans = (
            VLAN(name='VLAN 1', vid=1),
            VLAN(name='VLAN 2', vid=2),
            VLAN(name='VLAN 3', vid=3),
        )
        VLAN.objects.bulk_create(vlans)
        value = [vlan.pk for vlan in vlans]

        # Create a custom field & check that initial value is null
        cf = CustomField.objects.create(
            name='object_field',
            type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
            object_type=ObjectType.objects.get_for_model(VLAN),
            required=False
        )
        cf.object_types.set([self.object_type])
        instance = Site.objects.first()
        self.assertIsNone(instance.custom_field_data[cf.name])

        # Assign a value and check that it is saved
        instance.custom_field_data[cf.name] = value
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.custom_field_data[cf.name], value)

        # Delete the stored value and check that it is now null
        instance.custom_field_data.pop(cf.name)
        instance.save()
        instance.refresh_from_db()
        self.assertIsNone(instance.custom_field_data.get(cf.name))

    def test_rename_customfield(self):
        obj_type = ObjectType.objects.get_for_model(Site)
        FIELD_DATA = 'abc'

        # Create a custom field
        cf = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='field1')
        cf.save()
        cf.object_types.set([obj_type])

        # Assign custom field data to an object
        site = Site.objects.create(
            name='Site 1',
            slug='site-1',
            custom_field_data={'field1': FIELD_DATA}
        )
        site.refresh_from_db()
        self.assertEqual(site.custom_field_data['field1'], FIELD_DATA)

        # Rename the custom field
        cf.name = 'field2'
        cf.save()

        # Check that custom field data on the object has been updated
        site.refresh_from_db()
        self.assertNotIn('field1', site.custom_field_data)
        self.assertEqual(site.custom_field_data['field2'], FIELD_DATA)

    def test_default_value_validation(self):
        choiceset = CustomFieldChoiceSet.objects.create(
            name="Test Choice Set",
            extra_choices=(
                ('choice1', 'Choice 1'),
                ('choice2', 'Choice 2'),
            )
        )
        site = Site.objects.create(name='Site 1', slug='site-1')
        object_type = ObjectType.objects.get_for_model(Site)

        # Text
        CustomField(name='test', type='text', required=True, default="Default text").full_clean()

        # Integer
        CustomField(name='test', type='integer', required=True, default=1).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='integer', required=True, default='xxx').full_clean()

        # Boolean
        CustomField(name='test', type='boolean', required=True, default=True).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='boolean', required=True, default='xxx').full_clean()

        # Date
        CustomField(name='test', type='date', required=True, default="2023-02-25").full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='date', required=True, default='xxx').full_clean()

        # Datetime
        CustomField(name='test', type='datetime', required=True, default="2023-02-25 02:02:02").full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='datetime', required=True, default='xxx').full_clean()

        # URL
        CustomField(name='test', type='url', required=True, default="https://www.netbox.dev").full_clean()

        # JSON
        CustomField(name='test', type='json', required=True, default='{"test": "object"}').full_clean()

        # Selection
        CustomField(name='test', type='select', required=True, choice_set=choiceset, default='choice1').full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='select', required=True, choice_set=choiceset, default='xxx').full_clean()

        # Multi-select
        CustomField(
            name='test',
            type='multiselect',
            required=True,
            choice_set=choiceset,
            default=['choice1']  # Single default choice
        ).full_clean()
        CustomField(
            name='test',
            type='multiselect',
            required=True,
            choice_set=choiceset,
            default=['choice1', 'choice2']  # Multiple default choices
        ).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(
                name='test',
                type='multiselect',
                required=True,
                choice_set=choiceset,
                default=['xxx']
            ).full_clean()

        # Object
        CustomField(name='test', type='object', required=True, object_type=object_type, default=site.pk).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(name='test', type='object', required=True, object_type=object_type, default="xxx").full_clean()

        # Multi-object
        CustomField(
            name='test',
            type='multiobject',
            required=True,
            object_type=object_type,
            default=[site.pk]
        ).full_clean()
        with self.assertRaises(ValidationError):
            CustomField(
                name='test',
                type='multiobject',
                required=True,
                object_type=object_type,
                default=["xxx"]
            ).full_clean()


class CustomFieldManagerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_type = ObjectType.objects.get_for_model(Site)
        custom_field = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='text_field', default='foo')
        custom_field.save()
        custom_field.object_types.set([object_type])

    def test_get_for_model(self):
        self.assertEqual(CustomField.objects.get_for_model(Site).count(), 1)
        self.assertEqual(CustomField.objects.get_for_model(VirtualMachine).count(), 0)


class CustomFieldAPITest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        object_type = ObjectType.objects.get_for_model(Site)

        # Create some VLANs
        vlans = (
            VLAN(name='VLAN 1', vid=1),
            VLAN(name='VLAN 2', vid=2),
            VLAN(name='VLAN 3', vid=3),
            VLAN(name='VLAN 4', vid=4),
            VLAN(name='VLAN 5', vid=5),
        )
        VLAN.objects.bulk_create(vlans)

        # Create a set of custom field choices
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=(('foo', 'Foo'), ('bar', 'Bar'), ('baz', 'Baz'))
        )

        custom_fields = (
            CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='text_field', default='foo'),
            CustomField(type=CustomFieldTypeChoices.TYPE_LONGTEXT, name='longtext_field', default='ABC'),
            CustomField(type=CustomFieldTypeChoices.TYPE_INTEGER, name='integer_field', default=123),
            CustomField(type=CustomFieldTypeChoices.TYPE_DECIMAL, name='decimal_field', default=123.45),
            CustomField(type=CustomFieldTypeChoices.TYPE_BOOLEAN, name='boolean_field', default=False),
            CustomField(type=CustomFieldTypeChoices.TYPE_DATE, name='date_field', default='2020-01-01'),
            CustomField(type=CustomFieldTypeChoices.TYPE_DATETIME, name='datetime_field', default='2020-01-01T01:23:45'),
            CustomField(type=CustomFieldTypeChoices.TYPE_URL, name='url_field', default='http://example.com/1'),
            CustomField(type=CustomFieldTypeChoices.TYPE_JSON, name='json_field', default='{"x": "y"}'),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_SELECT,
                name='select_field',
                default='foo',
                choice_set=choice_set
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_MULTISELECT,
                name='multiselect_field',
                default=['foo'],
                choice_set=choice_set
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_OBJECT,
                name='object_field',
                object_type=ObjectType.objects.get_for_model(VLAN),
                default=vlans[0].pk,
            ),
            CustomField(
                type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
                name='multiobject_field',
                object_type=ObjectType.objects.get_for_model(VLAN),
                default=[vlans[0].pk, vlans[1].pk],
            ),
        )
        for cf in custom_fields:
            cf.save()
            cf.object_types.set([object_type])

        # Create some sites *after* creating the custom fields. This ensures that
        # default values are not set for the assigned objects.
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        # Assign custom field values for site 2
        sites[1].custom_field_data = {
            custom_fields[0].name: 'bar',
            custom_fields[1].name: 'DEF',
            custom_fields[2].name: 456,
            custom_fields[3].name: Decimal('456.78'),
            custom_fields[4].name: True,
            custom_fields[5].name: '2020-01-02',
            custom_fields[6].name: '2020-01-02 12:00:00',
            custom_fields[7].name: 'http://example.com/2',
            custom_fields[8].name: '{"foo": 1, "bar": 2}',
            custom_fields[9].name: 'bar',
            custom_fields[10].name: ['bar', 'baz'],
            custom_fields[11].name: vlans[1].pk,
            custom_fields[12].name: [vlans[2].pk, vlans[3].pk],
        }
        sites[1].save()

    def test_get_custom_fields(self):
        TYPES = {
            CustomFieldTypeChoices.TYPE_TEXT: 'string',
            CustomFieldTypeChoices.TYPE_LONGTEXT: 'string',
            CustomFieldTypeChoices.TYPE_INTEGER: 'integer',
            CustomFieldTypeChoices.TYPE_DECIMAL: 'decimal',
            CustomFieldTypeChoices.TYPE_BOOLEAN: 'boolean',
            CustomFieldTypeChoices.TYPE_DATE: 'string',
            CustomFieldTypeChoices.TYPE_DATETIME: 'string',
            CustomFieldTypeChoices.TYPE_URL: 'string',
            CustomFieldTypeChoices.TYPE_JSON: 'object',
            CustomFieldTypeChoices.TYPE_SELECT: 'string',
            CustomFieldTypeChoices.TYPE_MULTISELECT: 'array',
            CustomFieldTypeChoices.TYPE_OBJECT: 'object',
            CustomFieldTypeChoices.TYPE_MULTIOBJECT: 'array',
        }

        self.add_permissions('extras.view_customfield')
        url = reverse('extras-api:customfield-list')
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], len(TYPES))

        # Validate data types
        for customfield in response.data['results']:
            cf_type = customfield['type']['value']
            self.assertEqual(customfield['data_type'], TYPES[cf_type])

    def test_get_single_object_without_custom_field_data(self):
        """
        Validate that custom fields are present on an object even if it has no values defined.
        """
        site1 = Site.objects.get(name='Site 1')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site1.pk})
        self.add_permissions('dcim.view_site')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['name'], site1.name)
        self.assertEqual(response.data['custom_fields'], {
            'text_field': None,
            'longtext_field': None,
            'integer_field': None,
            'decimal_field': None,
            'boolean_field': None,
            'date_field': None,
            'datetime_field': None,
            'url_field': None,
            'json_field': None,
            'select_field': None,
            'multiselect_field': None,
            'object_field': None,
            'multiobject_field': None,
        })

    def test_get_single_object_with_custom_field_data(self):
        """
        Validate that custom fields are present and correctly set for an object with values defined.
        """
        site2 = Site.objects.get(name='Site 2')
        site2_cfvs = site2.cf
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.view_site')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['name'], site2.name)
        self.assertEqual(response.data['custom_fields']['text_field'], site2_cfvs['text_field'])
        self.assertEqual(response.data['custom_fields']['longtext_field'], site2_cfvs['longtext_field'])
        self.assertEqual(response.data['custom_fields']['integer_field'], site2_cfvs['integer_field'])
        self.assertEqual(response.data['custom_fields']['decimal_field'], site2_cfvs['decimal_field'])
        self.assertEqual(response.data['custom_fields']['boolean_field'], site2_cfvs['boolean_field'])
        self.assertEqual(response.data['custom_fields']['date_field'], site2_cfvs['date_field'])
        self.assertEqual(response.data['custom_fields']['datetime_field'], site2_cfvs['datetime_field'])
        self.assertEqual(response.data['custom_fields']['url_field'], site2_cfvs['url_field'])
        self.assertEqual(response.data['custom_fields']['json_field'], site2_cfvs['json_field'])
        self.assertEqual(response.data['custom_fields']['select_field'], site2_cfvs['select_field'])
        self.assertEqual(response.data['custom_fields']['multiselect_field'], site2_cfvs['multiselect_field'])
        self.assertEqual(response.data['custom_fields']['object_field']['id'], site2_cfvs['object_field'].pk)
        self.assertEqual(
            [obj['id'] for obj in response.data['custom_fields']['multiobject_field']],
            [obj.pk for obj in site2_cfvs['multiobject_field']]
        )

    def test_create_single_object_with_defaults(self):
        """
        Create a new site with no specified custom field values and check that it received the default values.
        """
        cf_defaults = {
            cf.name: cf.default for cf in CustomField.objects.all()
        }
        data = {
            'name': 'Site 3',
            'slug': 'site-3',
        }
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        # Validate response data
        response_cf = response.data['custom_fields']
        self.assertEqual(response_cf['text_field'], cf_defaults['text_field'])
        self.assertEqual(response_cf['longtext_field'], cf_defaults['longtext_field'])
        self.assertEqual(response_cf['integer_field'], cf_defaults['integer_field'])
        self.assertEqual(response_cf['decimal_field'], cf_defaults['decimal_field'])
        self.assertEqual(response_cf['boolean_field'], cf_defaults['boolean_field'])
        self.assertEqual(response_cf['date_field'].isoformat(), cf_defaults['date_field'])
        self.assertEqual(response_cf['datetime_field'].isoformat(), cf_defaults['datetime_field'])
        self.assertEqual(response_cf['url_field'], cf_defaults['url_field'])
        self.assertEqual(response_cf['json_field'], cf_defaults['json_field'])
        self.assertEqual(response_cf['select_field'], cf_defaults['select_field'])
        self.assertEqual(response_cf['multiselect_field'], cf_defaults['multiselect_field'])
        self.assertEqual(response_cf['object_field']['id'], cf_defaults['object_field'])
        self.assertEqual(
            [obj['id'] for obj in response.data['custom_fields']['multiobject_field']],
            cf_defaults['multiobject_field']
        )

        # Validate database data
        site = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site.custom_field_data['text_field'], cf_defaults['text_field'])
        self.assertEqual(site.custom_field_data['longtext_field'], cf_defaults['longtext_field'])
        self.assertEqual(site.custom_field_data['integer_field'], cf_defaults['integer_field'])
        self.assertEqual(site.custom_field_data['decimal_field'], cf_defaults['decimal_field'])
        self.assertEqual(site.custom_field_data['boolean_field'], cf_defaults['boolean_field'])
        self.assertEqual(site.custom_field_data['date_field'], cf_defaults['date_field'])
        self.assertEqual(site.custom_field_data['datetime_field'], cf_defaults['datetime_field'])
        self.assertEqual(site.custom_field_data['url_field'], cf_defaults['url_field'])
        self.assertEqual(site.custom_field_data['json_field'], cf_defaults['json_field'])
        self.assertEqual(site.custom_field_data['select_field'], cf_defaults['select_field'])
        self.assertEqual(site.custom_field_data['multiselect_field'], cf_defaults['multiselect_field'])
        self.assertEqual(site.custom_field_data['object_field'], cf_defaults['object_field'])
        self.assertEqual(site.custom_field_data['multiobject_field'], cf_defaults['multiobject_field'])

    def test_create_single_object_with_values(self):
        """
        Create a single new site with a value for each type of custom field.
        """
        data = {
            'name': 'Site 3',
            'slug': 'site-3',
            'custom_fields': {
                'text_field': 'bar',
                'longtext_field': 'blah blah blah',
                'integer_field': 456,
                'decimal_field': 456.78,
                'boolean_field': True,
                'date_field': datetime.date(2020, 1, 2),
                'datetime_field': datetime.datetime(2020, 1, 2, 12, 0, 0),
                'url_field': 'http://example.com/2',
                'json_field': '{"foo": 1, "bar": 2}',
                'select_field': 'bar',
                'multiselect_field': ['bar', 'baz'],
                'object_field': VLAN.objects.get(vid=2).pk,
                'multiobject_field': list(VLAN.objects.filter(vid__in=[3, 4]).values_list('pk', flat=True)),
            },
        }
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        # Validate response data
        response_cf = response.data['custom_fields']
        data_cf = data['custom_fields']
        self.assertEqual(response_cf['text_field'], data_cf['text_field'])
        self.assertEqual(response_cf['longtext_field'], data_cf['longtext_field'])
        self.assertEqual(response_cf['integer_field'], data_cf['integer_field'])
        self.assertEqual(response_cf['decimal_field'], data_cf['decimal_field'])
        self.assertEqual(response_cf['boolean_field'], data_cf['boolean_field'])
        self.assertEqual(response_cf['date_field'], data_cf['date_field'])
        self.assertEqual(response_cf['datetime_field'], data_cf['datetime_field'])
        self.assertEqual(response_cf['url_field'], data_cf['url_field'])
        self.assertEqual(response_cf['json_field'], data_cf['json_field'])
        self.assertEqual(response_cf['select_field'], data_cf['select_field'])
        self.assertEqual(response_cf['multiselect_field'], data_cf['multiselect_field'])
        self.assertEqual(response_cf['object_field']['id'], data_cf['object_field'])
        self.assertEqual(
            [obj['id'] for obj in response_cf['multiobject_field']],
            data_cf['multiobject_field']
        )

        # Validate database data
        site = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site.custom_field_data['text_field'], data_cf['text_field'])
        self.assertEqual(site.custom_field_data['longtext_field'], data_cf['longtext_field'])
        self.assertEqual(site.custom_field_data['integer_field'], data_cf['integer_field'])
        self.assertEqual(site.custom_field_data['decimal_field'], data_cf['decimal_field'])
        self.assertEqual(site.custom_field_data['boolean_field'], data_cf['boolean_field'])
        self.assertEqual(site.cf['date_field'], data_cf['date_field'])
        self.assertEqual(site.cf['datetime_field'], data_cf['datetime_field'])
        self.assertEqual(site.custom_field_data['url_field'], data_cf['url_field'])
        self.assertEqual(site.custom_field_data['json_field'], data_cf['json_field'])
        self.assertEqual(site.custom_field_data['select_field'], data_cf['select_field'])
        self.assertEqual(site.custom_field_data['multiselect_field'], data_cf['multiselect_field'])
        self.assertEqual(site.custom_field_data['object_field'], data_cf['object_field'])
        self.assertEqual(site.custom_field_data['multiobject_field'], data_cf['multiobject_field'])

    def test_create_multiple_objects_with_defaults(self):
        """
        Create three new sites with no specified custom field values and check that each received
        the default custom field values.
        """
        cf_defaults = {
            cf.name: cf.default for cf in CustomField.objects.all()
        }
        data = (
            {
                'name': 'Site 3',
                'slug': 'site-3',
            },
            {
                'name': 'Site 4',
                'slug': 'site-4',
            },
            {
                'name': 'Site 5',
                'slug': 'site-5',
            },
        )
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), len(data))

        for i, obj in enumerate(data):

            # Validate response data
            response_cf = response.data[i]['custom_fields']
            self.assertEqual(response_cf['text_field'], cf_defaults['text_field'])
            self.assertEqual(response_cf['longtext_field'], cf_defaults['longtext_field'])
            self.assertEqual(response_cf['integer_field'], cf_defaults['integer_field'])
            self.assertEqual(response_cf['decimal_field'], cf_defaults['decimal_field'])
            self.assertEqual(response_cf['boolean_field'], cf_defaults['boolean_field'])
            self.assertEqual(response_cf['date_field'].isoformat(), cf_defaults['date_field'])
            self.assertEqual(response_cf['datetime_field'].isoformat(), cf_defaults['datetime_field'])
            self.assertEqual(response_cf['url_field'], cf_defaults['url_field'])
            self.assertEqual(response_cf['json_field'], cf_defaults['json_field'])
            self.assertEqual(response_cf['select_field'], cf_defaults['select_field'])
            self.assertEqual(response_cf['multiselect_field'], cf_defaults['multiselect_field'])
            self.assertEqual(response_cf['object_field']['id'], cf_defaults['object_field'])
            self.assertEqual(
                [obj['id'] for obj in response_cf['multiobject_field']],
                cf_defaults['multiobject_field']
            )

            # Validate database data
            site = Site.objects.get(pk=response.data[i]['id'])
            self.assertEqual(site.custom_field_data['text_field'], cf_defaults['text_field'])
            self.assertEqual(site.custom_field_data['longtext_field'], cf_defaults['longtext_field'])
            self.assertEqual(site.custom_field_data['integer_field'], cf_defaults['integer_field'])
            self.assertEqual(site.custom_field_data['decimal_field'], cf_defaults['decimal_field'])
            self.assertEqual(site.custom_field_data['boolean_field'], cf_defaults['boolean_field'])
            self.assertEqual(site.custom_field_data['date_field'], cf_defaults['date_field'])
            self.assertEqual(site.custom_field_data['datetime_field'], cf_defaults['datetime_field'])
            self.assertEqual(site.custom_field_data['url_field'], cf_defaults['url_field'])
            self.assertEqual(site.custom_field_data['json_field'], cf_defaults['json_field'])
            self.assertEqual(site.custom_field_data['select_field'], cf_defaults['select_field'])
            self.assertEqual(site.custom_field_data['multiselect_field'], cf_defaults['multiselect_field'])
            self.assertEqual(site.custom_field_data['object_field'], cf_defaults['object_field'])
            self.assertEqual(site.custom_field_data['multiobject_field'], cf_defaults['multiobject_field'])

    def test_create_multiple_objects_with_values(self):
        """
        Create a three new sites, each with custom fields defined.
        """
        custom_field_data = {
            'text_field': 'bar',
            'longtext_field': 'abcdefghij',
            'integer_field': 456,
            'decimal_field': 456.78,
            'boolean_field': True,
            'date_field': datetime.date(2020, 1, 2),
            'datetime_field': datetime.datetime(2020, 1, 2, 12, 0, 0),
            'url_field': 'http://example.com/2',
            'json_field': '{"foo": 1, "bar": 2}',
            'select_field': 'bar',
            'multiselect_field': ['bar', 'baz'],
            'object_field': VLAN.objects.get(vid=2).pk,
            'multiobject_field': list(VLAN.objects.filter(vid__in=[3, 4]).values_list('pk', flat=True)),
        }
        data = (
            {
                'name': 'Site 3',
                'slug': 'site-3',
                'custom_fields': custom_field_data,
            },
            {
                'name': 'Site 4',
                'slug': 'site-4',
                'custom_fields': custom_field_data,
            },
            {
                'name': 'Site 5',
                'slug': 'site-5',
                'custom_fields': custom_field_data,
            },
        )
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), len(data))

        for i, obj in enumerate(data):

            # Validate response data
            response_cf = response.data[i]['custom_fields']
            self.assertEqual(response_cf['text_field'], custom_field_data['text_field'])
            self.assertEqual(response_cf['longtext_field'], custom_field_data['longtext_field'])
            self.assertEqual(response_cf['integer_field'], custom_field_data['integer_field'])
            self.assertEqual(response_cf['decimal_field'], custom_field_data['decimal_field'])
            self.assertEqual(response_cf['boolean_field'], custom_field_data['boolean_field'])
            self.assertEqual(response_cf['date_field'], custom_field_data['date_field'])
            self.assertEqual(response_cf['datetime_field'], custom_field_data['datetime_field'])
            self.assertEqual(response_cf['url_field'], custom_field_data['url_field'])
            self.assertEqual(response_cf['json_field'], custom_field_data['json_field'])
            self.assertEqual(response_cf['select_field'], custom_field_data['select_field'])
            self.assertEqual(response_cf['multiselect_field'], custom_field_data['multiselect_field'])
            self.assertEqual(response_cf['object_field']['id'], custom_field_data['object_field'])
            self.assertEqual(
                [obj['id'] for obj in response_cf['multiobject_field']],
                custom_field_data['multiobject_field']
            )

            # Validate database data
            site = Site.objects.get(pk=response.data[i]['id'])
            self.assertEqual(site.custom_field_data['text_field'], custom_field_data['text_field'])
            self.assertEqual(site.custom_field_data['longtext_field'], custom_field_data['longtext_field'])
            self.assertEqual(site.custom_field_data['integer_field'], custom_field_data['integer_field'])
            self.assertEqual(site.custom_field_data['decimal_field'], custom_field_data['decimal_field'])
            self.assertEqual(site.custom_field_data['boolean_field'], custom_field_data['boolean_field'])
            self.assertEqual(site.cf['date_field'], custom_field_data['date_field'])
            self.assertEqual(site.cf['datetime_field'], custom_field_data['datetime_field'])
            self.assertEqual(site.custom_field_data['url_field'], custom_field_data['url_field'])
            self.assertEqual(site.custom_field_data['json_field'], custom_field_data['json_field'])
            self.assertEqual(site.custom_field_data['select_field'], custom_field_data['select_field'])
            self.assertEqual(site.custom_field_data['multiselect_field'], custom_field_data['multiselect_field'])
            self.assertEqual(site.custom_field_data['object_field'], custom_field_data['object_field'])
            self.assertEqual(site.custom_field_data['multiobject_field'], custom_field_data['multiobject_field'])

    def test_update_single_object_with_values(self):
        """
        Update an object with existing custom field values. Ensure that only the updated custom field values are
        modified.
        """
        site2 = Site.objects.get(name='Site 2')
        original_cfvs = {**site2.cf}
        data = {
            'custom_fields': {
                'text_field': 'ABCD',
                'integer_field': 1234,
            },
        }
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Validate response data
        response_cf = response.data['custom_fields']
        self.assertEqual(response_cf['text_field'], data['custom_fields']['text_field'])
        self.assertEqual(response_cf['longtext_field'], original_cfvs['longtext_field'])
        self.assertEqual(response_cf['integer_field'], data['custom_fields']['integer_field'])
        self.assertEqual(response_cf['decimal_field'], original_cfvs['decimal_field'])
        self.assertEqual(response_cf['boolean_field'], original_cfvs['boolean_field'])
        self.assertEqual(response_cf['date_field'], original_cfvs['date_field'])
        self.assertEqual(response_cf['datetime_field'], original_cfvs['datetime_field'])
        self.assertEqual(response_cf['url_field'], original_cfvs['url_field'])
        self.assertEqual(response_cf['json_field'], original_cfvs['json_field'])
        self.assertEqual(response_cf['select_field'], original_cfvs['select_field'])
        self.assertEqual(response_cf['multiselect_field'], original_cfvs['multiselect_field'])
        self.assertEqual(response_cf['object_field']['id'], original_cfvs['object_field'].pk)
        self.assertListEqual(
            [obj['id'] for obj in response_cf['multiobject_field']],
            [obj.pk for obj in original_cfvs['multiobject_field']]
        )

        # Validate database data
        site2 = Site.objects.get(pk=site2.pk)
        self.assertEqual(site2.cf['text_field'], data['custom_fields']['text_field'])
        self.assertEqual(site2.cf['longtext_field'], original_cfvs['longtext_field'])
        self.assertEqual(site2.cf['integer_field'], data['custom_fields']['integer_field'])
        self.assertEqual(site2.cf['decimal_field'], original_cfvs['decimal_field'])
        self.assertEqual(site2.cf['boolean_field'], original_cfvs['boolean_field'])
        self.assertEqual(site2.cf['date_field'], original_cfvs['date_field'])
        self.assertEqual(site2.cf['datetime_field'], original_cfvs['datetime_field'])
        self.assertEqual(site2.cf['url_field'], original_cfvs['url_field'])
        self.assertEqual(site2.cf['json_field'], original_cfvs['json_field'])
        self.assertEqual(site2.cf['select_field'], original_cfvs['select_field'])
        self.assertEqual(site2.cf['multiselect_field'], original_cfvs['multiselect_field'])
        self.assertEqual(site2.cf['object_field'], original_cfvs['object_field'])
        self.assertListEqual(
            list(site2.cf['multiobject_field']),
            list(original_cfvs['multiobject_field'])
        )

    def test_specify_related_object_by_attr(self):
        site1 = Site.objects.get(name='Site 1')
        vlans = VLAN.objects.all()[:3]
        url = reverse('dcim-api:site-detail', kwargs={'pk': site1.pk})
        self.add_permissions('dcim.change_site')

        # Set related objects by PK
        data = {
            'custom_fields': {
                'object_field': vlans[0].pk,
                'multiobject_field': [vlans[1].pk, vlans[2].pk],
            },
        }
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(
            response.data['custom_fields']['object_field']['id'],
            vlans[0].pk
        )
        self.assertListEqual(
            [obj['id'] for obj in response.data['custom_fields']['multiobject_field']],
            [vlans[1].pk, vlans[2].pk]
        )

        # Set related objects by name
        data = {
            'custom_fields': {
                'object_field': {
                    'name': vlans[0].name,
                },
                'multiobject_field': [
                    {
                        'name': vlans[1].name
                    },
                    {
                        'name': vlans[2].name
                    },
                ],
            },
        }
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(
            response.data['custom_fields']['object_field']['id'],
            vlans[0].pk
        )
        self.assertListEqual(
            [obj['id'] for obj in response.data['custom_fields']['multiobject_field']],
            [vlans[1].pk, vlans[2].pk]
        )

        # Clear related objects
        data = {
            'custom_fields': {
                'object_field': None,
                'multiobject_field': [],
            },
        }
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIsNone(response.data['custom_fields']['object_field'])
        self.assertListEqual(response.data['custom_fields']['multiobject_field'], [])

    def test_minimum_maximum_values_validation(self):
        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        cf_integer = CustomField.objects.get(name='integer_field')
        cf_integer.validation_minimum = 10
        cf_integer.validation_maximum = 20
        cf_integer.save()

        data = {'custom_fields': {'integer_field': 9}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'integer_field': 21}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'integer_field': 15}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

    def test_regex_validation(self):
        site2 = Site.objects.get(name='Site 2')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site2.pk})
        self.add_permissions('dcim.change_site')

        cf_text = CustomField.objects.get(name='text_field')
        cf_text.validation_regex = r'^[A-Z]{3}$'  # Three uppercase letters
        cf_text.save()

        data = {'custom_fields': {'text_field': 'ABC123'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'text_field': 'abc'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'text_field': 'ABC'}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)


class CustomFieldImportTest(TestCase):
    user_permissions = (
        'dcim.view_site',
        'dcim.add_site',
    )

    @classmethod
    def setUpTestData(cls):

        # Create a set of custom field choices
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=(
                ('a', 'Option A'),
                ('b', 'Option B'),
                ('c', 'Option C'),
            )
        )

        custom_fields = (
            CustomField(name='text', type=CustomFieldTypeChoices.TYPE_TEXT),
            CustomField(name='longtext', type=CustomFieldTypeChoices.TYPE_LONGTEXT),
            CustomField(name='integer', type=CustomFieldTypeChoices.TYPE_INTEGER),
            CustomField(name='decimal', type=CustomFieldTypeChoices.TYPE_DECIMAL),
            CustomField(name='boolean', type=CustomFieldTypeChoices.TYPE_BOOLEAN),
            CustomField(name='date', type=CustomFieldTypeChoices.TYPE_DATE),
            CustomField(name='datetime', type=CustomFieldTypeChoices.TYPE_DATETIME),
            CustomField(name='url', type=CustomFieldTypeChoices.TYPE_URL),
            CustomField(name='json', type=CustomFieldTypeChoices.TYPE_JSON),
            CustomField(name='select', type=CustomFieldTypeChoices.TYPE_SELECT, choice_set=choice_set),
            CustomField(name='multiselect', type=CustomFieldTypeChoices.TYPE_MULTISELECT, choice_set=choice_set),
        )
        for cf in custom_fields:
            cf.save()
            cf.object_types.set([ObjectType.objects.get_for_model(Site)])

    def test_import(self):
        """
        Import a Site in CSV format, including a value for each CustomField.
        """
        data = (
            ('name', 'slug', 'status', 'cf_text', 'cf_longtext', 'cf_integer', 'cf_decimal', 'cf_boolean', 'cf_date', 'cf_datetime', 'cf_url', 'cf_json', 'cf_select', 'cf_multiselect'),
            ('Site 1', 'site-1', 'active', 'ABC', 'Foo', '123', '123.45', 'True', '2020-01-01', '2020-01-01 12:00:00', 'http://example.com/1', '{"foo": 123}', 'a', '"a,b"'),
            ('Site 2', 'site-2', 'active', 'DEF', 'Bar', '456', '456.78', 'False', '2020-01-02', '2020-01-02 12:00:00', 'http://example.com/2', '{"bar": 456}', 'b', '"b,c"'),
            ('Site 3', 'site-3', 'active', '', '', '', '', '', '', '', '', '', '', ''),
        )
        csv_data = '\n'.join(','.join(row) for row in data)

        response = self.client.post(reverse('dcim:site_import'), {
            'data': csv_data,
            'format': ImportFormatChoices.CSV,
            'csv_delimiter': CSVDelimiterChoices.AUTO,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Site.objects.count(), 3)

        # Validate data for site 1
        site1 = Site.objects.get(name='Site 1')
        self.assertEqual(len(site1.custom_field_data), 11)
        self.assertEqual(site1.custom_field_data['text'], 'ABC')
        self.assertEqual(site1.custom_field_data['longtext'], 'Foo')
        self.assertEqual(site1.custom_field_data['integer'], 123)
        self.assertEqual(site1.custom_field_data['decimal'], 123.45)
        self.assertEqual(site1.custom_field_data['boolean'], True)
        self.assertEqual(site1.cf['date'].isoformat(), '2020-01-01')
        self.assertEqual(site1.cf['datetime'].isoformat(), '2020-01-01T12:00:00+00:00')
        self.assertEqual(site1.custom_field_data['url'], 'http://example.com/1')
        self.assertEqual(site1.custom_field_data['json'], {"foo": 123})
        self.assertEqual(site1.custom_field_data['select'], 'a')
        self.assertEqual(site1.custom_field_data['multiselect'], ['a', 'b'])

        # Validate data for site 2
        site2 = Site.objects.get(name='Site 2')
        self.assertEqual(len(site2.custom_field_data), 11)
        self.assertEqual(site2.custom_field_data['text'], 'DEF')
        self.assertEqual(site2.custom_field_data['longtext'], 'Bar')
        self.assertEqual(site2.custom_field_data['integer'], 456)
        self.assertEqual(site2.custom_field_data['decimal'], 456.78)
        self.assertEqual(site2.custom_field_data['boolean'], False)
        self.assertEqual(site2.cf['date'].isoformat(), '2020-01-02')
        self.assertEqual(site2.cf['datetime'].isoformat(), '2020-01-02T12:00:00+00:00')
        self.assertEqual(site2.custom_field_data['url'], 'http://example.com/2')
        self.assertEqual(site2.custom_field_data['json'], {"bar": 456})
        self.assertEqual(site2.custom_field_data['select'], 'b')
        self.assertEqual(site2.custom_field_data['multiselect'], ['b', 'c'])

        # No custom field data should be set for site 3
        site3 = Site.objects.get(name='Site 3')
        self.assertFalse(any(site3.custom_field_data.values()))

    def test_import_missing_required(self):
        """
        Attempt to import an object missing a required custom field.
        """
        # Set one of our CustomFields to required
        CustomField.objects.filter(name='text').update(required=True)

        form_data = {
            'name': 'Site 1',
            'slug': 'site-1',
        }

        form = SiteImportForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cf_text', form.errors)

    def test_import_invalid_choice(self):
        """
        Attempt to import an object with an invalid choice selection.
        """
        form_data = {
            'name': 'Site 1',
            'slug': 'site-1',
            'cf_select': 'Choice X'
        }

        form = SiteImportForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cf_select', form.errors)


class CustomFieldModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cf1 = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='foo')
        cf1.save()
        cf1.object_types.set([ObjectType.objects.get_for_model(Site)])

        cf2 = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='bar')
        cf2.save()
        cf2.object_types.set([ObjectType.objects.get_for_model(Rack)])

    def test_cf_data(self):
        """
        Check that custom field data is present on the instance immediately after being set and after being fetched
        from the database.
        """
        site = Site(name='Test Site', slug='test-site')

        # Check custom field data on new instance
        site.custom_field_data['foo'] = 'abc'
        self.assertEqual(site.cf['foo'], 'abc')

        # Check custom field data from database
        site.save()
        site = Site.objects.get(name='Test Site')
        self.assertEqual(site.cf['foo'], 'abc')

    def test_invalid_data(self):
        """
        Setting custom field data for a non-applicable (or non-existent) CustomField should raise a ValidationError.
        """
        site = Site(name='Test Site', slug='test-site')

        # Set custom field data
        site.custom_field_data['foo'] = 'abc'
        site.custom_field_data['bar'] = 'def'
        with self.assertRaises(ValidationError):
            site.clean()

        del site.custom_field_data['bar']
        site.clean()

    def test_missing_required_field(self):
        """
        Check that a ValidationError is raised if any required custom fields are not present.
        """
        cf3 = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='baz', required=True)
        cf3.save()
        cf3.object_types.set([ObjectType.objects.get_for_model(Site)])

        site = Site(name='Test Site', slug='test-site')

        # Set custom field data with a required field omitted
        site.custom_field_data['foo'] = 'abc'
        with self.assertRaises(ValidationError):
            site.clean()

        site.custom_field_data['baz'] = 'def'
        site.clean()


class CustomFieldModelFilterTest(TestCase):
    queryset = Site.objects.all()
    filterset = SiteFilterSet

    @classmethod
    def setUpTestData(cls):
        object_type = ObjectType.objects.get_for_model(Site)

        manufacturers = Manufacturer.objects.bulk_create((
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
            Manufacturer(name='Manufacturer 4', slug='manufacturer-4'),
        ))

        choice_set = CustomFieldChoiceSet.objects.create(
            name='Custom Field Choice Set 1',
            extra_choices=(('a', 'A'), ('b', 'B'), ('c', 'C'))
        )

        # Integer filtering
        cf = CustomField(name='cf1', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf.save()
        cf.object_types.set([object_type])

        # Decimal filtering
        cf = CustomField(name='cf2', type=CustomFieldTypeChoices.TYPE_DECIMAL)
        cf.save()
        cf.object_types.set([object_type])

        # Boolean filtering
        cf = CustomField(name='cf3', type=CustomFieldTypeChoices.TYPE_BOOLEAN)
        cf.save()
        cf.object_types.set([object_type])

        # Exact text filtering
        cf = CustomField(
            name='cf4',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            filter_logic=CustomFieldFilterLogicChoices.FILTER_EXACT
        )
        cf.save()
        cf.object_types.set([object_type])

        # Loose text filtering
        cf = CustomField(
            name='cf5',
            type=CustomFieldTypeChoices.TYPE_TEXT,
            filter_logic=CustomFieldFilterLogicChoices.FILTER_LOOSE
        )
        cf.save()
        cf.object_types.set([object_type])

        # Date filtering
        cf = CustomField(name='cf6', type=CustomFieldTypeChoices.TYPE_DATE)
        cf.save()
        cf.object_types.set([object_type])

        # Exact URL filtering
        cf = CustomField(
            name='cf7',
            type=CustomFieldTypeChoices.TYPE_URL,
            filter_logic=CustomFieldFilterLogicChoices.FILTER_EXACT
        )
        cf.save()
        cf.object_types.set([object_type])

        # Loose URL filtering
        cf = CustomField(
            name='cf8',
            type=CustomFieldTypeChoices.TYPE_URL,
            filter_logic=CustomFieldFilterLogicChoices.FILTER_LOOSE
        )
        cf.save()
        cf.object_types.set([object_type])

        # Selection filtering
        cf = CustomField(
            name='cf9',
            type=CustomFieldTypeChoices.TYPE_SELECT,
            choice_set=choice_set
        )
        cf.save()
        cf.object_types.set([object_type])

        # Multiselect filtering
        cf = CustomField(
            name='cf10',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            choice_set=choice_set
        )
        cf.save()
        cf.object_types.set([object_type])

        # Object filtering
        cf = CustomField(
            name='cf11',
            type=CustomFieldTypeChoices.TYPE_OBJECT,
            object_type=ObjectType.objects.get_for_model(Manufacturer)
        )
        cf.save()
        cf.object_types.set([object_type])

        # Multi-object filtering
        cf = CustomField(
            name='cf12',
            type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
            object_type=ObjectType.objects.get_for_model(Manufacturer)
        )
        cf.save()
        cf.object_types.set([object_type])

        Site.objects.bulk_create([
            Site(name='Site 1', slug='site-1', custom_field_data={
                'cf1': 100,
                'cf2': 100.1,
                'cf3': True,
                'cf4': 'foo',
                'cf5': 'foo',
                'cf6': '2016-06-26',
                'cf7': 'http://a.example.com',
                'cf8': 'http://a.example.com',
                'cf9': 'A',
                'cf10': ['A', 'B'],
                'cf11': manufacturers[0].pk,
                'cf12': [manufacturers[0].pk, manufacturers[3].pk],
            }),
            Site(name='Site 2', slug='site-2', custom_field_data={
                'cf1': 200,
                'cf2': 200.2,
                'cf3': True,
                'cf4': 'foobar',
                'cf5': 'foobar',
                'cf6': '2016-06-27',
                'cf7': 'http://b.example.com',
                'cf8': 'http://b.example.com',
                'cf9': 'B',
                'cf10': ['B', 'C'],
                'cf11': manufacturers[1].pk,
                'cf12': [manufacturers[1].pk, manufacturers[3].pk],
            }),
            Site(name='Site 3', slug='site-3', custom_field_data={
                'cf1': 300,
                'cf2': 300.3,
                'cf3': False,
                'cf4': 'bar',
                'cf5': 'bar',
                'cf6': '2016-06-28',
                'cf7': 'http://c.example.com',
                'cf8': 'http://c.example.com',
                'cf9': 'C',
                'cf10': None,
                'cf11': manufacturers[2].pk,
                'cf12': [manufacturers[2].pk, manufacturers[3].pk],
            }),
        ])

    def test_filter_integer(self):
        self.assertEqual(self.filterset({'cf_cf1': [100, 200]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf1__n': [200]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf1__gt': [200]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf1__gte': [200]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf1__lt': [200]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf1__lte': [200]}, self.queryset).qs.count(), 2)

    def test_filter_decimal(self):
        self.assertEqual(self.filterset({'cf_cf2': [100.1, 200.2]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf2__n': [200.2]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf2__gt': [200.2]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf2__gte': [200.2]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf2__lt': [200.2]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf2__lte': [200.2]}, self.queryset).qs.count(), 2)

    def test_filter_boolean(self):
        self.assertEqual(self.filterset({'cf_cf3': True}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf3': False}, self.queryset).qs.count(), 1)

    def test_filter_text_strict(self):
        self.assertEqual(self.filterset({'cf_cf4': ['foo']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf4__n': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__ic': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__nic': ['foo']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf4__isw': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__nisw': ['foo']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf4__iew': ['bar']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf4__niew': ['bar']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf4__ie': ['FOO']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf4__nie': ['FOO']}, self.queryset).qs.count(), 2)

    def test_filter_text_loose(self):
        self.assertEqual(self.filterset({'cf_cf5': ['foo']}, self.queryset).qs.count(), 2)

    def test_filter_date(self):
        self.assertEqual(self.filterset({'cf_cf6': ['2016-06-26', '2016-06-27']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf6__n': ['2016-06-27']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf6__gt': ['2016-06-27']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf6__gte': ['2016-06-27']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf6__lt': ['2016-06-27']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf6__lte': ['2016-06-27']}, self.queryset).qs.count(), 2)

    def test_filter_url_strict(self):
        self.assertEqual(self.filterset({'cf_cf7': ['http://a.example.com', 'http://b.example.com']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf7__n': ['http://b.example.com']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf7__ic': ['b']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf7__nic': ['b']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf7__isw': ['http://']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf7__nisw': ['http://']}, self.queryset).qs.count(), 0)
        self.assertEqual(self.filterset({'cf_cf7__iew': ['.com']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf7__niew': ['.com']}, self.queryset).qs.count(), 0)
        self.assertEqual(self.filterset({'cf_cf7__ie': ['HTTP://A.EXAMPLE.COM']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf7__nie': ['HTTP://A.EXAMPLE.COM']}, self.queryset).qs.count(), 2)

    def test_filter_url_loose(self):
        self.assertEqual(self.filterset({'cf_cf8': ['example.com']}, self.queryset).qs.count(), 3)

    def test_filter_select(self):
        self.assertEqual(self.filterset({'cf_cf9': ['A', 'B']}, self.queryset).qs.count(), 2)

    def test_filter_multiselect(self):
        self.assertEqual(self.filterset({'cf_cf10': ['A']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf10': ['A', 'C']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf10': ['null']}, self.queryset).qs.count(), 1)

    def test_filter_object(self):
        manufacturer_ids = Manufacturer.objects.values_list('id', flat=True)
        self.assertEqual(self.filterset({'cf_cf11': [manufacturer_ids[0], manufacturer_ids[1]]}, self.queryset).qs.count(), 2)

    def test_filter_multiobject(self):
        manufacturer_ids = Manufacturer.objects.values_list('id', flat=True)
        self.assertEqual(self.filterset({'cf_cf12': [manufacturer_ids[0], manufacturer_ids[1]]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf12': [manufacturer_ids[3]]}, self.queryset).qs.count(), 3)
