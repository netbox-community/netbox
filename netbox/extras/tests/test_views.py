import urllib.parse
import uuid

from django.contrib.auth.models import User
from django.urls import reverse

from dcim.models import Site
from extras.choices import ObjectChangeActionChoices
from extras.models import ConfigContext, ObjectChange, Tag
from utilities.testing import ViewTestCases, TestCase


class TagTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Tag

    # Disable inapplicable tests
    test_create_object = None
    test_import_objects = None

    @classmethod
    def setUpTestData(cls):

        Tag.objects.bulk_create((
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2'),
            Tag(name='Tag 3', slug='tag-3'),
        ))

        cls.form_data = {
            'name': 'Tag X',
            'slug': 'tag-x',
            'color': 'c0c0c0',
            'comments': 'Some comments',
        }

        cls.bulk_edit_data = {
            'color': '00ff00',
        }


class ConfigContextTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ConfigContext

    # Disable inapplicable tests
    test_import_objects = None

    # TODO: Resolve model discrepancies when creating/editing ConfigContexts
    test_create_object = None
    test_edit_object = None

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')

        # Create three ConfigContexts
        for i in range(1, 4):
            configcontext = ConfigContext(
                name='Config Context {}'.format(i),
                data={'foo': i}
            )
            configcontext.save()
            configcontext.sites.add(site)

        cls.form_data = {
            'name': 'Config Context X',
            'weight': 200,
            'description': 'A new config context',
            'is_active': True,
            'regions': [],
            'sites': [site.pk],
            'roles': [],
            'platforms': [],
            'tenant_groups': [],
            'tenants': [],
            'tags': [],
            'data': '{"foo": 123}',
        }

        cls.bulk_edit_data = {
            'weight': 300,
            'is_active': False,
            'description': 'New description',
        }


# TODO: Convert to StandardTestCases.Views
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
