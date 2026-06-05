import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import requests
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone

from core.choices import DataSourceStatusChoices
from core.jobs import SyncDataSourceJob, SystemHousekeepingJob
from core.models import DataFile, DataSource, Job


def _make_runner(cls, **job_attrs):
    """
    Build a JobRunner without going through ``__init__``.

    ``JobRunner.__init__`` attaches a ``JobLogHandler`` to a module-level
    singleton logger, so calling it once per test would accumulate handlers
    across the suite. Bypass it and stub the logger directly.
    """
    runner = cls.__new__(cls)
    runner.job = MagicMock(**job_attrs)
    runner.logger = MagicMock()
    return runner


class HousekeepingRunnerMixin:
    """Provides a `_runner()` helper that builds a SystemHousekeepingJob with a mock job."""

    @staticmethod
    def _runner():
        return _make_runner(SystemHousekeepingJob)


class SyncDataSourceJobTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.datasource = DataSource.objects.create(
            name='Test Source',
            type='local',
            source_url='/tmp/test',
        )

    def test_enqueue_sets_datasource_status_to_queued(self):
        job = MagicMock()
        job.object = self.datasource

        with patch('core.models.Job.enqueue', return_value=job):
            result = SyncDataSourceJob.enqueue(instance=self.datasource)

        self.assertIs(result, job)
        # Verify both the in-memory assignment (`datasource.status = ...`) and the
        # persisted update (`DataSource.objects.filter(pk=...).update(...)`).
        self.assertEqual(self.datasource.status, DataSourceStatusChoices.QUEUED)
        self.datasource.refresh_from_db()
        self.assertEqual(self.datasource.status, DataSourceStatusChoices.QUEUED)

    def test_enqueue_without_object_is_noop(self):
        # Baseline: the datasource starts at NEW. (Captures setUpTestData drift.)
        self.assertEqual(self.datasource.status, DataSourceStatusChoices.NEW)

        job = MagicMock()
        job.object = None

        with (
            patch('core.models.Job.enqueue', return_value=job),
            patch(
                'core.jobs.DataSource.objects.filter',
                wraps=DataSource.objects.filter,
            ) as filter_,
        ):
            result = SyncDataSourceJob.enqueue()

        self.assertIs(result, job)
        # Intent: the `if datasource := job.object` branch was skipped, so no
        # filter().update() call was even attempted.
        filter_.assert_not_called()
        # Outcome: no side effect on any existing DataSource.
        self.datasource.refresh_from_db()
        self.assertEqual(self.datasource.status, DataSourceStatusChoices.NEW)

    def test_run_syncs_datasource_and_updates_search_cache(self):
        datafile = DataFile.objects.create(
            source=self.datasource,
            path='test.txt',
            last_updated=timezone.now(),
            size=4,
            hash='0' * 64,
            data=b'test',
        )
        runner = _make_runner(SyncDataSourceJob, object_id=self.datasource.pk)

        with (
            patch('core.models.DataSource.sync') as sync,
            patch('core.jobs.search_backend.cache') as cache,
        ):
            runner.run()

        sync.assert_called_once_with()
        cache.assert_called_once()
        # The cache argument should iterate over the datasource's data files.
        cache_arg = cache.call_args.args[0]
        self.assertEqual(list(cache_arg), [datafile])

    def test_run_marks_datasource_failed_and_reraises_on_sync_error(self):
        runner = _make_runner(SyncDataSourceJob, object_id=self.datasource.pk)

        with (
            patch('core.models.DataSource.sync', side_effect=RuntimeError('boom')),
            patch('core.jobs.search_backend.cache') as cache,
        ):
            with self.assertRaisesMessage(RuntimeError, 'boom'):
                runner.run()

        self.datasource.refresh_from_db()
        self.assertEqual(self.datasource.status, DataSourceStatusChoices.FAILED)
        cache.assert_not_called()

    def test_run_raises_when_datasource_no_longer_exists(self):
        # If the DataSource was deleted between enqueue and run, the initial lookup
        # raises DoesNotExist; the framework will surface it as a job error.
        runner = _make_runner(SyncDataSourceJob, object_id=99_999_999)

        with self.assertRaises(DataSource.DoesNotExist):
            runner.run()


