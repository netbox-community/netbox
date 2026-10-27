import os
from unittest.mock import patch

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


class AssertExpectedQueryCountTestCase(TestCase):
    """
    Verify the baseline keys and the check modes of assert_expected_query_count.
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
            with patch.dict(os.environ, {'UPDATE_QUERY_COUNTS': '1', 'SKIP_QUERY_COUNTS': ''}):
                with assert_expected_query_count(test_case, 'test_name'):
                    pass
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

    def test_checks_enabled_by_default(self):
        """A count mismatch fails unless SKIP_QUERY_COUNTS is 1."""
        tc = self._make_test_case()
        with (
            patch.dict(os.environ, {'UPDATE_QUERY_COUNTS': ''}),
            patch.object(qc_mod, '_load_baseline', return_value={'fakemodel:test_name': 99}),
        ):
            os.environ.pop('SKIP_QUERY_COUNTS', None)
            with self.assertRaisesRegex(AssertionError, 'expected 99, got 0'):
                with assert_expected_query_count(tc, 'test_name'):
                    pass
            os.environ['SKIP_QUERY_COUNTS'] = '0'
            with self.assertRaisesRegex(AssertionError, 'expected 99, got 0'):
                with assert_expected_query_count(tc, 'test_name'):
                    pass

    def test_skip_mode_bypasses_checks(self):
        """SKIP_QUERY_COUNTS=1 runs the block unchecked, also for a missing key and under --parallel."""
        tc = self._make_test_case()
        ran = []
        with (
            patch.dict(os.environ, {'UPDATE_QUERY_COUNTS': '', 'SKIP_QUERY_COUNTS': '1'}),
            patch.object(qc_mod, '_load_baseline', return_value={'fakemodel:test_name': 99}) as load_baseline,
            patch.object(qc_mod, '_is_parallel_test_run', return_value=True),
        ):
            with assert_expected_query_count(tc, 'test_name'):
                ran.append('test_name')
            with assert_expected_query_count(tc, 'unrecorded'):
                ran.append('unrecorded')
        self.assertEqual(ran, ['test_name', 'unrecorded'])
        load_baseline.assert_not_called()

    def test_skip_mode_rejects_update_mode(self):
        """Combining SKIP_QUERY_COUNTS and UPDATE_QUERY_COUNTS raises before the block runs."""
        tc = self._make_test_case()
        ran = []
        with (
            patch.dict(os.environ, {'UPDATE_QUERY_COUNTS': '1', 'SKIP_QUERY_COUNTS': '1'}),
            patch.object(qc_mod, '_record_update') as record_update,
        ):
            with self.assertRaisesRegex(RuntimeError, 'SKIP_QUERY_COUNTS=1 cannot be combined'):
                with assert_expected_query_count(tc, 'test_name'):
                    ran.append('test_name')
        self.assertEqual(ran, [])
        record_update.assert_not_called()
