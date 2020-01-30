import urllib.parse
import uuid

from django.contrib.auth.models import User
from django.urls import reverse

from dcim.models import Site
from extras.choices import ObjectChangeActionChoices
from extras.models import ConfigContext, ObjectChange, Tag
from utilities.testing import TestCase


class TagTestCase(TestCase):
    user_permissions = (
        'extras.view_tag',
    )

    @classmethod
    def setUpTestData(cls):

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
        self.assertHttpStatus(response, 200)


class ConfigContextTestCase(TestCase):
    user_permissions = (
        'extras.view_configcontext',
    )

    @classmethod
    def setUpTestData(cls):

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
        self.assertHttpStatus(response, 200)

    def test_configcontext(self):

        configcontext = ConfigContext.objects.first()
        response = self.client.get(configcontext.get_absolute_url())
        self.assertHttpStatus(response, 200)


class ObjectChangeTestCase(TestCase):
    user_permissions = (
        'extras.view_objectchange',
    )

    @classmethod
    def setUpTestData(cls):

        site = Site(name='Site 1', slug='site-1')
        site.save()

        # Create three ObjectChanges
        user = User.objects.create_user(username='testuser2')
        for i in range(1, 4):
            oc = site.to_objectchange(action=ObjectChangeActionChoices.ACTION_UPDATE)
            oc.user = user
            oc.request_id = uuid.uuid4()
            oc.save()

    def test_objectchange_list(self):

        url = reverse('extras:objectchange_list')
        params = {
            "user": User.objects.first(),
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_objectchange(self):

        objectchange = ObjectChange.objects.first()
        response = self.client.get(objectchange.get_absolute_url())
        self.assertHttpStatus(response, 200)