class SystemHousekeepingRunTestCase(HousekeepingRunnerMixin, TestCase):
    SUBMETHODS = (
        'send_census_report',
        'clear_expired_sessions',
        'prune_changelog',
        'delete_expired_jobs',
        'check_for_new_releases',
    )

    @override_settings(DEBUG=True)
    def test_run_skips_when_debug_is_enabled(self):
        # DEBUG is checked before sys.argv; sys.argv is irrelevant here.
        runner = self._runner()
        patches = {name: patch.object(SystemHousekeepingJob, name) for name in self.SUBMETHODS}
        mocks = {name: p.start() for name, p in patches.items()}
        self.addCleanup(lambda: [p.stop() for p in patches.values()])

        runner.run()

        for mock in mocks.values():
            mock.assert_not_called()

    @override_settings(DEBUG=False)
    def test_run_skips_during_test_invocation(self):
        runner = self._runner()
        patches = {name: patch.object(SystemHousekeepingJob, name) for name in self.SUBMETHODS}
        mocks = {name: p.start() for name, p in patches.items()}
        self.addCleanup(lambda: [p.stop() for p in patches.values()])

        with patch('core.jobs.sys.argv', ['manage.py', 'test']):
            runner.run()

        for mock in mocks.values():
            mock.assert_not_called()

    @override_settings(DEBUG=False)
    def test_run_executes_all_housekeeping_tasks(self):
        runner = self._runner()
        patches = {name: patch.object(SystemHousekeepingJob, name) for name in self.SUBMETHODS}
        mocks = {name: p.start() for name, p in patches.items()}
        self.addCleanup(lambda: [p.stop() for p in patches.values()])

        with patch('core.jobs.sys.argv', ['netbox']):
            runner.run()

        for mock in mocks.values():
            mock.assert_called_once_with()


class SendCensusReportTestCase(HousekeepingRunnerMixin, TestCase):
    @override_settings(ISOLATED_DEPLOYMENT=True)
    def test_send_census_report_skips_when_isolated_deployment(self):
        with patch('core.jobs.requests.get') as get:
            self._runner().send_census_report()
        get.assert_not_called()

    @override_settings(ISOLATED_DEPLOYMENT=False, CENSUS_REPORTING_ENABLED=False)
    def test_send_census_report_skips_when_reporting_disabled(self):
        with patch('core.jobs.requests.get') as get:
            self._runner().send_census_report()
        get.assert_not_called()

    @override_settings(
        ISOLATED_DEPLOYMENT=False,
        CENSUS_REPORTING_ENABLED=True,
        CENSUS_URL='https://census.example/',
        DEPLOYMENT_ID='abc123',
    )
    def test_send_census_report_sends_expected_payload(self):
        with (
            patch('core.jobs.requests.get') as get,
            patch('core.jobs.resolve_proxies', return_value={'https': 'proxy'}) as resolve,
        ):
            self._runner().send_census_report()

        resolve.assert_called_once_with(url='https://census.example/')
        get.assert_called_once()
        kwargs = get.call_args.kwargs
        self.assertEqual(kwargs['url'], 'https://census.example/')
        self.assertEqual(kwargs['timeout'], 3)
        self.assertEqual(kwargs['proxies'], {'https': 'proxy'})
        self.assertEqual(kwargs['params']['deployment_id'], 'abc123')
        self.assertIn('version', kwargs['params'])
        self.assertIn('python_version', kwargs['params'])

    @override_settings(
        ISOLATED_DEPLOYMENT=False,
        CENSUS_REPORTING_ENABLED=True,
        CENSUS_URL='https://census.example/',
    )
    def test_send_census_report_swallows_request_exception(self):
        with (
            patch('core.jobs.requests.get', side_effect=requests.RequestException('down')),
            patch('core.jobs.resolve_proxies', return_value={}),
        ):
            self._runner().send_census_report()  # must not raise


