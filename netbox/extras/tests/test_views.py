import urllib.parse
import uuid

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from dcim.models import Site
from extras.constants import OBJECTCHANGE_ACTION_UPDATE
from extras.models import ConfigContext, ObjectChange, Tag
from utilities.testing import create_test_user


class TagTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['extras.view_tag'])
        self.client = Client()
        self.client.force_login(user)

        Tag.objects.bulk_create([
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2'),
            Tag(name='Tag 3', slug='tag-3'),
        ])

    def test_tag_list(self):

        url = reverse('extras:tag_list')
        params = {
            "q": "tag",
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)


class ConfigContextTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['extras.view_configcontext'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        # Create three ConfigContexts
        for i in range(1, 4):
            configcontext = ConfigContext(
                name='Config Context {}'.format(i),
                data='{{"foo": {}}}'.format(i)
            )
            configcontext.save()
            configcontext.sites.add(site)

    def test_configcontext_list(self):

        url = reverse('extras:configcontext_list')
        params = {
            "q": "foo",
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_configcontext(self):

        configcontext = ConfigContext.objects.first()
        response = self.client.get(configcontext.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class ObjectChangeTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['extras.view_objectchange'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        # Create three ObjectChanges
        for i in range(1, 4):
            oc = site.to_objectchange(action=OBJECTCHANGE_ACTION_UPDATE)
            oc.user = user
            oc.request_id = uuid.uuid4()
            oc.save()

    def test_objectchange_list(self):

        url = reverse('extras:objectchange_list')
        params = {
            "user": User.objects.first(),
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_objectchange(self):

        objectchange = ObjectChange.objects.first()
        response = self.client.get(objectchange.get_absolute_url())
        self.assertEqual(response.status_code, 200)
