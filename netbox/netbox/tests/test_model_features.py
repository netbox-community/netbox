from django.test import TestCase

from core.models import AutoSyncRecord, DataSource
from extras.models import CustomLink
from netbox.models.features import get_model_features, has_feature, model_is_public
from netbox.tests.dummy_plugin.models import DummyModel
from taggit.models import Tag


class ModelFeaturesTestCase(TestCase):

    def test_model_is_public(self):
        """
        Test that the is_public() utility function returns True for public models only.
        """
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