class ClearExpiredSessionsTestCase(HousekeepingRunnerMixin, TestCase):
    def test_clear_expired_sessions_calls_session_store(self):
        engine = MagicMock()
        with patch('core.jobs.import_module', return_value=engine) as import_module:
            self._runner().clear_expired_sessions()

        import_module.assert_called_once_with(settings.SESSION_ENGINE)
        engine.SessionStore.clear_expired.assert_called_once_with()

    def test_clear_expired_sessions_handles_not_implemented(self):
        engine = MagicMock()
        engine.SessionStore.clear_expired.side_effect = NotImplementedError
        runner = self._runner()

        with patch('core.jobs.import_module', return_value=engine):
            runner.clear_expired_sessions()  # must not raise

        runner.logger.warning.assert_called_once()
        self.assertIn(
            'does not support',
            runner.logger.warning.call_args.args[0],
        )


class DeleteExpiredJobsTestCase(HousekeepingRunnerMixin, TestCase):
    def test_delete_expired_jobs_skips_when_retention_unset(self):
        old_job = Job.objects.create(name='old', job_id=uuid.uuid4())
        Job.objects.filter(pk=old_job.pk).update(created=timezone.now() - timedelta(days=365))

        with patch('core.jobs.Config') as config_cls:
            config_cls.return_value.JOB_RETENTION = 0
            self._runner().delete_expired_jobs()

        self.assertTrue(Job.objects.filter(pk=old_job.pk).exists())

    def test_delete_expired_jobs_deletes_only_jobs_older_than_retention(self):
        old_job = Job.objects.create(name='old', job_id=uuid.uuid4())
        recent_job = Job.objects.create(name='recent', job_id=uuid.uuid4())
        Job.objects.filter(pk=old_job.pk).update(created=timezone.now() - timedelta(days=30))
        Job.objects.filter(pk=recent_job.pk).update(created=timezone.now() - timedelta(hours=1))

        with patch('core.jobs.Config') as config_cls:
            config_cls.return_value.JOB_RETENTION = 7
            self._runner().delete_expired_jobs()

        self.assertFalse(Job.objects.filter(pk=old_job.pk).exists())
        self.assertTrue(Job.objects.filter(pk=recent_job.pk).exists())


