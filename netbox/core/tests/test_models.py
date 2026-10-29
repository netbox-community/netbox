import tempfile
import uuid
from contextlib import contextmanager
from datetime import timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command
from django.db import IntegrityError, connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from core.choices import DataSourceStatusChoices, JobNotificationChoices, JobStatusChoices, ObjectChangeActionChoices
from core.data_backends import LocalBackend
from core.exceptions import SyncError
from core.models import AutoSyncRecord, DataFile, DataSource, Job, ObjectType
from core.signals import post_sync
from dcim.models import Device, Location, Site
from extras.models import ConfigTemplate, Notification
from netbox.constants import CENSOR_TOKEN, CENSOR_TOKEN_CHANGED
from users.models import User
from utilities.querysets import RestrictedQuerySet
from utilities.testing import PinnedConnectionRouter


class DataSourceTestCase(TestCase):

    def setUp(self):
        # A synced local source, used by the sync tests
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        (self.root / 'a.txt').write_text('old\n')
        (self.root / 'obsolete.txt').write_text('old\n')
        self.datasource = DataSource.objects.create(name='Data Source 2', type='local', source_url=self.root.as_uri())
        self.datasource.sync()
        self.original_files = list(self.datasource.datafiles.values())
        self.last_synced = self.datasource.last_synced

        # The next sync finds one file changed, one removed and one added
        (self.root / 'a.txt').write_text('new\n')
        (self.root / 'obsolete.txt').unlink()
        (self.root / 'b.txt').write_text('new\n')

    def assert_files_unchanged(self):
        self.assertEqual(list(self.datasource.datafiles.values()), self.original_files)
        self.datasource.refresh_from_db()
        self.assertEqual(self.datasource.last_synced, self.last_synced)

    def assert_files_synced(self):
        self.assertEqual(
            dict(self.datasource.datafiles.values_list('path', 'data')),
            {'a.txt': b'new\n', 'b.txt': b'new\n'},
        )
        self.datasource.refresh_from_db()
        self.assertEqual(self.datasource.status, DataSourceStatusChoices.COMPLETED)
        self.assertGreater(self.datasource.last_synced, self.last_synced)

    def test_no_ignore_rules(self):
        ds = DataSource(ignore_rules='')
        self.assertFalse(ds._ignore('README.md'))
        self.assertFalse(ds._ignore('subdir/file.py'))

    def test_ignore_by_filename(self):
        ds = DataSource(ignore_rules='*.txt')
        self.assertTrue(ds._ignore('notes.txt'))
        self.assertTrue(ds._ignore('subdir/notes.txt'))
        self.assertFalse(ds._ignore('notes.py'))

    def test_ignore_by_subdirectory(self):
        ds = DataSource(ignore_rules='dev/*')
        self.assertTrue(ds._ignore('dev/README.md'))
        self.assertTrue(ds._ignore('dev/script.py'))
        self.assertFalse(ds._ignore('prod/script.py'))

    def test_password_added_on_create(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/',
            parameters={
                'username': 'jeff',
                'password': 'foobar123',
            }
        )

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_CREATE)
        self.assertIsNone(objectchange.prechange_data)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN_CHANGED)

    def test_password_added_on_update(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/'
        )
        datasource.snapshot()

        # Add a blank password
        datasource.parameters = {
            'username': 'jeff',
            'password': '',
        }

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertIsNone(objectchange.prechange_data['parameters'])
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], '')

        # Add a password
        datasource.parameters = {
            'username': 'jeff',
            'password': 'foobar123',
        }

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN_CHANGED)

    def test_password_changed(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/',
            parameters={
                'username': 'jeff',
                'password': 'password1',
            }
        )
        datasource.snapshot()

        # Change the password
        datasource.parameters['password'] = 'password2'

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.prechange_data['parameters']['password'], CENSOR_TOKEN)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN_CHANGED)

    def test_password_removed_on_update(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/',
            parameters={
                'username': 'jeff',
                'password': 'foobar123',
            }
        )
        datasource.snapshot()

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.prechange_data['parameters']['password'], CENSOR_TOKEN)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN)

        # Remove the password
        datasource.parameters['password'] = ''

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.prechange_data['parameters']['password'], CENSOR_TOKEN)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'jeff')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], '')

    def test_password_not_modified(self):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='git',
            source_url='http://localhost/',
            parameters={
                'username': 'username1',
                'password': 'foobar123',
            }
        )
        datasource.snapshot()

        # Remove the password
        datasource.parameters['username'] = 'username2'

        objectchange = datasource.to_objectchange(ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(objectchange.prechange_data['parameters']['username'], 'username1')
        self.assertEqual(objectchange.prechange_data['parameters']['password'], CENSOR_TOKEN)
        self.assertEqual(objectchange.postchange_data['parameters']['username'], 'username2')
        self.assertEqual(objectchange.postchange_data['parameters']['password'], CENSOR_TOKEN)

    def test_sync_rolls_back_read_failure(self):
        """A sync that fails reading a new file keeps the synced files and their links."""
        obsolete = self.datasource.datafiles.get(path='obsolete.txt')
        template = ConfigTemplate.objects.create(
            name='Config Template 1',
            data_source=self.datasource,
            data_file=obsolete,
            data_path=obsolete.path,
            template_code='old\n',
            auto_sync_enabled=True,
        )
        autosync = AutoSyncRecord.objects.get(datafile=obsolete)
        (self.root / 'link.txt').symlink_to('missing.txt')

        with patch.object(post_sync, 'send') as send:
            with self.assertRaises(FileNotFoundError):
                call_command('syncdatasource', self.datasource.name, stdout=StringIO())

        self.assert_files_unchanged()
        self.assertEqual(self.datasource.status, DataSourceStatusChoices.FAILED)
        template.refresh_from_db()
        self.assertEqual(template.data_file_id, obsolete.pk)
        self.assertTrue(AutoSyncRecord.objects.filter(pk=autosync.pk, datafile=obsolete).exists())
        send.assert_not_called()

    def test_sync_rolls_back_create_failure(self):
        """A sync that fails creating its new files keeps the synced files."""
        with patch.object(RestrictedQuerySet, 'bulk_create', side_effect=IntegrityError('Simulated bulk create error')):
            with self.assertRaisesMessage(IntegrityError, 'Simulated bulk create error'):
                self.datasource.sync()

        self.assert_files_unchanged()

    def test_sync_rolls_back_backend_cleanup_failure(self):
        """A sync whose backend fails during cleanup keeps the synced files."""

        @contextmanager
        def fetch(backend):
            yield str(self.root)
            raise OSError('Simulated cleanup error')

        with patch.object(LocalBackend, 'fetch', fetch):
            with self.assertRaisesMessage(OSError, 'Simulated cleanup error'):
                self.datasource.sync()

        self.assert_files_unchanged()

    def test_sync_locks_datasource_before_reading_files(self):
        """Take the sync lock inside the transaction, before the files are read and the sync completes."""
        with CaptureQueriesContext(connection) as context:
            self.datasource.sync()

        queries = [query['sql'] for query in context.captured_queries]
        begins = [i for i, sql in enumerate(queries) if sql.startswith('SAVEPOINT')]
        locks = [i for i, sql in enumerate(queries) if 'pg_advisory_xact_lock' in sql]
        reads = [i for i, sql in enumerate(queries) if sql.startswith('SELECT') and 'FROM "core_datafile"' in sql]
        completions = [
            i for i, sql in enumerate(queries) if sql.startswith('UPDATE "core_datasource"') and "'completed'" in sql
        ]
        commits = [i for i, sql in enumerate(queries) if sql.startswith('RELEASE SAVEPOINT')]
        self.assertTrue(locks)
        self.assertLess(begins[0], locks[0])
        self.assertLess(locks[0], reads[0])
        self.assertLess(reads[0], completions[0])
        self.assertLess(completions[0], commits[0])

    def test_post_sync_failure_preserves_synced_files(self):
        """A failing post_sync receiver leaves the completed sync in place."""
        with patch.object(post_sync, 'send', side_effect=SyncError('Simulated post_sync error')):
            with self.assertRaisesMessage(SyncError, 'Simulated post_sync error'):
                self.datasource.sync()

        self.assert_files_synced()

    def test_sync_pins_datafile_queries_to_transaction_connection(self):
        """Run the data file reads, updates and deletes of a sync on its transaction's connection."""
        # Django routes a new data file's construction and validation itself
        (self.root / 'b.txt').unlink()

        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(DataFile)]):
            self.datasource.sync()

        self.assertEqual(dict(self.datasource.datafiles.values_list('path', 'data')), {'a.txt': b'new\n'})

    def test_sync_keeps_paths_repeating_source_root(self):
        """A file below a directory repeating the source root syncs under its full path."""
        # Repeat the whole root string below it, as /scripts/scripts_old does for /scripts
        nested_path = f'{self.root}_old/legacy.py'.lstrip('/')
        (self.root / nested_path).parent.mkdir(parents=True)
        (self.root / nested_path).write_text('nested\n')
        (self.root / 'legacy.py').write_text('root\n')

        self.datasource.sync()

        self.assertEqual(
            dict(self.datasource.datafiles.values_list('path', 'data')),
            {'a.txt': b'new\n', 'b.txt': b'new\n', 'legacy.py': b'root\n', nested_path: b'nested\n'},
        )


