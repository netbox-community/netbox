from django.core import serializers
from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from dcim.choices import SiteStatusChoices
from dcim.models import Site
from extras.choices import CustomFieldChoiceSetBaseChoices
from extras.models import CustomFieldChoiceSet, Tag
from utilities.serialization import deserialize_object, serialize_object


class SerializationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        tags = (
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2'),
            Tag(name='Tag 3', slug='tag-3'),
        )
        Tag.objects.bulk_create(tags)

    def test_serialize_object(self):
        site = Site.objects.create(
            name='Site 1',
            slug='site=1',
            description='Ignore me',
        )
        site.tags.set(Tag.objects.all())

        data = serialize_object(site, extra={'foo': 123}, exclude=['description'])
        self.assertEqual(data['name'], site.name)
        self.assertEqual(data['slug'], site.slug)
        self.assertEqual(data['tags'], [tag.name for tag in Tag.objects.all()])
        self.assertEqual(data['foo'], 123)
        self.assertNotIn('description', data)

    def test_serialize_object_empty_array_field_subclass(self):
        """An empty ArrayField subclass value serializes as a list, not a string."""
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Choice Set 1',
            base_choices=CustomFieldChoiceSetBaseChoices.IATA,
            extra_choices=[],
        )
        data = serialize_object(choice_set)
        self.assertEqual(data['extra_choices'], [])

    def test_deserialize_object(self):
        data = {
            'name': 'Site 1',
            'slug': 'site-1',
            'tags': ['Tag 1', 'Tag 2', 'Tag 3'],
            'foo': 123,
        }

        instance = deserialize_object(Site, data, pk=123)
        self.assertEqual(instance.object.pk, 123)
        self.assertEqual(instance.object.name, data['name'])
        self.assertEqual(instance.object.slug, data['slug'])
        self.assertEqual(instance.object.status, SiteStatusChoices.STATUS_ACTIVE)  # Default field value
        self.assertEqual(instance.object.foo, data['foo'])  # Non-field attribute
        self.assertEqual(list(instance.m2m_data['tags']), list(Tag.objects.all()))

    def test_deserialized_object_save(self):
        """A deserialized object saves and reassigns its tags (Django 6.1 calls set_base())."""
        data = {
            'name': 'Site 1',
            'slug': 'site-1',
            'tags': ['Tag 1', 'Tag 2'],
        }
        deserialize_object(Site, data, pk=123).save()

        site = Site.objects.get(pk=123)
        self.assertEqual(site.name, data['name'])
        self.assertEqual(sorted(site.tags.values_list('name', flat=True)), data['tags'])

    def test_deserialized_object_save_with_empty_tag_list(self):
        """
        An empty `tags` list still reaches set_base(): deserialize_object() only pops the key
        when it is non-empty, so Django populates m2m_data['tags'] with an empty list. (Data
        carrying no `tags` key at all would not populate m2m_data, and so would not exercise
        set_base() — keep the empty list explicit.)
        """
        deserialize_object(Site, {'name': 'Site 2', 'slug': 'site-2', 'tags': []}, pk=124).save()

        site = Site.objects.get(pk=124)
        self.assertEqual(site.name, 'Site 2')
        self.assertEqual(site.tags.count(), 0)

    def test_deserialized_object_save_with_tag_pks(self):
        """Django's deserializer resolves M2M values to primary keys; set_base() must take them."""
        tags = list(Tag.objects.all()[:2])
        data = [{
            'model': 'dcim.site',
            'pk': 125,
            'fields': {'name': 'Site 3', 'slug': 'site-3', 'tags': [tag.pk for tag in tags]},
        }]
        list(serializers.deserialize('python', data))[0].save()

        site = Site.objects.get(pk=125)
        self.assertEqual(sorted(site.tags.values_list('pk', flat=True)), sorted(tag.pk for tag in tags))

    def test_deserialized_object_save_with_unknown_tag_pk(self):
        """A key matching no tag is left for the database to reject."""
        data = [{
            'model': 'dcim.site',
            'pk': 126,
            'fields': {'name': 'Site 4', 'slug': 'site-4', 'tags': [99999]},
        }]
        with transaction.atomic():
            list(serializers.deserialize('python', data))[0].save()
            with self.assertRaises(IntegrityError):
                connection.check_constraints()
            transaction.set_rollback(True)
