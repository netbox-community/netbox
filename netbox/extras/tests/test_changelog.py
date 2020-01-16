from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from dcim.models import Site
from extras.choices import *
from extras.constants import *
from extras.models import CustomField, CustomFieldValue, ObjectChange
from utilities.testing import APITestCase


class ChangeLogTest(APITestCase):

    def setUp(self):

        super().setUp()

        # Create a custom field on the Site model
        ct = ContentType.objects.get_for_model(Site)
        cf = CustomField(
            type=CustomFieldTypeChoices.TYPE_TEXT,
            name='my_field',
            required=False
        )
        cf.save()
        cf.obj_type.set([ct])

    def test_create_object(self):

        data = {
            'name': 'Test Site 1',
            'slug': 'test-site-1',
            'custom_fields': {
                'my_field': 'ABC'
            },
            'tags': [
                'bar', 'foo'
            ],
        }

        self.assertEqual(ObjectChange.objects.count(), 0)

        url = reverse('dcim-api:site-list')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        site = Site.objects.get(pk=response.data['id'])
        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk
        )
        self.assertEqual(oc.changed_object, site)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_CREATE)
        self.assertEqual(oc.object_data['custom_fields'], data['custom_fields'])
        self.assertListEqual(sorted(oc.object_data['tags']), data['tags'])

    def test_update_object(self):

        site = Site(name='Test Site 1', slug='test-site-1')
        site.save()

        data = {
            'name': 'Test Site X',
            'slug': 'test-site-x',
            'custom_fields': {
                'my_field': 'DEF'
            },
            'tags': [
                'abc', 'xyz'
            ],
        }

        self.assertEqual(ObjectChange.objects.count(), 0)

        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        response = self.client.put(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        site = Site.objects.get(pk=response.data['id'])
        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk
        )
        self.assertEqual(oc.changed_object, site)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(oc.object_data['custom_fields'], data['custom_fields'])
        self.assertListEqual(sorted(oc.object_data['tags']), data['tags'])

    def test_delete_object(self):

        site = Site(
            name='Test Site 1',
            slug='test-site-1'
        )
        site.save()
        site.tags.add('foo', 'bar')
        CustomFieldValue.objects.create(
            field=CustomField.objects.get(name='my_field'),
            obj=site,
            value='ABC'
        )

        self.assertEqual(ObjectChange.objects.count(), 0)

        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Site.objects.count(), 0)

        oc = ObjectChange.objects.first()
        self.assertEqual(oc.changed_object, None)
        self.assertEqual(oc.object_repr, site.name)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_DELETE)
        self.assertEqual(oc.object_data['custom_fields'], {'my_field': 'ABC'})
        self.assertListEqual(sorted(oc.object_data['tags']), ['bar', 'foo'])
