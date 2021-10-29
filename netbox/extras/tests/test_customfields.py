from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status

from dcim.filtersets import SiteFilterSet
from dcim.forms import SiteCSVForm
from dcim.models import Site, Rack
from extras.choices import *
from extras.models import CustomField
from utilities.testing import APITestCase, TestCase
from virtualization.models import VirtualMachine


class CustomFieldTest(TestCase):

    def setUp(self):

        Site.objects.bulk_create([
            Site(name='Site A', slug='site-a'),
            Site(name='Site B', slug='site-b'),
            Site(name='Site C', slug='site-c'),
        ])

    def test_simple_fields(self):
        DATA = (
            {
                'field_type': CustomFieldTypeChoices.TYPE_TEXT,
                'field_value': 'Foobar!',
                'empty_value': '',
            },
            {
                'field_type': CustomFieldTypeChoices.TYPE_LONGTEXT,
                'field_value': 'Text with **Markdown**',
                'empty_value': '',
            },
            {
                'field_type': CustomFieldTypeChoices.TYPE_INTEGER,
                'field_value': 0,
                'empty_value': None,
            },
            {
                'field_type': CustomFieldTypeChoices.TYPE_INTEGER,
                'field_value': 42,
                'empty_value': None,
            },
            {
                'field_type': CustomFieldTypeChoices.TYPE_BOOLEAN,
                'field_value': True,
                'empty_value': None,
            },
            {
                'field_type': CustomFieldTypeChoices.TYPE_BOOLEAN,
                'field_value': False,
                'empty_value': None,
            },
            {
                'field_type': CustomFieldTypeChoices.TYPE_DATE,
                'field_value': '2016-06-23',
                'empty_value': None,
            },
            {
                'field_type': CustomFieldTypeChoices.TYPE_URL,
                'field_value': 'http://example.com/',
                'empty_value': '',
            },
            {
                'field_type': CustomFieldTypeChoices.TYPE_JSON,
                'field_value': '{"foo": 1, "bar": 2}',
                'empty_value': 'null',
            },
        )

        obj_type = ContentType.objects.get_for_model(Site)

        for data in DATA:

            # Create a custom field
            cf = CustomField(type=data['field_type'], name='my_field', required=False)
            cf.save()
            cf.content_types.set([obj_type])

            # Check that the field has a null initial value
            site = Site.objects.first()
            self.assertIsNone(site.custom_field_data[cf.name])

            # Assign a value to the first Site
            site.custom_field_data[cf.name] = data['field_value']
            site.save()

            # Retrieve the stored value
            site.refresh_from_db()
            self.assertEqual(site.custom_field_data[cf.name], data['field_value'])

            # Delete the stored value
            site.custom_field_data.pop(cf.name)
            site.save()
            site.refresh_from_db()
            self.assertIsNone(site.custom_field_data.get(cf.name))

            # Delete the custom field
            cf.delete()

    def test_select_field(self):
        obj_type = ContentType.objects.get_for_model(Site)

        # Create a custom field
        cf = CustomField(
            type=CustomFieldTypeChoices.TYPE_SELECT,
            name='my_field',
            required=False,
            choices=['Option A', 'Option B', 'Option C']
        )
        cf.save()
        cf.content_types.set([obj_type])

        # Check that the field has a null initial value
        site = Site.objects.first()
        self.assertIsNone(site.custom_field_data[cf.name])

        # Assign a value to the first Site
        site.custom_field_data[cf.name] = 'Option A'
        site.save()

        # Retrieve the stored value
        site.refresh_from_db()
        self.assertEqual(site.custom_field_data[cf.name], 'Option A')

        # Delete the stored value
        site.custom_field_data.pop(cf.name)
        site.save()
        site.refresh_from_db()
        self.assertIsNone(site.custom_field_data.get(cf.name))

        # Delete the custom field
        cf.delete()

    def test_rename_customfield(self):
        obj_type = ContentType.objects.get_for_model(Site)
        FIELD_DATA = 'abc'

        # Create a custom field
        cf = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='field1')
        cf.save()
        cf.content_types.set([obj_type])

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