class ObjectTypeTestCase(TestCase):

    def test_create(self):
        """
        Test that an ObjectType created for a given app_label & model name will be automatically assigned to
        the appropriate ContentType.
        """
        kwargs = {
            'app_label': 'foo',
            'model': 'bar',
        }
        ct = ContentType.objects.create(**kwargs)
        ot = ObjectType.objects.create(**kwargs)
        self.assertEqual(ot.contenttype_ptr, ct)

    def test_get_by_natural_key(self):
        """
        Test that get_by_natural_key() returns the appropriate ObjectType.
        """
        self.assertEqual(
            ObjectType.objects.get_by_natural_key('dcim', 'site'),
            ObjectType.objects.get(app_label='dcim', model='site')
        )
        with self.assertRaises(ObjectDoesNotExist):
            ObjectType.objects.get_by_natural_key('foo', 'bar')

    def test_get_for_id(self):
        """
        Test that get_by_id() returns the appropriate ObjectType.
        """
        ot = ObjectType.objects.get_by_natural_key('dcim', 'site')
        self.assertEqual(
            ObjectType.objects.get_for_id(ot.pk),
            ObjectType.objects.get(pk=ot.pk)
        )
        with self.assertRaises(ObjectDoesNotExist):
            ObjectType.objects.get_for_id(0)

    def test_get_for_model(self):
        """
        Test that get_by_model() returns the appropriate ObjectType.
        """
        self.assertEqual(
            ObjectType.objects.get_for_model(Site),
            ObjectType.objects.get_by_natural_key('dcim', 'site')
        )

    def test_get_for_models(self):
        """
        Test that get_by_models() returns the appropriate ObjectType mapping.
        """
        self.assertEqual(
            ObjectType.objects.get_for_models(Site, Location, Device),
            {
                Site: ObjectType.objects.get_by_natural_key('dcim', 'site'),
                Location: ObjectType.objects.get_by_natural_key('dcim', 'location'),
                Device: ObjectType.objects.get_by_natural_key('dcim', 'device'),
            }
        )

    def test_public(self):
        """
        Test that public() returns only ObjectTypes for public models.
        """
        public_ots = ObjectType.objects.public()
        self.assertIn(ObjectType.objects.get_by_natural_key('dcim', 'site'), public_ots)
        self.assertNotIn(ObjectType.objects.get_by_natural_key('extras', 'taggeditem'), public_ots)

    def test_with_feature(self):
        """
        Test that with_feature() returns only ObjectTypes for models which support the specified feature.
        """
        bookmarks_ots = ObjectType.objects.with_feature('bookmarks')
        self.assertIn(ObjectType.objects.get_by_natural_key('dcim', 'site'), bookmarks_ots)
        self.assertNotIn(ObjectType.objects.get_by_natural_key('dcim', 'cabletermination'), bookmarks_ots)


