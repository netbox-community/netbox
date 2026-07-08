import urllib.parse
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test import Client, override_settings
from django.urls import reverse

from dcim.models import DeviceType, Manufacturer, Site
from extras.models import ImageAttachment
from netbox.constants import EMPTY_TABLE_TEXT
from netbox.search.backends import search_backend
from utilities.testing import TestCase


class HomeViewTestCase(TestCase):

    def test_home(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)


class SearchViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        sites = (
            Site(name='Site Alpha', slug='alpha', description='Red'),
            Site(name='Site Bravo', slug='bravo', description='Red'),
            Site(name='Site Charlie', slug='charlie', description='Green'),
            Site(name='Site Delta', slug='delta', description='Green'),
            Site(name='Site Echo', slug='echo', description='Blue'),
            Site(name='Site Foxtrot', slug='foxtrot', description='Blue'),
        )
        Site.objects.bulk_create(sites)
        search_backend.cache(sites)

    def test_search(self):
        url = reverse('search')
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)

    def test_search_query(self):
        url = reverse('search')
        params = {
            'q': 'red',
        }
        query = urllib.parse.urlencode(params)

        # Test without view permission
        response = self.client.get(f'{url}?{query}')
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn(EMPTY_TABLE_TEXT, content)

        # Add view permissions & query again. Only matching objects should be listed
        self.add_permissions('dcim.view_site')
        response = self.client.get(f'{url}?{query}')
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn('Site Alpha', content)
        self.assertIn('Site Bravo', content)
        self.assertNotIn('Site Charlie', content)
        self.assertNotIn('Site Delta', content)
        self.assertNotIn('Site Echo', content)
        self.assertNotIn('Site Foxtrot', content)

    def test_search_no_results(self):
        self.add_permissions('dcim.view_site')
        url = reverse('search')
        params = {
            'q': 'xxxxxxxxx',  # Matches nothing
        }
        query = urllib.parse.urlencode(params)

        response = self.client.get(f'{url}?{query}')
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn(EMPTY_TABLE_TEXT, content)


class MediaViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        ct = ContentType.objects.get_for_model(Site)
        cls.image_attachment = ImageAttachment.objects.create(
            object_type=ct,
            object_id=site.pk,
            name='Test Image',
            image='image-attachments/site_1_test.jpg',
            image_height=100,
            image_width=100,
        )

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        cls.device_type = DeviceType.objects.create(
            model='Device Type 1',
            slug='device-type-1',
            manufacturer=manufacturer,
            front_image='devicetype-images/front.jpg',
        )

    def test_media_login_required(self):
        url = reverse('media', kwargs={'path': 'foo.txt'})
        response = Client().get(url)

        # Unauthenticated request should redirect to login page
        self.assertHttpStatus(response, 302)

    @override_settings(LOGIN_REQUIRED=False)
    def test_media_login_not_required(self):
        url = reverse('media', kwargs={'path': 'foo.txt'})
        response = Client().get(url)

        # Unauthenticated request should return a 404 (not found)
        self.assertHttpStatus(response, 404)

    def test_image_attachment_with_permission(self):
        self.add_permissions('extras.view_imageattachment')
        url = reverse('media', kwargs={'path': self.image_attachment.image.name})
        with patch('netbox.views.misc.serve', return_value=HttpResponse(status=200)):
            response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        self.assertEqual(response['Content-Security-Policy'], "sandbox; default-src 'none'")
        self.assertEqual(response['X-Content-Type-Options'], "nosniff")

    def test_image_attachment_without_permission(self):
        url = reverse('media', kwargs={'path': self.image_attachment.image.name})
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)

    def test_image_attachment_traversal_without_permission(self):
        # A traversal path that normalizes to a protected directory must still be denied.
        traversal_path = 'foo/../' + self.image_attachment.image.name
        url = reverse('media', kwargs={'path': traversal_path})
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)

    def test_device_type_with_permission(self):
        self.add_permissions('dcim.view_devicetype')
        url = reverse('media', kwargs={'path': self.device_type.front_image.name})
        with patch('netbox.views.misc.serve', return_value=HttpResponse(status=200)):
            response = self.client.get(url)
        self.assertHttpStatus(response, 200)
        self.assertEqual(response['Content-Security-Policy'], "sandbox; default-src 'none'")
        self.assertEqual(response['X-Content-Type-Options'], "nosniff")

    def test_device_type_without_permission(self):
        url = reverse('media', kwargs={'path': self.device_type.front_image.name})
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)

    def test_device_type_traversal_without_permission(self):
        # A traversal path that normalizes to a protected directory must still be denied.
        traversal_path = 'foo/../' + self.device_type.front_image.name
        url = reverse('media', kwargs={'path': traversal_path})
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)
