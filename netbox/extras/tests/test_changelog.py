from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from dcim.choices import SiteStatusChoices
from dcim.models import Site
from extras.choices import *
from extras.models import CustomField, ObjectChange, Tag
from utilities.testing import APITestCase
from utilities.testing.utils import post_data
from utilities.testing.views import ModelViewTestCase


class ChangeLogViewTest(ModelViewTestCase):
    model = Site

    @classmethod
    def setUpTestData(cls):

        # Create a custom field on the Site model
        ct = ContentType.objects.get_for_model(Site)
        cf = CustomField(
            type=CustomFieldTypeChoices.TYPE_TEXT,
            name='my_field',
            required=False
        )
        cf.save()
        cf.content_types.set([ct])

        # Create a select custom field on the Site model
        cf_select = CustomField(
            type=CustomFieldTypeChoices.TYPE_SELECT,
            name='my_field_select',
            required=False,
            choices=['Bar', 'Foo']
        )
        cf_select.save()
        cf_select.content_types.set([ct])

    def test_create_object(self):
        tags = self.create_tags('Tag 1', 'Tag 2')
        form_data = {
            'name': 'Site 1',
            'slug': 'site-1',
            'status': SiteStatusChoices.STATUS_ACTIVE,
            'cf_my_field': 'ABC',
            'cf_my_field_select': 'Bar',
            'tags': [tag.pk for tag in tags],
        }

        request = {
            'path': self._get_url('add'),
            'data': post_data(form_data),
        }
        self.add_permissions('dcim.add_site', 'extras.view_tag')
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)

        site = Site.objects.get(name='Site 1')
        # First OC is the creation; second is the tags update
        oc_list = ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk
        ).order_by('pk')
        self.assertEqual(oc_list[0].changed_object, site)
        self.assertEqual(oc_list[0].action, ObjectChangeActionChoices.ACTION_CREATE)
        self.assertEqual(oc_list[0].prechange_data, None)
        self.assertEqual(oc_list[0].postchange_data['custom_fields']['my_field'], form_data['cf_my_field'])
        self.assertEqual(oc_list[0].postchange_data['custom_fields']['my_field_select'], form_data['cf_my_field_select'])
        self.assertEqual(oc_list[1].action, ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(oc_list[1].postchange_data['tags'], ['Tag 1', 'Tag 2'])

    def test_update_object(self):
        site = Site(name='Site 1', slug='site-1')
        site.save()
        tags = self.create_tags('Tag 1', 'Tag 2', 'Tag 3')
        site.tags.set('Tag 1', 'Tag 2')

        form_data = {
            'name': 'Site X',
            'slug': 'site-x',
            'status': SiteStatusChoices.STATUS_PLANNED,
            'cf_my_field': 'DEF',
            'cf_my_field_select': 'Foo',
            'tags': [tags[2].pk],
        }

        request = {
            'path': self._get_url('edit', instance=site),
            'data': post_data(form_data),
        }
        self.add_permissions('dcim.change_site', 'extras.view_tag')
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)

        site.refresh_from_db()
        # Get only the most recent OC
        oc = ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk
        ).first()
        self.assertEqual(oc.changed_object, site)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(oc.prechange_data['name'], 'Site 1')
        self.assertEqual(oc.prechange_data['tags'], ['Tag 1', 'Tag 2'])
        self.assertEqual(oc.postchange_data['custom_fields']['my_field'], form_data['cf_my_field'])
        self.assertEqual(oc.postchange_data['custom_fields']['my_field_select'], form_data['cf_my_field_select'])
        self.assertEqual(oc.postchange_data['tags'], ['Tag 3'])

    def test_delete_object(self):
        site = Site(
            name='Site 1',
            slug='site-1',
            custom_field_data={
                'my_field': 'ABC',
                'my_field_select': 'Bar'
            }
        )
        site.save()
        self.create_tags('Tag 1', 'Tag 2')
        site.tags.set('Tag 1', 'Tag 2')

        request = {
            'path': self._get_url('delete', instance=site),
            'data': post_data({'confirm': True}),
        }
        self.add_permissions('dcim.delete_site')
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)

        oc = ObjectChange.objects.first()
        self.assertEqual(oc.changed_object, None)
        self.assertEqual(oc.object_repr, site.name)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_DELETE)
        self.assertEqual(oc.prechange_data['custom_fields']['my_field'], 'ABC')
        self.assertEqual(oc.prechange_data['custom_fields']['my_field_select'], 'Bar')
        self.assertEqual(oc.prechange_data['tags'], ['Tag 1', 'Tag 2'])
        self.assertEqual(oc.postchange_data, None)

    def test_bulk_update_objects(self):
        sites = (
            Site(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_ACTIVE),
            Site(name='Site 2', slug='site-2', status=SiteStatusChoices.STATUS_ACTIVE),
            Site(name='Site 3', slug='site-3', status=SiteStatusChoices.STATUS_ACTIVE),
        )
        Site.objects.bulk_create(sites)

        form_data = {
            'pk': [site.pk for site in sites],
            '_apply': True,
            'status': SiteStatusChoices.STATUS_PLANNED,
            'description': 'New description',
        }

        request = {
            'path': self._get_url('bulk_edit'),
            'data': post_data(form_data),
        }
        self.add_permissions('dcim.view_site', 'dcim.change_site')
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)

        objectchange = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=sites[0].pk
        )
        self.assertEqual(objectchange.changed_object, sites[0])
        self.assertEqual(objectchange.action, ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['status'], SiteStatusChoices.STATUS_ACTIVE)
        self.assertEqual(objectchange.prechange_data['description'], '')
        self.assertEqual(objectchange.postchange_data['status'], form_data['status'])
        self.assertEqual(objectchange.postchange_data['description'], form_data['description'])

    def test_bulk_delete_objects(self):
        sites = (
            Site(name='Site 1', slug='site-1', status=SiteStatusChoices.STATUS_ACTIVE),
            Site(name='Site 2', slug='site-2', status=SiteStatusChoices.STATUS_ACTIVE),
            Site(name='Site 3', slug='site-3', status=SiteStatusChoices.STATUS_ACTIVE),
        )
        Site.objects.bulk_create(sites)

        form_data = {
            'pk': [site.pk for site in sites],
            'confirm': True,
            '_confirm': True,
        }

        request = {
            'path': self._get_url('bulk_delete'),
            'data': post_data(form_data),
        }
        self.add_permissions('dcim.delete_site')
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)

        objectchange = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=sites[0].pk
        )
        self.assertEqual(objectchange.changed_object_type, ContentType.objects.get_for_model(Site))
        self.assertEqual(objectchange.changed_object_id, sites[0].pk)
        self.assertEqual(objectchange.action, ObjectChangeActionChoices.ACTION_DELETE)
        self.assertEqual(objectchange.prechange_data['name'], sites[0].name)
        self.assertEqual(objectchange.prechange_data['slug'], sites[0].slug)
        self.assertEqual(objectchange.postchange_data, None)