class JobTestCase(TestCase):

    def _make_job(self, user, notifications):
        """
        Create and return a persisted Job with the given user and notifications setting.
        """
        return Job.objects.create(
            name='Test Job',
            job_id=uuid.uuid4(),
            user=user,
            notifications=notifications,
            status=JobStatusChoices.STATUS_RUNNING,
        )

    @patch('core.models.jobs.django_rq.get_queue')
    def test_delete_cancels_job_from_correct_queue(self, mock_get_queue):
        """
        Test that when a job is deleted, it's canceled from the correct queue.
        """
        mock_queue = MagicMock()
        mock_rq_job = MagicMock()
        mock_queue.fetch_job.return_value = mock_rq_job
        mock_get_queue.return_value = mock_queue

        def dummy_func(**kwargs):
            pass

        # Enqueue a job with a custom queue name
        custom_queue = 'my_custom_queue'
        job = Job.enqueue(
            func=dummy_func,
            name='Test Job',
            queue_name=custom_queue
        )

        # Reset mock to clear enqueue call
        mock_get_queue.reset_mock()

        # Delete the job
        job.delete()

        # Verify the correct queue was used for cancellation
        mock_get_queue.assert_called_with(custom_queue)
        mock_queue.fetch_job.assert_called_with(str(job.job_id))
        mock_rq_job.cancel.assert_called_once()

    @patch('core.models.jobs.job_end')
    def test_terminate_notification_always(self, mock_job_end):
        """
        With notifications=always, a Notification should be created for every
        terminal status (completed, failed, errored).
        """
        user = User.objects.create_user(username='notification-always')

        for status in (
            JobStatusChoices.STATUS_COMPLETED,
            JobStatusChoices.STATUS_FAILED,
            JobStatusChoices.STATUS_ERRORED,
        ):
            with self.subTest(status=status):
                job = self._make_job(user, JobNotificationChoices.NOTIFICATION_ALWAYS)
                job.terminate(status=status)
                self.assertEqual(
                    Notification.objects.filter(user=user, object_id=job.pk).count(),
                    1,
                    msg=f"Expected a notification for status={status} with notifications=always",
                )

    @patch('core.models.jobs.job_end')
    def test_terminate_notification_on_failure(self, mock_job_end):
        """
        With notifications=on_failure, a Notification should be created only for
        non-completed terminal statuses (failed, errored), not for completed.
        """
        user = User.objects.create_user(username='notification-on-failure')

        # No notification on successful completion
        job = self._make_job(user, JobNotificationChoices.NOTIFICATION_ON_FAILURE)
        job.terminate(status=JobStatusChoices.STATUS_COMPLETED)
        self.assertEqual(
            Notification.objects.filter(user=user, object_id=job.pk).count(),
            0,
            msg="Expected no notification for status=completed with notifications=on_failure",
        )

        # Notification on failure/error
        for status in (JobStatusChoices.STATUS_FAILED, JobStatusChoices.STATUS_ERRORED):
            with self.subTest(status=status):
                job = self._make_job(user, JobNotificationChoices.NOTIFICATION_ON_FAILURE)
                job.terminate(status=status)
                self.assertEqual(
                    Notification.objects.filter(user=user, object_id=job.pk).count(),
                    1,
                    msg=f"Expected a notification for status={status} with notifications=on_failure",
                )

    @patch('core.models.jobs.job_end')
    def test_terminate_notification_never(self, mock_job_end):
        """
        With notifications=never, no Notification should be created regardless
        of terminal status.
        """
        user = User.objects.create_user(username='notification-never')

        for status in (
            JobStatusChoices.STATUS_COMPLETED,
            JobStatusChoices.STATUS_FAILED,
            JobStatusChoices.STATUS_ERRORED,
        ):
            with self.subTest(status=status):
                job = self._make_job(user, JobNotificationChoices.NOTIFICATION_NEVER)
                job.terminate(status=status)
                self.assertEqual(
                    Notification.objects.filter(user=user, object_id=job.pk).count(),
                    0,
                    msg=f"Expected no notification for status={status} with notifications=never",
                )

    @patch('core.models.jobs.job_end')
    def test_execution_time_set_on_terminate(self, mock_job_end):
        """
        terminate() should set execution_time to (completed - started) for a started job.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        job.started = timezone.now() - timedelta(seconds=90)
        job.save()

        job.terminate(status=JobStatusChoices.STATUS_COMPLETED)

        self.assertIsNotNone(job.execution_time)
        self.assertEqual(job.execution_time, job.completed - job.started)

    @patch('core.models.jobs.job_end')
    def test_execution_time_none_before_completion(self, mock_job_end):
        """
        A job which has not completed should have a null execution_time.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        self.assertIsNone(job.execution_time)

    @patch('core.models.jobs.job_end')
    def test_execution_time_none_when_never_started(self, mock_job_end):
        """
        Terminating a job which was never started (no started timestamp) should leave
        execution_time null rather than computing a value from a missing start time.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        self.assertIsNone(job.started)

        job.terminate(status=JobStatusChoices.STATUS_COMPLETED)

        self.assertIsNone(job.execution_time)
