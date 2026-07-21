import os
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from utilities.release import RELEASE_PATH, _find_release_base_path, load_release_data


class ReleaseDataTestCase(TestCase):
    def test_find_release_base_path_locates_release_yaml(self):
        """The resolved base path contains release.yaml in a source checkout."""
        base_path = _find_release_base_path()
        self.assertTrue(os.path.isfile(os.path.join(base_path, RELEASE_PATH)))

    def test_find_release_base_path_raises_when_release_yaml_missing(self):
        """Neither a checkout release.yaml nor a bundled _data copy resolves."""
        with (
            patch('utilities.release.os.path.isfile', return_value=False),
            patch('utilities.release.importlib.util.find_spec', return_value=None),
        ):
            with self.assertRaisesMessage(ImproperlyConfigured, RELEASE_PATH):
                _find_release_base_path()

    def test_load_release_data_returns_version(self):
        """Release data loads and exposes a non-empty version string."""
        release = load_release_data()
        self.assertTrue(release.version)
        self.assertTrue(release.full_version)
