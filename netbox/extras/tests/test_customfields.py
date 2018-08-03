from __future__ import unicode_literals

from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from dcim.models import Site
from extras.constants import CF_TYPE_TEXT, CF_TYPE_INTEGER, CF_TYPE_BOOLEAN, CF_TYPE_DATE, CF_TYPE_SELECT, CF_TYPE_URL
from extras.models import CustomField, CustomFieldValue, CustomFieldChoice
from utilities.testing import APITestCase


class CustomFieldTest(TestCase):

    def setUp(self):

        Site.objects.bulk_create([
            Site(name='Site A', slug='site-a'),
            Site(name='Site B', slug='site-b'),
            Site(name='Site C', slug='site-c'),
        ])

    def test_simple_fields(self):

        DATA = (
            {'field_type': CF_TYPE_TEXT, 'field_value': 'Foobar!', 'empty_value': ''},
            {'field_type': CF_TYPE_INTEGER, 'field_value': 0, 'empty_value': None},
            {'field_type': CF_TYPE_INTEGER, 'field_value': 42, 'empty_value': None},
            {'field_type': CF_TYPE_BOOLEAN, 'field_value': True, 'empty_value': None},
            {'field_type': CF_TYPE_BOOLEAN, 'field_value': False, 'empty_value': None},
            {'field_type': CF_TYPE_DATE, 'field_value': date(2016, 6, 23), 'empty_value': None},
            {'field_type': CF_TYPE_URL, 'field_value': 'http://example.com/', 'empty_value': ''},
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
        cf = CustomField(type=CF_TYPE_SELECT, name='my_field', required=False)
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

        super(CustomFieldAPITest, self).setUp()

        content_type = ContentType.objects.get_for_model(Site)

        # Text custom field
        self.cf_text = CustomField(type=CF_TYPE_TEXT, name='magic_word')
        self.cf_text.save()
        self.cf_text.obj_type.set([content_type])
        self.cf_text.save()

        # Integer custom field
        self.cf_integer = CustomField(type=CF_TYPE_INTEGER, name='magic_number')
        self.cf_integer.save()
        self.cf_integer.obj_type.set([content_type])
        self.cf_integer.save()

        # Boolean custom field
        self.cf_boolean = CustomField(type=CF_TYPE_BOOLEAN, name='is_magic')
        self.cf_boolean.save()
        self.cf_boolean.obj_type.set([content_type])
        self.cf_boolean.save()

        # Date custom field
        self.cf_date = CustomField(type=CF_TYPE_DATE, name='magic_date')
        self.cf_date.save()
        self.cf_date.obj_type.set([content_type])
        self.cf_date.save()

        # URL custom field
        self.cf_url = CustomField(type=CF_TYPE_URL, name='magic_url')
        self.cf_url.save()
        self.cf_url.obj_type.set([content_type])
        self.cf_url.save()

        # Select custom field
        self.cf_select = CustomField(type=CF_TYPE_SELECT, name='magic_choice')
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