class CustomFieldManagerTest(TestCase):

    def setUp(self):
        content_type = ContentType.objects.get_for_model(Site)
        custom_field = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='text_field', default='foo')
        custom_field.save()
        custom_field.content_types.set([content_type])

    def test_get_for_model(self):
        self.assertEqual(CustomField.objects.get_for_model(Site).count(), 1)
        self.assertEqual(CustomField.objects.get_for_model(VirtualMachine).count(), 0)


class CustomFieldAPITest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        content_type = ContentType.objects.get_for_model(Site)

        # Text custom field
        cls.cf_text = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='text_field', default='foo')
        cls.cf_text.save()
        cls.cf_text.content_types.set([content_type])

        # Long text custom field
        cls.cf_longtext = CustomField(type=CustomFieldTypeChoices.TYPE_LONGTEXT, name='longtext_field', default='ABC')
        cls.cf_longtext.save()
        cls.cf_longtext.content_types.set([content_type])

        # Integer custom field
        cls.cf_integer = CustomField(type=CustomFieldTypeChoices.TYPE_INTEGER, name='number_field', default=123)
        cls.cf_integer.save()
        cls.cf_integer.content_types.set([content_type])

        # Boolean custom field
        cls.cf_boolean = CustomField(type=CustomFieldTypeChoices.TYPE_BOOLEAN, name='boolean_field', default=False)
        cls.cf_boolean.save()
        cls.cf_boolean.content_types.set([content_type])

        # Date custom field
        cls.cf_date = CustomField(type=CustomFieldTypeChoices.TYPE_DATE, name='date_field', default='2020-01-01')
        cls.cf_date.save()
        cls.cf_date.content_types.set([content_type])

        # URL custom field
        cls.cf_url = CustomField(type=CustomFieldTypeChoices.TYPE_URL, name='url_field', default='http://example.com/1')
        cls.cf_url.save()
        cls.cf_url.content_types.set([content_type])

        # JSON custom field
        cls.cf_json = CustomField(type=CustomFieldTypeChoices.TYPE_JSON, name='json_field', default='{"x": "y"}')
        cls.cf_json.save()
        cls.cf_json.content_types.set([content_type])

        # Select custom field
        cls.cf_select = CustomField(type=CustomFieldTypeChoices.TYPE_SELECT, name='choice_field', choices=['Foo', 'Bar', 'Baz'])
        cls.cf_select.default = 'Foo'
        cls.cf_select.save()
        cls.cf_select.content_types.set([content_type])

        # Create some sites
        cls.sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(cls.sites)

        # Assign custom field values for site 2
        cls.sites[1].custom_field_data = {
            cls.cf_text.name: 'bar',
            cls.cf_longtext.name: 'DEF',
            cls.cf_integer.name: 456,
            cls.cf_boolean.name: True,
            cls.cf_date.name: '2020-01-02',
            cls.cf_url.name: 'http://example.com/2',
            cls.cf_json.name: '{"foo": 1, "bar": 2}',
            cls.cf_select.name: 'Bar',
        }
        cls.sites[1].save()

    def test_get_single_object_without_custom_field_data(self):
        """
        Validate that custom fields are present on an object even if it has no values defined.
        """
        url = reverse('dcim-api:site-detail', kwargs={'pk': self.sites[0].pk})
        self.add_permissions('dcim.view_site')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['name'], self.sites[0].name)
        self.assertEqual(response.data['custom_fields'], {
            'text_field': None,
            'longtext_field': None,
            'number_field': None,
            'boolean_field': None,
            'date_field': None,
            'url_field': None,
            'json_field': None,
            'choice_field': None,
        })

    def test_get_single_object_with_custom_field_data(self):
        """
        Validate that custom fields are present and correctly set for an object with values defined.
        """
        site2_cfvs = self.sites[1].custom_field_data
        url = reverse('dcim-api:site-detail', kwargs={'pk': self.sites[1].pk})
        self.add_permissions('dcim.view_site')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['name'], self.sites[1].name)
        self.assertEqual(response.data['custom_fields']['text_field'], site2_cfvs['text_field'])
        self.assertEqual(response.data['custom_fields']['longtext_field'], site2_cfvs['longtext_field'])
        self.assertEqual(response.data['custom_fields']['number_field'], site2_cfvs['number_field'])
        self.assertEqual(response.data['custom_fields']['boolean_field'], site2_cfvs['boolean_field'])
        self.assertEqual(response.data['custom_fields']['date_field'], site2_cfvs['date_field'])
        self.assertEqual(response.data['custom_fields']['url_field'], site2_cfvs['url_field'])
        self.assertEqual(response.data['custom_fields']['json_field'], site2_cfvs['json_field'])
        self.assertEqual(response.data['custom_fields']['choice_field'], site2_cfvs['choice_field'])

    def test_create_single_object_with_defaults(self):
        """
        Create a new site with no specified custom field values and check that it received the default values.
        """
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
        self.assertEqual(response_cf['text_field'], self.cf_text.default)
        self.assertEqual(response_cf['longtext_field'], self.cf_longtext.default)
        self.assertEqual(response_cf['number_field'], self.cf_integer.default)
        self.assertEqual(response_cf['boolean_field'], self.cf_boolean.default)
        self.assertEqual(response_cf['date_field'], self.cf_date.default)
        self.assertEqual(response_cf['url_field'], self.cf_url.default)
        self.assertEqual(response_cf['json_field'], self.cf_json.default)
        self.assertEqual(response_cf['choice_field'], self.cf_select.default)

        # Validate database data
        site = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site.custom_field_data['text_field'], self.cf_text.default)
        self.assertEqual(site.custom_field_data['longtext_field'], self.cf_longtext.default)
        self.assertEqual(site.custom_field_data['number_field'], self.cf_integer.default)
        self.assertEqual(site.custom_field_data['boolean_field'], self.cf_boolean.default)
        self.assertEqual(str(site.custom_field_data['date_field']), self.cf_date.default)
        self.assertEqual(site.custom_field_data['url_field'], self.cf_url.default)
        self.assertEqual(site.custom_field_data['json_field'], self.cf_json.default)
        self.assertEqual(site.custom_field_data['choice_field'], self.cf_select.default)

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
                'number_field': 456,
                'boolean_field': True,
                'date_field': '2020-01-02',
                'url_field': 'http://example.com/2',
                'json_field': '{"foo": 1, "bar": 2}',
                'choice_field': 'Bar',
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
        self.assertEqual(response_cf['number_field'], data_cf['number_field'])
        self.assertEqual(response_cf['boolean_field'], data_cf['boolean_field'])
        self.assertEqual(response_cf['date_field'], data_cf['date_field'])
        self.assertEqual(response_cf['url_field'], data_cf['url_field'])
        self.assertEqual(response_cf['json_field'], data_cf['json_field'])
        self.assertEqual(response_cf['choice_field'], data_cf['choice_field'])

        # Validate database data
        site = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site.custom_field_data['text_field'], data_cf['text_field'])
        self.assertEqual(site.custom_field_data['longtext_field'], data_cf['longtext_field'])
        self.assertEqual(site.custom_field_data['number_field'], data_cf['number_field'])
        self.assertEqual(site.custom_field_data['boolean_field'], data_cf['boolean_field'])
        self.assertEqual(str(site.custom_field_data['date_field']), data_cf['date_field'])
        self.assertEqual(site.custom_field_data['url_field'], data_cf['url_field'])
        self.assertEqual(site.custom_field_data['json_field'], data_cf['json_field'])
        self.assertEqual(site.custom_field_data['choice_field'], data_cf['choice_field'])

    def test_create_multiple_objects_with_defaults(self):
        """
        Create three news sites with no specified custom field values and check that each received
        the default custom field values.
        """
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
            self.assertEqual(response_cf['text_field'], self.cf_text.default)
            self.assertEqual(response_cf['longtext_field'], self.cf_longtext.default)
            self.assertEqual(response_cf['number_field'], self.cf_integer.default)
            self.assertEqual(response_cf['boolean_field'], self.cf_boolean.default)
            self.assertEqual(response_cf['date_field'], self.cf_date.default)
            self.assertEqual(response_cf['url_field'], self.cf_url.default)
            self.assertEqual(response_cf['json_field'], self.cf_json.default)
            self.assertEqual(response_cf['choice_field'], self.cf_select.default)

            # Validate database data
            site = Site.objects.get(pk=response.data[i]['id'])
            self.assertEqual(site.custom_field_data['text_field'], self.cf_text.default)
            self.assertEqual(site.custom_field_data['longtext_field'], self.cf_longtext.default)
            self.assertEqual(site.custom_field_data['number_field'], self.cf_integer.default)
            self.assertEqual(site.custom_field_data['boolean_field'], self.cf_boolean.default)
            self.assertEqual(str(site.custom_field_data['date_field']), self.cf_date.default)
            self.assertEqual(site.custom_field_data['url_field'], self.cf_url.default)
            self.assertEqual(site.custom_field_data['json_field'], self.cf_json.default)
            self.assertEqual(site.custom_field_data['choice_field'], self.cf_select.default)

    def test_create_multiple_objects_with_values(self):
        """
        Create a three new sites, each with custom fields defined.
        """
        custom_field_data = {
            'text_field': 'bar',
            'longtext_field': 'abcdefghij',
            'number_field': 456,
            'boolean_field': True,
            'date_field': '2020-01-02',
            'url_field': 'http://example.com/2',
            'json_field': '{"foo": 1, "bar": 2}',
            'choice_field': 'Bar',
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
            self.assertEqual(response_cf['number_field'], custom_field_data['number_field'])
            self.assertEqual(response_cf['boolean_field'], custom_field_data['boolean_field'])
            self.assertEqual(response_cf['date_field'], custom_field_data['date_field'])
            self.assertEqual(response_cf['url_field'], custom_field_data['url_field'])
            self.assertEqual(response_cf['json_field'], custom_field_data['json_field'])
            self.assertEqual(response_cf['choice_field'], custom_field_data['choice_field'])

            # Validate database data
            site = Site.objects.get(pk=response.data[i]['id'])
            self.assertEqual(site.custom_field_data['text_field'], custom_field_data['text_field'])
            self.assertEqual(site.custom_field_data['longtext_field'], custom_field_data['longtext_field'])
            self.assertEqual(site.custom_field_data['number_field'], custom_field_data['number_field'])
            self.assertEqual(site.custom_field_data['boolean_field'], custom_field_data['boolean_field'])
            self.assertEqual(str(site.custom_field_data['date_field']), custom_field_data['date_field'])
            self.assertEqual(site.custom_field_data['url_field'], custom_field_data['url_field'])
            self.assertEqual(site.custom_field_data['json_field'], custom_field_data['json_field'])
            self.assertEqual(site.custom_field_data['choice_field'], custom_field_data['choice_field'])

    def test_update_single_object_with_values(self):
        """
        Update an object with existing custom field values. Ensure that only the updated custom field values are
        modified.
        """
        site = self.sites[1]
        original_cfvs = {**site.custom_field_data}
        data = {
            'custom_fields': {
                'text_field': 'ABCD',
                'number_field': 1234,
            },
        }
        url = reverse('dcim-api:site-detail', kwargs={'pk': self.sites[1].pk})
        self.add_permissions('dcim.change_site')

        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        # Validate response data
        response_cf = response.data['custom_fields']
        self.assertEqual(response_cf['text_field'], data['custom_fields']['text_field'])
        self.assertEqual(response_cf['number_field'], data['custom_fields']['number_field'])
        self.assertEqual(response_cf['longtext_field'], original_cfvs['longtext_field'])
        self.assertEqual(response_cf['boolean_field'], original_cfvs['boolean_field'])
        self.assertEqual(response_cf['date_field'], original_cfvs['date_field'])
        self.assertEqual(response_cf['url_field'], original_cfvs['url_field'])
        self.assertEqual(response_cf['json_field'], original_cfvs['json_field'])
        self.assertEqual(response_cf['choice_field'], original_cfvs['choice_field'])

        # Validate database data
        site.refresh_from_db()
        self.assertEqual(site.custom_field_data['text_field'], data['custom_fields']['text_field'])
        self.assertEqual(site.custom_field_data['number_field'], data['custom_fields']['number_field'])
        self.assertEqual(site.custom_field_data['longtext_field'], original_cfvs['longtext_field'])
        self.assertEqual(site.custom_field_data['boolean_field'], original_cfvs['boolean_field'])
        self.assertEqual(site.custom_field_data['date_field'], original_cfvs['date_field'])
        self.assertEqual(site.custom_field_data['url_field'], original_cfvs['url_field'])
        self.assertEqual(site.custom_field_data['json_field'], original_cfvs['json_field'])
        self.assertEqual(site.custom_field_data['choice_field'], original_cfvs['choice_field'])

    def test_minimum_maximum_values_validation(self):
        url = reverse('dcim-api:site-detail', kwargs={'pk': self.sites[1].pk})
        self.add_permissions('dcim.change_site')

        self.cf_integer.validation_minimum = 10
        self.cf_integer.validation_maximum = 20
        self.cf_integer.save()

        data = {'custom_fields': {'number_field': 9}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'number_field': 21}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        data = {'custom_fields': {'number_field': 15}}
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

    def test_regex_validation(self):
        url = reverse('dcim-api:site-detail', kwargs={'pk': self.sites[1].pk})
        self.add_permissions('dcim.change_site')

        self.cf_text.validation_regex = r'^[A-Z]{3}$'  # Three uppercase letters
        self.cf_text.save()

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

        custom_fields = (
            CustomField(name='text', type=CustomFieldTypeChoices.TYPE_TEXT),
            CustomField(name='longtext', type=CustomFieldTypeChoices.TYPE_LONGTEXT),
            CustomField(name='integer', type=CustomFieldTypeChoices.TYPE_INTEGER),
            CustomField(name='boolean', type=CustomFieldTypeChoices.TYPE_BOOLEAN),
            CustomField(name='date', type=CustomFieldTypeChoices.TYPE_DATE),
            CustomField(name='url', type=CustomFieldTypeChoices.TYPE_URL),
            CustomField(name='json', type=CustomFieldTypeChoices.TYPE_JSON),
            CustomField(name='select', type=CustomFieldTypeChoices.TYPE_SELECT, choices=[
                'Choice A', 'Choice B', 'Choice C',
            ]),
        )
        for cf in custom_fields:
            cf.save()
            cf.content_types.set([ContentType.objects.get_for_model(Site)])

    def test_import(self):
        """
        Import a Site in CSV format, including a value for each CustomField.
        """
        data = (
            ('name', 'slug', 'status', 'cf_text', 'cf_longtext', 'cf_integer', 'cf_boolean', 'cf_date', 'cf_url', 'cf_json', 'cf_select'),
            ('Site 1', 'site-1', 'active', 'ABC', 'Foo', '123', 'True', '2020-01-01', 'http://example.com/1', '{"foo": 123}', 'Choice A'),
            ('Site 2', 'site-2', 'active', 'DEF', 'Bar', '456', 'False', '2020-01-02', 'http://example.com/2', '{"bar": 456}', 'Choice B'),
            ('Site 3', 'site-3', 'active', '', '', '', '', '', '', '', ''),
        )
        csv_data = '\n'.join(','.join(row) for row in data)

        response = self.client.post(reverse('dcim:site_import'), {'csv': csv_data})
        self.assertEqual(response.status_code, 200)

        # Validate data for site 1
        site1 = Site.objects.get(name='Site 1')
        self.assertEqual(len(site1.custom_field_data), 8)
        self.assertEqual(site1.custom_field_data['text'], 'ABC')
        self.assertEqual(site1.custom_field_data['longtext'], 'Foo')
        self.assertEqual(site1.custom_field_data['integer'], 123)
        self.assertEqual(site1.custom_field_data['boolean'], True)
        self.assertEqual(site1.custom_field_data['date'], '2020-01-01')
        self.assertEqual(site1.custom_field_data['url'], 'http://example.com/1')
        self.assertEqual(site1.custom_field_data['json'], {"foo": 123})
        self.assertEqual(site1.custom_field_data['select'], 'Choice A')

        # Validate data for site 2
        site2 = Site.objects.get(name='Site 2')
        self.assertEqual(len(site2.custom_field_data), 8)
        self.assertEqual(site2.custom_field_data['text'], 'DEF')
        self.assertEqual(site2.custom_field_data['longtext'], 'Bar')
        self.assertEqual(site2.custom_field_data['integer'], 456)
        self.assertEqual(site2.custom_field_data['boolean'], False)
        self.assertEqual(site2.custom_field_data['date'], '2020-01-02')
        self.assertEqual(site2.custom_field_data['url'], 'http://example.com/2')
        self.assertEqual(site2.custom_field_data['json'], {"bar": 456})
        self.assertEqual(site2.custom_field_data['select'], 'Choice B')

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

        form = SiteCSVForm(data=form_data)
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

        form = SiteCSVForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cf_select', form.errors)


class CustomFieldModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cf1 = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='foo')
        cf1.save()
        cf1.content_types.set([ContentType.objects.get_for_model(Site)])

        cf2 = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='bar')
        cf2.save()
        cf2.content_types.set([ContentType.objects.get_for_model(Rack)])

    def test_cf_data(self):
        """
        Check that custom field data is present on the instance immediately after being set and after being fetched
        from the database.
        """
        site = Site(name='Test Site', slug='test-site')

        # Check custom field data on new instance
        site.cf['foo'] = 'abc'
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
        site.cf['foo'] = 'abc'
        site.cf['bar'] = 'def'
        with self.assertRaises(ValidationError):
            site.clean()

        del(site.cf['bar'])
        site.clean()

    def test_missing_required_field(self):
        """
        Check that a ValidationError is raised if any required custom fields are not present.
        """
        cf3 = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='baz', required=True)
        cf3.save()
        cf3.content_types.set([ContentType.objects.get_for_model(Site)])

        site = Site(name='Test Site', slug='test-site')

        # Set custom field data with a required field omitted
        site.cf['foo'] = 'abc'
        with self.assertRaises(ValidationError):
            site.clean()

        site.cf['baz'] = 'def'
        site.clean()


