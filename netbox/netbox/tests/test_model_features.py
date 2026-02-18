from unittest import skipIf

from django.conf import settings
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

    def test_cloningmixin_injects_gfk_attribute(self):
        """
        Tests the cloning mixin with GFK attribute injection in the `clone` method.

        This test validates that the `clone` method correctly handles
        and retains the General Foreign Key (GFK) attributes on an
        object when the cloning fields are explicitly defined.
        """
        site = Site.objects.create(name='Test Site', slug='test-site')
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=site)

        original_clone_fields = getattr(Prefix, 'clone_fields', None)
        try:
            Prefix.clone_fields = ('scope_type', 'scope_id')
            attrs = prefix.clone()

            self.assertEqual(attrs['scope_type'], prefix.scope_type_id)
            self.assertEqual(attrs['scope_id'], prefix.scope_id)
            self.assertEqual(attrs['scope'], prefix.scope_id)
        finally:
            if original_clone_fields is None:
                delattr(Prefix, 'clone_fields')
            else:
                Prefix.clone_fields = original_clone_fields

    def test_cloningmixin_does_not_inject_gfk_attribute_if_incomplete(self):
        """
        Tests the cloning mixin with incomplete cloning fields does not inject the GFK attribute.

        This test validates that the `clone` method correctly handles
        the case where the cloning fields are incomplete, ensuring that
        the generic foreign key (GFK) attribute is not injected during
        the cloning process.
        """
        site = Site.objects.create(name='Test Site', slug='test-site')
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=site)

        original_clone_fields = getattr(Prefix, 'clone_fields', None)
        try:
            Prefix.clone_fields = ('scope_type',)
            attrs = prefix.clone()

            self.assertIn('scope_type', attrs)
            self.assertNotIn('scope', attrs)
        finally:
            if original_clone_fields is None:
                delattr(Prefix, 'clone_fields')
            else:
                Prefix.clone_fields = original_clone_fields
