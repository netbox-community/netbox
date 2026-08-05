import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone

from core.choices import JobNotificationChoices, JobStatusChoices, ObjectChangeActionChoices
from core.models import DataSource, Job, ObjectType
from dcim.models import Device, Location, Site
from extras.models import Notification
from netbox.constants import CENSOR_TOKEN, CENSOR_TOKEN_CHANGED
from users.models import User


class DataSourceIgnoreRulesTestCase(TestCase):

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


class DataSourceChangeLoggingTestCase(TestCase):

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

    @patch('core.models.jobs.job_end')
    def test_elapsed_time_returns_execution_time_once_completed(self, mock_job_end):
        """
        For a completed job, elapsed_time should return the recorded execution_time.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        job.started = timezone.now() - timedelta(seconds=90)
        job.save()

        job.terminate(status=JobStatusChoices.STATUS_COMPLETED)

        self.assertEqual(job.elapsed_time, job.execution_time)

    def test_elapsed_time_of_running_job(self):
        """
        A running job has no execution_time yet, so elapsed_time should report the time elapsed
        since it started.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        job.started = timezone.now() - timedelta(seconds=90)
        job.save()

        self.assertEqual(job.status, JobStatusChoices.STATUS_RUNNING)
        self.assertIsNone(job.execution_time)
        self.assertGreaterEqual(job.elapsed_time, timedelta(seconds=90))
        self.assertLess(job.elapsed_time, timedelta(seconds=120))

    def test_elapsed_time_none_when_never_started(self):
        """
        A job which has not started has no elapsed time to report.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)

        self.assertIsNone(job.started)
        self.assertIsNone(job.elapsed_time)

    def test_elapsed_time_clamps_negative_execution_time(self):
        """
        elapsed_time is the value NetBox displays, so an anomalous negative duration (e.g. resulting
        from clock skew) is floored at zero. The stored execution_time is left as recorded, so that
        the anomaly remains visible to the API and to exports.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        job.started = timezone.now()
        job.completed = timezone.now()
        job.execution_time = timedelta(seconds=-5)
        job.status = JobStatusChoices.STATUS_COMPLETED
        job.save()

        self.assertEqual(job.elapsed_time, timedelta())
        self.assertEqual(job.execution_time, timedelta(seconds=-5))

    def test_duration_is_deprecated(self):
        """
        Job.duration is retained for existing export templates and plugins, but must warn.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        job.started = timezone.now() - timedelta(seconds=90)
        job.completed = job.started + timedelta(seconds=90)
        job.status = JobStatusChoices.STATUS_COMPLETED
        job.save()

        with self.assertWarns(DeprecationWarning):
            self.assertEqual(job.duration, '1 minutes, 30.00 seconds')

    def test_duration_falls_back_to_created(self):
        """
        The deprecated property's original behavior must be preserved: a job which completed without
        ever starting reports its duration relative to creation.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        job.started = None
        job.completed = job.created + timedelta(seconds=30)
        job.status = JobStatusChoices.STATUS_ERRORED
        job.save()

        with self.assertWarns(DeprecationWarning):
            self.assertEqual(job.duration, '0 minutes, 30.00 seconds')

    def test_duration_none_when_not_completed(self):
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)

        with self.assertWarns(DeprecationWarning):
            self.assertIsNone(job.duration)

    def test_elapsed_time_none_when_completed_without_execution_time(self):
        """
        A job which completed without recording an execution time (e.g. one predating the field)
        has no elapsed time to report; it must not accrue time indefinitely.
        """
        job = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        job.started = timezone.now() - timedelta(seconds=90)
        job.completed = timezone.now()
        job.status = JobStatusChoices.STATUS_COMPLETED
        job.save()

        self.assertIsNone(job.execution_time)
        self.assertIsNone(job.elapsed_time)

    def test_elapsed_time_expression_matches_property(self):
        """
        The elapsed_time_expression() queryset expression should agree with the elapsed_time
        property for completed, running, and never-started jobs.
        """
        completed = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        completed.started = timezone.now() - timedelta(seconds=90)
        completed.completed = timezone.now()
        completed.execution_time = timedelta(seconds=90)
        completed.status = JobStatusChoices.STATUS_COMPLETED
        completed.save()

        # A job which completed without recording an execution time must resolve to null, rather
        # than to an ever-growing interval since it started
        unrecorded = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        unrecorded.started = timezone.now() - timedelta(seconds=90)
        unrecorded.completed = timezone.now()
        unrecorded.status = JobStatusChoices.STATUS_COMPLETED
        unrecorded.save()

        running = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        running.started = timezone.now() - timedelta(minutes=5)
        running.save()

        pending = self._make_job(None, JobNotificationChoices.NOTIFICATION_NEVER)
        pending.status = JobStatusChoices.STATUS_PENDING
        pending.save()

        annotated = {
            job.pk: job
            for job in Job.objects.annotate(elapsed=Job.elapsed_time_expression())
        }

        self.assertEqual(annotated[completed.pk].elapsed, timedelta(seconds=90))
        self.assertIsNone(annotated[unrecorded.pk].elapsed)
        self.assertIsNone(annotated[pending.pk].elapsed)
        # The running job's elapsed time is computed at query time, so compare approximately
        self.assertAlmostEqual(
            annotated[running.pk].elapsed.total_seconds(),
            running.elapsed_time.total_seconds(),
            delta=5,
        )