class CustomFieldModelFilterTest(TestCase):
    queryset = Site.objects.all()
    filterset = SiteFilterSet

    @classmethod
    def setUpTestData(cls):
        obj_type = ContentType.objects.get_for_model(Site)

        # Integer filtering
        cf = CustomField(name='cf1', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf.save()
        cf.content_types.set([obj_type])

        # Boolean filtering
        cf = CustomField(name='cf2', type=CustomFieldTypeChoices.TYPE_BOOLEAN)
        cf.save()
        cf.content_types.set([obj_type])

        # Exact text filtering
        cf = CustomField(name='cf3', type=CustomFieldTypeChoices.TYPE_TEXT,
                         filter_logic=CustomFieldFilterLogicChoices.FILTER_EXACT)
        cf.save()
        cf.content_types.set([obj_type])

        # Loose text filtering
        cf = CustomField(name='cf4', type=CustomFieldTypeChoices.TYPE_TEXT,
                         filter_logic=CustomFieldFilterLogicChoices.FILTER_LOOSE)
        cf.save()
        cf.content_types.set([obj_type])

        # Date filtering
        cf = CustomField(name='cf5', type=CustomFieldTypeChoices.TYPE_DATE)
        cf.save()
        cf.content_types.set([obj_type])

        # Exact URL filtering
        cf = CustomField(name='cf6', type=CustomFieldTypeChoices.TYPE_URL,
                         filter_logic=CustomFieldFilterLogicChoices.FILTER_EXACT)
        cf.save()
        cf.content_types.set([obj_type])

        # Loose URL filtering
        cf = CustomField(name='cf7', type=CustomFieldTypeChoices.TYPE_URL,
                         filter_logic=CustomFieldFilterLogicChoices.FILTER_LOOSE)
        cf.save()
        cf.content_types.set([obj_type])

        # Selection filtering
        cf = CustomField(name='cf8', type=CustomFieldTypeChoices.TYPE_SELECT, choices=['Foo', 'Bar', 'Baz'])
        cf.save()
        cf.content_types.set([obj_type])

        # Multiselect filtering
        cf = CustomField(name='cf9', type=CustomFieldTypeChoices.TYPE_MULTISELECT, choices=['A', 'B', 'C', 'X'])
        cf.save()
        cf.content_types.set([obj_type])

        Site.objects.bulk_create([
            Site(name='Site 1', slug='site-1', custom_field_data={
                'cf1': 100,
                'cf2': True,
                'cf3': 'foo',
                'cf4': 'foo',
                'cf5': '2016-06-26',
                'cf6': 'http://a.example.com',
                'cf7': 'http://a.example.com',
                'cf8': 'Foo',
                'cf9': ['A', 'X'],
            }),
            Site(name='Site 2', slug='site-2', custom_field_data={
                'cf1': 200,
                'cf2': True,
                'cf3': 'foobar',
                'cf4': 'foobar',
                'cf5': '2016-06-27',
                'cf6': 'http://b.example.com',
                'cf7': 'http://b.example.com',
                'cf8': 'Bar',
                'cf9': ['B', 'X'],
            }),
            Site(name='Site 3', slug='site-3', custom_field_data={
                'cf1': 300,
                'cf2': False,
                'cf3': 'bar',
                'cf4': 'bar',
                'cf5': '2016-06-28',
                'cf6': 'http://c.example.com',
                'cf7': 'http://c.example.com',
                'cf8': 'Baz',
                'cf9': ['C', 'X'],
            }),
        ])

    def test_filter_integer(self):
        self.assertEqual(self.filterset({'cf_cf1': [100, 200]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf1__n': [200]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf1__gt': [200]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf1__gte': [200]}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf1__lt': [200]}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf1__lte': [200]}, self.queryset).qs.count(), 2)

    def test_filter_boolean(self):
        self.assertEqual(self.filterset({'cf_cf2': True}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf2': False}, self.queryset).qs.count(), 1)

    def test_filter_text_strict(self):
        self.assertEqual(self.filterset({'cf_cf3': ['foo']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf3__n': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf3__ic': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf3__nic': ['foo']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf3__isw': ['foo']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf3__nisw': ['foo']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf3__iew': ['bar']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf3__niew': ['bar']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf3__ie': ['FOO']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf3__nie': ['FOO']}, self.queryset).qs.count(), 2)

    def test_filter_text_loose(self):
        self.assertEqual(self.filterset({'cf_cf4': ['foo']}, self.queryset).qs.count(), 2)

    def test_filter_date(self):
        self.assertEqual(self.filterset({'cf_cf5': ['2016-06-26', '2016-06-27']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf5__n': ['2016-06-27']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf5__gt': ['2016-06-27']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf5__gte': ['2016-06-27']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf5__lt': ['2016-06-27']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf5__lte': ['2016-06-27']}, self.queryset).qs.count(), 2)

    def test_filter_url_strict(self):
        self.assertEqual(self.filterset({'cf_cf6': ['http://a.example.com', 'http://b.example.com']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf6__n': ['http://b.example.com']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf6__ic': ['b']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf6__nic': ['b']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf6__isw': ['http://']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf6__nisw': ['http://']}, self.queryset).qs.count(), 0)
        self.assertEqual(self.filterset({'cf_cf6__iew': ['.com']}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({'cf_cf6__niew': ['.com']}, self.queryset).qs.count(), 0)
        self.assertEqual(self.filterset({'cf_cf6__ie': ['HTTP://A.EXAMPLE.COM']}, self.queryset).qs.count(), 1)
        self.assertEqual(self.filterset({'cf_cf6__nie': ['HTTP://A.EXAMPLE.COM']}, self.queryset).qs.count(), 2)

    def test_filter_url_loose(self):
        self.assertEqual(self.filterset({'cf_cf7': ['example.com']}, self.queryset).qs.count(), 3)

    def test_filter_select(self):
        self.assertEqual(self.filterset({'cf_cf8': ['Foo', 'Bar']}, self.queryset).qs.count(), 2)

    def test_filter_multiselect(self):
        self.assertEqual(self.filterset({'cf_cf9': ['A', 'B']}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'cf_cf9': ['X']}, self.queryset).qs.count(), 3)
