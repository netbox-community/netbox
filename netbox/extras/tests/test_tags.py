from django.apps import apps
from django.db import models
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status

from dcim.models import Site
from extras.managers import NetBoxTaggableManagerField
from netbox.models.features import TagsMixin
from utilities.testing import APITestCase, create_tags


class TaggedItemTestCase(APITestCase):
    """
    Test the application of Tags to and item (a Site, for example) upon creation (POST) and modification (PATCH).
    """
    def test_create_tagged_item(self):
        tags = create_tags("Foo", "Bar", "Baz")
        data = {
            'name': 'Test Site',
            'slug': 'test-site',
            'tags': [t.pk for t in tags]
        }
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertListEqual(
            sorted([t['id'] for t in response.data['tags']]),
            sorted(data['tags'])
        )
        site = Site.objects.get(pk=response.data['id'])
        self.assertListEqual(
            sorted([t.name for t in site.tags.all()]),
            sorted(["Foo", "Bar", "Baz"])
        )

    def test_update_tagged_item(self):
        site = Site.objects.create(
            name='Test Site',
            slug='test-site'
        )
        site.tags.add("Foo", "Bar", "Baz")
        create_tags("New Tag")
        data = {
            'tags': [
                {"name": "Foo"},
                {"name": "Bar"},
                {"name": "New Tag"},
            ]
        }
        self.add_permissions('dcim.change_site')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})

        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertListEqual(
            sorted([t['name'] for t in response.data['tags']]),
            sorted([t['name'] for t in data['tags']])
        )
        site = Site.objects.get(pk=response.data['id'])
        self.assertListEqual(
            sorted([t.name for t in site.tags.all()]),
            sorted(["Foo", "Bar", "New Tag"])
        )

    def test_clear_tagged_item(self):
        site = Site.objects.create(
            name='Test Site',
            slug='test-site'
        )
        site.tags.add("Foo", "Bar", "Baz")
        data = {
            'tags': []
        }
        self.add_permissions('dcim.change_site')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})

        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tags']), 0)
        site = Site.objects.get(pk=response.data['id'])
        self.assertEqual(len(site.tags.all()), 0)


class TagsMixinCollisionTestCase(SimpleTestCase):
    """
    Two TagsMixin-derived models that share a class name (e.g. introduced by separate plugins)
    must not collide on Tag's reverse accessor. Regression test for #22301.
    """
    def _make_taggable_model(self, app_label, name='Foo'):
        # Build a model dynamically and register a cleanup to remove it from the global app
        # registry so subsequent test runs (and other tests in this process) don't see ghost
        # models leak in via apps.get_models().
        model = type(name, (TagsMixin, models.Model), {
            '__module__': self.__class__.__module__,
            'Meta': type('Meta', (), {'app_label': app_label}),
        })
        self.addCleanup(apps.all_models[app_label].pop, name.lower(), None)
        self.addCleanup(apps.clear_cache)
        return model

    def test_same_named_taggable_models_in_different_apps(self):
        foo_a = self._make_taggable_model('dcim')
        foo_b = self._make_taggable_model('ipam')

        # Without the fix, Django's system checks raise fields.E304 on these two models.
        self.assertEqual(foo_a.check(), [])
        self.assertEqual(foo_b.check(), [])

        # Each model should resolve to its own unique related_name on the Tag relation.
        rn_a = foo_a._meta.get_field('tags').remote_field.related_name
        rn_b = foo_b._meta.get_field('tags').remote_field.related_name
        self.assertNotEqual(rn_a, rn_b)

    def test_deconstruct_emits_upstream_path(self):
        """
        NetBoxTaggableManagerField.deconstruct() must emit the upstream taggit path and drop
        related_name, so existing migrations remain valid and no AlterField is produced for
        every TagsMixin consumer.
        """
        model = self._make_taggable_model('dcim', name='DeconstructProbe')
        field = model._meta.get_field('tags')
        self.assertIsInstance(field, NetBoxTaggableManagerField)
        _name, path, _args, kwargs = field.deconstruct()
        self.assertEqual(path, 'taggit.managers.TaggableManager')
        self.assertNotIn('related_name', kwargs)
