from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import status

from dcim.models import Site
from utilities.testing import APITestCase


class TaggedItemTest(APITestCase):
    """
    Test the application of Tags to and item (a Site, for example) upon creation (POST) and modification (PATCH).
    """

    def setUp(self):

        super(TaggedItemTest, self).setUp()

    def test_create_tagged_item(self):

        data = {
            'name': 'Test Site',
            'slug': 'test-site',
            'tags': ['Foo', 'Bar', 'Baz']
        }

        url = reverse('dcim-api:site-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(sorted(response.data['tags']), sorted(data['tags']))
        site = Site.objects.get(pk=response.data['id'])
        tags = [tag.name for tag in site.tags.all()]
        self.assertEqual(sorted(tags), sorted(data['tags']))

    def test_update_tagged_item(self):

        site = Site.objects.create(
            name='Test Site',
            slug='test-site',
            tags=['Foo', 'Bar', 'Baz']
        )

        data = {
            'tags': ['Foo', 'Bar', 'New Tag']
        }

        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})
        response = self.client.patch(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(sorted(response.data['tags']), sorted(data['tags']))
        site = Site.objects.get(pk=response.data['id'])
        tags = [tag.name for tag in site.tags.all()]
        self.assertEqual(sorted(tags), sorted(data['tags']))
