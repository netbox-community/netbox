from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from dcim.forms import SiteCSVForm
from dcim.models import Site
from extras.choices import *
from extras.models import CustomField, CustomFieldValue, CustomFieldChoice
from utilities.testing import APITestCase, create_test_user
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
            {'field_type': CustomFieldTypeChoices.TYPE_TEXT, 'field_value': 'Foobar!', 'empty_value': ''},
            {'field_type': CustomFieldTypeChoices.TYPE_INTEGER, 'field_value': 0, 'empty_value': None},
            {'field_type': CustomFieldTypeChoices.TYPE_INTEGER, 'field_value': 42, 'empty_value': None},
            {'field_type': CustomFieldTypeChoices.TYPE_BOOLEAN, 'field_value': True, 'empty_value': None},
            {'field_type': CustomFieldTypeChoices.TYPE_BOOLEAN, 'field_value': False, 'empty_value': None},
            {'field_type': CustomFieldTypeChoices.TYPE_DATE, 'field_value': date(2016, 6, 23), 'empty_value': None},
            {'field_type': CustomFieldTypeChoices.TYPE_URL, 'field_value': 'http://example.com/', 'empty_value': ''},
        )

        obj_type = ContentType.objects.get_for_model(Site)

        for data in DATA:

            # Create a custom field
            cf = CustomField(type=data['field_type'], name='my_field', required=False)
            cf.save()
            cf.obj_type.set([obj_type])
            cf.save()

            # Assign a value to the first Site
            site = Site.objects.first()
            cfv = CustomFieldValue(field=cf, obj_type=obj_type, obj_id=site.id)
            cfv.value = data['field_value']
            cfv.save()

            # Retrieve the stored value
            cfv = CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=site.pk).first()
            self.assertEqual(cfv.value, data['field_value'])

            # Delete the stored value
            cfv.value = data['empty_value']
            cfv.save()
            self.assertEqual(CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=site.pk).count(), 0)

            # Delete the custom field
            cf.delete()

    def test_select_field(self):

        obj_type = ContentType.objects.get_for_model(Site)

        # Create a custom field
        cf = CustomField(type=CustomFieldTypeChoices.TYPE_SELECT, name='my_field', required=False)
        cf.save()
        cf.obj_type.set([obj_type])
        cf.save()

        # Create some choices for the field
        CustomFieldChoice.objects.bulk_create([
            CustomFieldChoice(field=cf, value='Option A'),
            CustomFieldChoice(field=cf, value='Option B'),
            CustomFieldChoice(field=cf, value='Option C'),
        ])

        # Assign a value to the first Site
        site = Site.objects.first()
        cfv = CustomFieldValue(field=cf, obj_type=obj_type, obj_id=site.id)
        cfv.value = cf.choices.first()
        cfv.save()

        # Retrieve the stored value
        cfv = CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=site.pk).first()
        self.assertEqual(str(cfv.value), 'Option A')

        # Delete the stored value
        cfv.value = None
        cfv.save()
        self.assertEqual(CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=site.pk).count(), 0)

        # Delete the custom field
        cf.delete()


