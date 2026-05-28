import os

from django.test import TestCase

import utilities.testing.query_counts as qc_mod
from utilities.testing.query_counts import assert_expected_query_count


class _FakeModel:
    """Minimal stand-in for a Django model class with _meta."""

    class _meta:
        app_label = 'utilities'
        model_name = 'fakemodel'


class _BaseTestCase:
    """Shared base for fake test-case objects passed to assert_expected_query_count."""
    model = _FakeModel


class AssertExpectedQueryCountLabelTestCase(TestCase):
    """
    Verify that assert_expected_query_count uses query_count_model_label when
    set on the test case and falls back to model._meta.model_name otherwise.
    """

    def _make_test_case(self, label_value=None, set_attr=False):
        """Return a minimal fake test case object."""
        tc = type('FakeTestCase', (_BaseTestCase,), {'fail': self.fail})()
        if set_attr:
            tc.query_count_model_label = label_value
        return tc

    def _recorded_key(self, test_case):
        """
        Drive assert_expected_query_count in UPDATE mode and return the key it
        wrote.  We patch _record_update to capture the key without touching the
        filesystem.
        """
        captured = {}

        original = qc_mod._record_update

        def fake_record(app_label, key, count):
            captured['key'] = key

        original_parallel = qc_mod._is_parallel_test_run
        qc_mod._record_update = fake_record
        qc_mod._is_parallel_test_run = lambda: False
        try:
            old_env = os.environ.get(qc_mod.UPDATE_ENV_VAR)
            os.environ[qc_mod.UPDATE_ENV_VAR] = '1'
            try:
                with assert_expected_query_count(test_case, 'test_name'):
                    pass
            finally:
                if old_env is None:
                    del os.environ[qc_mod.UPDATE_ENV_VAR]
                else:
                    os.environ[qc_mod.UPDATE_ENV_VAR] = old_env
        finally:
            qc_mod._record_update = original
            qc_mod._is_parallel_test_run = original_parallel

        return captured['key']

    def test_default_uses_model_name(self):
        """Without query_count_model_label the key prefix is model._meta.model_name."""
        tc = self._make_test_case()
        key = self._recorded_key(tc)
        self.assertEqual(key, 'fakemodel:test_name')

    def test_custom_label_overrides_model_name(self):
        """A set query_count_model_label is used as the key prefix."""
        tc = self._make_test_case(label_value='my-stable-label', set_attr=True)
        key = self._recorded_key(tc)
        self.assertEqual(key, 'my-stable-label:test_name')

    def test_empty_string_label_is_used_as_prefix(self):
        """An empty-string query_count_model_label is used as-is, not treated as falsy."""
        tc = self._make_test_case(label_value='', set_attr=True)
        key = self._recorded_key(tc)
        self.assertEqual(key, ':test_name')