class ChangeLogAPITest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        # Create a custom field on the Site model
        ct = ContentType.objects.get_for_model(Site)
        cf = CustomField(
            type=CustomFieldTypeChoices.TYPE_TEXT,
            name='my_field',
            required=False
        )
        cf.save()
        cf.content_types.set([ct])

        # Create a select custom field on the Site model
        cf_select = CustomField(
            type=CustomFieldTypeChoices.TYPE_SELECT,
            name='my_field_select',
            required=False,
            choices=['Bar', 'Foo']
        )
        cf_select.save()
        cf_select.content_types.set([ct])

        # Create some tags
        tags = (
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2'),
            Tag(name='Tag 3', slug='tag-3'),
        )
        Tag.objects.bulk_create(tags)

    def test_create_object(self):
        data = {
            'name': 'Site 1',
            'slug': 'site-1',
            'custom_fields': {
                'my_field': 'ABC',
                'my_field_select': 'Bar',
            },
            'tags': [
                {'name': 'Tag 1'},
                {'name': 'Tag 2'},
            ]
        }
        self.assertEqual(ObjectChange.objects.count(), 0)
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        site = Site.objects.get(pk=response.data['id'])
        # First OC is the creation; second is the tags update
        oc_list = ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk
        ).order_by('pk')
        self.assertEqual(oc_list[0].changed_object, site)
        self.assertEqual(oc_list[0].action, ObjectChangeActionChoices.ACTION_CREATE)
        self.assertEqual(oc_list[0].prechange_data, None)
        self.assertEqual(oc_list[0].postchange_data['custom_fields'], data['custom_fields'])
        self.assertEqual(oc_list[1].action, ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(oc_list[1].postchange_data['tags'], ['Tag 1', 'Tag 2'])

    def test_update_object(self):
        site = Site(name='Site 1', slug='site-1')
        site.save()

        data = {
            'name': 'Site X',
            'slug': 'site-x',
            'custom_fields': {
                'my_field': 'DEF',
                'my_field_select': 'Foo',
            },
            'tags': [
                {'name': 'Tag 3'}
            ]
        }
        self.assertEqual(ObjectChange.objects.count(), 0)
        self.add_permissions('dcim.change_site')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})

        response = self.client.put(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        site = Site.objects.get(pk=response.data['id'])
        # Get only the most recent OC
        oc = ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk
        ).first()
        self.assertEqual(oc.changed_object, site)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(oc.postchange_data['custom_fields'], data['custom_fields'])
        self.assertEqual(oc.postchange_data['tags'], ['Tag 3'])

    def test_delete_object(self):
        site = Site(
            name='Site 1',
            slug='site-1',
            custom_field_data={
                'my_field': 'ABC',
                'my_field_select': 'Bar'
            }
        )
        site.save()
        site.tags.set(*Tag.objects.all()[:2])
        self.assertEqual(ObjectChange.objects.count(), 0)
        self.add_permissions('dcim.delete_site')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})

        response = self.client.delete(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Site.objects.count(), 0)

        oc = ObjectChange.objects.first()
        self.assertEqual(oc.changed_object, None)
        self.assertEqual(oc.object_repr, site.name)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_DELETE)
        self.assertEqual(oc.prechange_data['custom_fields']['my_field'], 'ABC')
        self.assertEqual(oc.prechange_data['custom_fields']['my_field_select'], 'Bar')
        self.assertEqual(oc.prechange_data['tags'], ['Tag 1', 'Tag 2'])
        self.assertEqual(oc.postchange_data, None)

    def test_bulk_create_objects(self):
        data = (
            {
                'name': 'Site 1',
                'slug': 'site-1',
            },
            {
                'name': 'Site 2',
                'slug': 'site-2',
            },
            {
                'name': 'Site 3',
                'slug': 'site-3',
            },
        )
        self.assertEqual(ObjectChange.objects.count(), 0)
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ObjectChange.objects.count(), 3)

        site1 = Site.objects.get(pk=response.data[0]['id'])
        objectchange = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site1.pk
        )
        self.assertEqual(objectchange.changed_object, site1)
        self.assertEqual(objectchange.action, ObjectChangeActionChoices.ACTION_CREATE)
        self.assertEqual(objectchange.prechange_data, None)
        self.assertEqual(objectchange.postchange_data['name'], data[0]['name'])
        self.assertEqual(objectchange.postchange_data['slug'], data[0]['slug'])

    def test_bulk_edit_objects(self):
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        data = (
            {
                'id': sites[0].pk,
                'name': 'Site A',
                'slug': 'site-A',
            },
            {
                'id': sites[1].pk,
                'name': 'Site B',
                'slug': 'site-b',
            },
            {
                'id': sites[2].pk,
                'name': 'Site C',
                'slug': 'site-c',
            },
        )
        self.assertEqual(ObjectChange.objects.count(), 0)
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.change_site')

        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ObjectChange.objects.count(), 3)

        objectchange = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=sites[0].pk
        )
        self.assertEqual(objectchange.changed_object, sites[0])
        self.assertEqual(objectchange.action, ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['name'], 'Site 1')
        self.assertEqual(objectchange.prechange_data['slug'], 'site-1')
        self.assertEqual(objectchange.postchange_data['name'], data[0]['name'])
        self.assertEqual(objectchange.postchange_data['slug'], data[0]['slug'])

    def test_bulk_delete_objects(self):
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        data = (
            {
                'id': sites[0].pk,
            },
            {
                'id': sites[1].pk,
            },
            {
                'id': sites[2].pk,
            },
        )
        self.assertEqual(ObjectChange.objects.count(), 0)
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.delete_site')

        response = self.client.delete(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ObjectChange.objects.count(), 3)

        objectchange = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=sites[0].pk
        )
        self.assertEqual(objectchange.changed_object_type, ContentType.objects.get_for_model(Site))
        self.assertEqual(objectchange.changed_object_id, sites[0].pk)
        self.assertEqual(objectchange.action, ObjectChangeActionChoices.ACTION_DELETE)
        self.assertEqual(objectchange.prechange_data['name'], 'Site 1')
        self.assertEqual(objectchange.prechange_data['slug'], 'site-1')
        self.assertEqual(objectchange.postchange_data, None)