class CustomFieldAPITest(APITestCase):

    def setUp(self):

        super().setUp()

        content_type = ContentType.objects.get_for_model(Site)

        # Text custom field
        self.cf_text = CustomField(type=CustomFieldTypeChoices.TYPE_TEXT, name='magic_word')
        self.cf_text.save()
        self.cf_text.obj_type.set([content_type])
        self.cf_text.save()

        # Integer custom field
        self.cf_integer = CustomField(type=CustomFieldTypeChoices.TYPE_INTEGER, name='magic_number')
        self.cf_integer.save()
        self.cf_integer.obj_type.set([content_type])
        self.cf_integer.save()

        # Boolean custom field
        self.cf_boolean = CustomField(type=CustomFieldTypeChoices.TYPE_BOOLEAN, name='is_magic')
        self.cf_boolean.save()
        self.cf_boolean.obj_type.set([content_type])
        self.cf_boolean.save()

        # Date custom field
        self.cf_date = CustomField(type=CustomFieldTypeChoices.TYPE_DATE, name='magic_date')
        self.cf_date.save()
        self.cf_date.obj_type.set([content_type])
        self.cf_date.save()

        # URL custom field
        self.cf_url = CustomField(type=CustomFieldTypeChoices.TYPE_URL, name='magic_url')
        self.cf_url.save()
        self.cf_url.obj_type.set([content_type])
        self.cf_url.save()

        # Select custom field
        self.cf_select = CustomField(type=CustomFieldTypeChoices.TYPE_SELECT, name='magic_choice')
        self.cf_select.save()
        self.cf_select.obj_type.set([content_type])
        self.cf_select.save()
        self.cf_select_choice1 = CustomFieldChoice(field=self.cf_select, value='Foo')
        self.cf_select_choice1.save()
        self.cf_select_choice2 = CustomFieldChoice(field=self.cf_select, value='Bar')
        self.cf_select_choice2.save()
        self.cf_select_choice3 = CustomFieldChoice(field=self.cf_select, value='Baz')
        self.cf_select_choice3.save()

        self.site = Site.objects.create(name='Test Site 1', slug='test-site-1')

    def test_get_obj_without_custom_fields(self):

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.site.name)
        self.assertEqual(response.data['custom_fields'], {
            'magic_word': None,
            'magic_number': None,
            'is_magic': None,
            'magic_date': None,
            'magic_url': None,
            'magic_choice': None,
        })

    def test_get_obj_with_custom_fields(self):

        CUSTOM_FIELD_VALUES = [
            (self.cf_text, 'Test string'),
            (self.cf_integer, 1234),
            (self.cf_boolean, True),
            (self.cf_date, date(2016, 6, 23)),
            (self.cf_url, 'http://example.com/'),
            (self.cf_select, self.cf_select_choice1.pk),
        ]
        for field, value in CUSTOM_FIELD_VALUES:
            cfv = CustomFieldValue(field=field, obj=self.site)
            cfv.value = value
            cfv.save()

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.site.name)
        self.assertEqual(response.data['custom_fields'].get('magic_word'), CUSTOM_FIELD_VALUES[0][1])
        self.assertEqual(response.data['custom_fields'].get('magic_number'), CUSTOM_FIELD_VALUES[1][1])
        self.assertEqual(response.data['custom_fields'].get('is_magic'), CUSTOM_FIELD_VALUES[2][1])
        self.assertEqual(response.data['custom_fields'].get('magic_date'), CUSTOM_FIELD_VALUES[3][1])
        self.assertEqual(response.data['custom_fields'].get('magic_url'), CUSTOM_FIELD_VALUES[4][1])
        self.assertEqual(response.data['custom_fields'].get('magic_choice'), {
            'value': self.cf_select_choice1.pk, 'label': 'Foo'
        })

    def test_set_custom_field_text(self):

        data = {
            'name': 'Test Site 1',
            'slug': 'test-site-1',
            'custom_fields': {
                'magic_word': 'Foo bar baz',
            }
        }

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['custom_fields'].get('magic_word'), data['custom_fields']['magic_word'])
        cfv = self.site.custom_field_values.get(field=self.cf_text)
        self.assertEqual(cfv.value, data['custom_fields']['magic_word'])

    def test_set_custom_field_integer(self):

        data = {
            'name': 'Test Site 1',
            'slug': 'test-site-1',
            'custom_fields': {
                'magic_number': 42,
            }
        }

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['custom_fields'].get('magic_number'), data['custom_fields']['magic_number'])
        cfv = self.site.custom_field_values.get(field=self.cf_integer)
        self.assertEqual(cfv.value, data['custom_fields']['magic_number'])

    def test_set_custom_field_boolean(self):

        data = {
            'name': 'Test Site 1',
            'slug': 'test-site-1',
            'custom_fields': {
                'is_magic': 0,
            }
        }

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['custom_fields'].get('is_magic'), data['custom_fields']['is_magic'])
        cfv = self.site.custom_field_values.get(field=self.cf_boolean)
        self.assertEqual(cfv.value, data['custom_fields']['is_magic'])

    def test_set_custom_field_date(self):

        data = {
            'name': 'Test Site 1',
            'slug': 'test-site-1',
            'custom_fields': {
                'magic_date': '2017-04-25',
            }
        }

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['custom_fields'].get('magic_date'), data['custom_fields']['magic_date'])
        cfv = self.site.custom_field_values.get(field=self.cf_date)
        self.assertEqual(cfv.value.isoformat(), data['custom_fields']['magic_date'])

    def test_set_custom_field_url(self):

        data = {
            'name': 'Test Site 1',
            'slug': 'test-site-1',
            'custom_fields': {
                'magic_url': 'http://example.com/2/',
            }
        }

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['custom_fields'].get('magic_url'), data['custom_fields']['magic_url'])
        cfv = self.site.custom_field_values.get(field=self.cf_url)
        self.assertEqual(cfv.value, data['custom_fields']['magic_url'])

    def test_set_custom_field_select(self):

        data = {
            'name': 'Test Site 1',
            'slug': 'test-site-1',
            'custom_fields': {
                'magic_choice': self.cf_select_choice2.pk,
            }
        }

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['custom_fields'].get('magic_choice'), data['custom_fields']['magic_choice'])
        cfv = self.site.custom_field_values.get(field=self.cf_select)
        self.assertEqual(cfv.value.pk, data['custom_fields']['magic_choice'])

    def test_set_custom_field_defaults(self):
        """
        Create a new object with no custom field data. Custom field values should be created using the custom fields'
        default values.
        """
        CUSTOM_FIELD_DEFAULTS = {
            'magic_word': 'foobar',
            'magic_number': '123',
            'is_magic': 'true',
            'magic_date': '2019-12-13',
            'magic_url': 'http://example.com/',
            'magic_choice': self.cf_select_choice1.value,
        }

        # Update CustomFields to set default values
        for field_name, default_value in CUSTOM_FIELD_DEFAULTS.items():
            CustomField.objects.filter(name=field_name).update(default=default_value)

        data = {
            'name': 'Test Site X',
            'slug': 'test-site-x',
        }

        url = reverse('dcim-api:site-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['custom_fields']['magic_word'], CUSTOM_FIELD_DEFAULTS['magic_word'])
        self.assertEqual(response.data['custom_fields']['magic_number'], str(CUSTOM_FIELD_DEFAULTS['magic_number']))
        self.assertEqual(response.data['custom_fields']['is_magic'], bool(CUSTOM_FIELD_DEFAULTS['is_magic']))
        self.assertEqual(response.data['custom_fields']['magic_date'], CUSTOM_FIELD_DEFAULTS['magic_date'])
        self.assertEqual(response.data['custom_fields']['magic_url'], CUSTOM_FIELD_DEFAULTS['magic_url'])
        self.assertEqual(response.data['custom_fields']['magic_choice'], self.cf_select_choice1.pk)


class CustomFieldChoiceAPITest(APITestCase):
    def setUp(self):
        super().setUp()

        vm_content_type = ContentType.objects.get_for_model(VirtualMachine)

        self.cf_1 = CustomField.objects.create(name="cf_1", type=CustomFieldTypeChoices.TYPE_SELECT)
        self.cf_2 = CustomField.objects.create(name="cf_2", type=CustomFieldTypeChoices.TYPE_SELECT)

        self.cf_choice_1 = CustomFieldChoice.objects.create(field=self.cf_1, value="cf_field_1", weight=100)
        self.cf_choice_2 = CustomFieldChoice.objects.create(field=self.cf_1, value="cf_field_2", weight=50)
        self.cf_choice_3 = CustomFieldChoice.objects.create(field=self.cf_2, value="cf_field_3", weight=10)

    def test_list_cfc(self):
        url = reverse('extras-api:custom-field-choice-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(response.data[self.cf_1.name]), 2)
        self.assertEqual(len(response.data[self.cf_2.name]), 1)

        self.assertTrue(self.cf_choice_1.value in response.data[self.cf_1.name])
        self.assertTrue(self.cf_choice_2.value in response.data[self.cf_1.name])
        self.assertTrue(self.cf_choice_3.value in response.data[self.cf_2.name])

        self.assertEqual(self.cf_choice_1.pk, response.data[self.cf_1.name][self.cf_choice_1.value])
        self.assertEqual(self.cf_choice_2.pk, response.data[self.cf_1.name][self.cf_choice_2.value])
        self.assertEqual(self.cf_choice_3.pk, response.data[self.cf_2.name][self.cf_choice_3.value])


class CustomFieldImportTest(TestCase):

    def setUp(self):

        user = create_test_user(
            permissions=[
                'dcim.view_site',
                'dcim.add_site',
            ]
        )
        self.client = Client()
        self.client.force_login(user)

    @classmethod
    def setUpTestData(cls):

        custom_fields = (
            CustomField(name='text', type=CustomFieldTypeChoices.TYPE_TEXT),
            CustomField(name='integer', type=CustomFieldTypeChoices.TYPE_INTEGER),
            CustomField(name='boolean', type=CustomFieldTypeChoices.TYPE_BOOLEAN),
            CustomField(name='date', type=CustomFieldTypeChoices.TYPE_DATE),
            CustomField(name='url', type=CustomFieldTypeChoices.TYPE_URL),
            CustomField(name='select', type=CustomFieldTypeChoices.TYPE_SELECT),
        )
        for cf in custom_fields:
            cf.save()
            cf.obj_type.set([ContentType.objects.get_for_model(Site)])

        CustomFieldChoice.objects.bulk_create((
            CustomFieldChoice(field=custom_fields[5], value='Choice A'),
            CustomFieldChoice(field=custom_fields[5], value='Choice B'),
            CustomFieldChoice(field=custom_fields[5], value='Choice C'),
        ))

    def test_import(self):
        """
        Import a Site in CSV format, including a value for each CustomField.
        """
        data = (
            ('name', 'slug', 'cf_text', 'cf_integer', 'cf_boolean', 'cf_date', 'cf_url', 'cf_select'),
            ('Site 1', 'site-1', 'ABC', '123', 'True', '2020-01-01', 'http://example.com/1', 'Choice A'),
            ('Site 2', 'site-2', 'DEF', '456', 'False', '2020-01-02', 'http://example.com/2', 'Choice B'),
            ('Site 3', 'site-3', '', '', '', '', '', ''),
        )
        csv_data = '\n'.join(','.join(row) for row in data)

        response = self.client.post(reverse('dcim:site_import'), {'csv': csv_data})
        self.assertEqual(response.status_code, 200)

        # Validate data for site 1
        custom_field_values = {
            cf.name: value for cf, value in Site.objects.get(name='Site 1').get_custom_fields().items()
        }
        self.assertEqual(len(custom_field_values), 6)
        self.assertEqual(custom_field_values['text'], 'ABC')
        self.assertEqual(custom_field_values['integer'], 123)
        self.assertEqual(custom_field_values['boolean'], True)
        self.assertEqual(custom_field_values['date'], date(2020, 1, 1))
        self.assertEqual(custom_field_values['url'], 'http://example.com/1')
        self.assertEqual(custom_field_values['select'].value, 'Choice A')

        # Validate data for site 2
        custom_field_values = {
            cf.name: value for cf, value in Site.objects.get(name='Site 2').get_custom_fields().items()
        }
        self.assertEqual(len(custom_field_values), 6)
        self.assertEqual(custom_field_values['text'], 'DEF')
        self.assertEqual(custom_field_values['integer'], 456)
        self.assertEqual(custom_field_values['boolean'], False)
        self.assertEqual(custom_field_values['date'], date(2020, 1, 2))
        self.assertEqual(custom_field_values['url'], 'http://example.com/2')
        self.assertEqual(custom_field_values['select'].value, 'Choice B')

        # No CustomFieldValues should be created for site 3
        obj_type = ContentType.objects.get_for_model(Site)
        site3 = Site.objects.get(name='Site 3')
        self.assertFalse(CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=site3.pk).exists())
        self.assertEqual(CustomFieldValue.objects.count(), 12)  # Sanity check

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
