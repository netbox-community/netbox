from unittest import skipIf

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from taggit.models import Tag

from core.models import AutoSyncRecord, DataSource
from dcim.models import Site
from extras.models import CustomLink
from ipam.models import Prefix
from netbox.models.features import get_model_features, has_feature, model_is_public


class ModelFeaturesTestCase(TestCase):
    """
    A test case class for verifying model features and utility functions.
    """

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, 'dummy_plugin not in settings.PLUGINS')
    def test_model_is_public(self):
        """
        Test that the is_public() utility function returns True for public models only.
        """
        from netbox.tests.dummy_plugin.models import DummyModel

        # Public model
        self.assertFalse(hasattr(DataSource, '_netbox_private'))
        self.assertTrue(model_is_public(DataSource))

        # Private model
        self.assertTrue(getattr(AutoSyncRecord, '_netbox_private'))
        self.assertFalse(model_is_public(AutoSyncRecord))

        # Plugin model
        self.assertFalse(hasattr(DummyModel, '_netbox_private'))
        self.assertTrue(model_is_public(DummyModel))

        # Non-core model
        self.assertFalse(hasattr(Tag, '_netbox_private'))
        self.assertFalse(model_is_public(Tag))

    def test_has_feature(self):
        """
        Test the functionality of the has_feature() utility function.
        """
        # Sanity checking
        self.assertTrue(hasattr(DataSource, 'bookmarks'), "Invalid test?")
        self.assertFalse(hasattr(AutoSyncRecord, 'bookmarks'), "Invalid test?")

        self.assertTrue(has_feature(DataSource, 'bookmarks'))
        self.assertFalse(has_feature(AutoSyncRecord, 'bookmarks'))

    def test_get_model_features(self):
        """
        Check that get_model_features() returns the expected features for a model.
        """
        # Sanity checking
        self.assertTrue(hasattr(CustomLink, 'clone'), "Invalid test?")
        self.assertFalse(hasattr(CustomLink, 'bookmarks'), "Invalid test?")

        features = get_model_features(CustomLink)
        self.assertIn('cloning', features)
        self.assertNotIn('bookmarks', features)

    def test_cloningmixin_emits_gfk_subwidget_params(self):
        """A cloned GFK is exposed as the GenericObjectChoiceField subwidget params."""
        site = Site.objects.create(name='Test Site', slug='test-site')
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=site)

        attrs = prefix.clone()

        content_type = ContentType.objects.get_for_model(Site)
        self.assertEqual(attrs['scope_content_type'], content_type.pk)
        self.assertEqual(attrs['scope_object_id'], site.pk)
        # The bare GFK name and the raw model fields are not emitted.
        self.assertNotIn('scope', attrs)
        self.assertNotIn('scope_type', attrs)
        self.assertNotIn('scope_id', attrs)

    def test_cloningmixin_omits_unset_gfk(self):
        """An unset GFK contributes no params to the clone output."""
        prefix = Prefix.objects.create(prefix='10.0.0.0/24')

        attrs = prefix.clone()

        self.assertNotIn('scope_content_type', attrs)
        self.assertNotIn('scope_object_id', attrs)
        self.assertNotIn('scope', attrs)