class CheckForNewReleasesTestCase(HousekeepingRunnerMixin, TestCase):
    @override_settings(ISOLATED_DEPLOYMENT=True)
    def test_check_for_new_releases_skips_when_isolated(self):
        with patch('core.jobs.requests.get') as get:
            self._runner().check_for_new_releases()
        get.assert_not_called()

    @override_settings(ISOLATED_DEPLOYMENT=False, RELEASE_CHECK_URL=None)
    def test_check_for_new_releases_skips_when_url_unset(self):
        with patch('core.jobs.requests.get') as get:
            self._runner().check_for_new_releases()
        get.assert_not_called()

    @override_settings(ISOLATED_DEPLOYMENT=False, RELEASE_CHECK_URL='https://api.example/')
    def test_check_for_new_releases_handles_request_exception(self):
        with (
            patch('core.jobs.requests.get', side_effect=requests.RequestException('down')),
            patch('core.jobs.cache') as cache,
            patch('core.jobs.resolve_proxies', return_value={}),
        ):
            self._runner().check_for_new_releases()

        cache.set.assert_not_called()

    @override_settings(ISOLATED_DEPLOYMENT=False, RELEASE_CHECK_URL='https://api.example/')
    def test_check_for_new_releases_handles_no_stable_releases(self):
        # All entries are filtered out (prereleases, devreleases, or missing tag_name);
        # check_for_new_releases() must not crash on the resulting empty list.
        response = MagicMock()
        response.json.return_value = [
            {'tag_name': 'v4.7.0-rc1', 'html_url': 'https://example/rc', 'prerelease': True},
            {'tag_name': 'v4.7.0-dev', 'html_url': 'https://example/dev', 'devrelease': True},
            {'html_url': 'https://example/no-tag'},
        ]

        with (
            patch('core.jobs.requests.get', return_value=response),
            patch('core.jobs.cache.set') as cache_set,
            patch('core.jobs.resolve_proxies', return_value={}),
        ):
            self._runner().check_for_new_releases()

        cache_set.assert_not_called()

    @override_settings(ISOLATED_DEPLOYMENT=False, RELEASE_CHECK_URL='https://api.example/')
    def test_check_for_new_releases_caches_latest_stable_release(self):
        response = MagicMock()
        response.json.return_value = [
            {'tag_name': 'v4.5.0', 'html_url': 'https://example/4.5.0'},
            {'tag_name': 'v4.6.0', 'html_url': 'https://example/4.6.0'},
            {'tag_name': 'v4.7.0-rc1', 'html_url': 'https://example/rc', 'prerelease': True},
            {'tag_name': 'v4.7.0-dev', 'html_url': 'https://example/dev', 'devrelease': True},
            {'html_url': 'https://example/no-tag'},
        ]

        with (
            patch('core.jobs.requests.get', return_value=response) as get,
            patch('core.jobs.cache.set') as cache_set,
            patch('core.jobs.resolve_proxies', return_value={'http': 'proxy'}) as resolve,
        ):
            self._runner().check_for_new_releases()

        # HTTP request: URL, GitHub API Accept header, resolved proxies.
        resolve.assert_called_once_with(url='https://api.example/')
        get.assert_called_once_with(
            url='https://api.example/',
            headers={'Accept': 'application/vnd.github.v3+json'},
            proxies={'http': 'proxy'},
        )
        response.raise_for_status.assert_called_once_with()

        cache_set.assert_called_once()
        # Accept either positional or keyword form for cache.set(key, value, ttl).
        call = cache_set.call_args
        bound = {**dict(zip(('key', 'value', 'timeout'), call.args)), **call.kwargs}
        self.assertEqual(bound['key'], 'latest_release')
        self.assertIsNone(bound['timeout'])
        latest_version, latest_url = bound['value']
        self.assertEqual(str(latest_version), '4.6.0')
        self.assertEqual(latest_url, 'https://example/4.6.0')


class PruneChangelogTestCase(HousekeepingRunnerMixin, TestCase):
    def test_prune_changelog_skips_when_retention_unset(self):
        with (
            patch('core.jobs.Config') as config_cls,
            patch('core.jobs.ObjectChange') as object_change,
        ):
            config_cls.return_value.CHANGELOG_RETENTION = None
            self._runner().prune_changelog()

        object_change.objects.filter.assert_not_called()

    def test_prune_changelog_uses_strict_cutoff_filter(self):
        # Implementation pin: prune_changelog must use time__lt (strict less-than) so a
        # record exactly at the cutoff is retained. End-to-end behavior of the prune is
        # covered by ChangelogPruneRetentionTestCase in core/tests/test_changelog.py.
        with (
            patch('core.jobs.Config') as config_cls,
            patch('core.jobs.ObjectChange') as object_change,
            patch('core.jobs.timezone') as tz,
        ):
            config_cls.return_value.CHANGELOG_RETENTION = 7
            config_cls.return_value.CHANGELOG_RETAIN_CREATE_LAST_UPDATE = False
            tz.now.return_value = timezone.datetime(2026, 1, 8, tzinfo=timezone.get_current_timezone())
            object_change.objects.filter.return_value.delete.return_value = (0, {})

            self._runner().prune_changelog()

        expected_cutoff = timezone.datetime(2026, 1, 1, tzinfo=timezone.get_current_timezone())
        object_change.objects.filter.assert_called_once_with(time__lt=expected_cutoff)
