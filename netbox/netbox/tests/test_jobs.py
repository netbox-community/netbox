import uuid
from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase, tag
from django.urls import reverse
from django.utils import timezone
from django_pg_utils import advisory_lock
from django_rq import get_queue

from core.choices import JobStatusChoices
from core.exceptions import JobFailed
from core.models import DataSource, Job
from core.signals import job_end
from dcim.models import Site
from dcim.views import SiteBulkEditView
from extras.models import Notification
from users.models import User
from utilities.request import copy_safe_request
from utilities.testing import disable_logging, disable_warnings
from utilities.testing.mixins import RQQueueTestMixin

from ..jobs import *
from ..jobs import _INSTALL_ROOT


def _noop():
    """A no-op callable used to register a real RQ job in tests."""
    pass


class TestJobRunner(JobRunner):

    def run(self, *args, **kwargs):
        if kwargs.get('make_fail', False):
            raise JobFailed()
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")


@system_job(interval=60)
class TestSystemJobRunner(JobRunner):

    def run(self, *args, **kwargs):
        pass


class BaseJobRunnerTestCase(RQQueueTestMixin, TestCase):

    @staticmethod
    def get_schedule_at(offset=1):
        # Schedule jobs a week in advance to avoid accidentally running jobs on worker nodes used for testing.
        return timezone.now() + timedelta(weeks=offset)


class JobRunnerTestCase(BaseJobRunnerTestCase):
    """
    Test the internal logic of `JobRunner`.
    """

    def test_name_default(self):
        self.assertEqual(TestJobRunner.name, TestJobRunner.__name__)

    def test_name_set(self):
        class NamedJobRunner(TestJobRunner):
            class Meta:
                name = 'TestName'

        self.assertEqual(NamedJobRunner.name, 'TestName')

    def test_handle(self):
        job = TestJobRunner.enqueue(immediate=True)

        # Check job status
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)

        # Check logging
        self.assertEqual(len(job.log_entries), 4)
        self.assertEqual(job.log_entries[0]['message'], "Debug message")
        self.assertEqual(job.log_entries[1]['message'], "Info message")
        self.assertEqual(job.log_entries[2]['message'], "Warning message")
        self.assertEqual(job.log_entries[3]['message'], "Error message")

    def test_handle_failed(self):
        with disable_warnings('netbox.jobs'):
            job = TestJobRunner.enqueue(immediate=True, make_fail=True)

        self.assertEqual(job.status, JobStatusChoices.STATUS_FAILED)

    def test_handle_errored(self):
        class ErroredJobRunner(TestJobRunner):
            EXP = Exception('Test error')

            def run(self, *args, **kwargs):
                raise self.EXP

        job = ErroredJobRunner.enqueue(immediate=True)

        self.assertEqual(job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertEqual(job.error, repr(ErroredJobRunner.EXP))
        self.assertEqual(len(job.log_entries), 1)
        self.assertEqual(job.log_entries[0]['level'], 'error')
        tb_message = job.log_entries[0]['message']
        self.assertIn('Traceback', tb_message)
        self.assertIn('Test error', tb_message)
        self.assertNotIn(_INSTALL_ROOT, tb_message)

    @tag('regression')  # Ref: #23535
    def test_handle_reschedules_before_terminating(self):
        """A periodic job's successor exists when job_end is sent."""
        outcomes = (
            (None, JobStatusChoices.STATUS_COMPLETED),
            (JobFailed(), JobStatusChoices.STATUS_FAILED),
            (RuntimeError('Simulated run error'), JobStatusChoices.STATUS_ERRORED),
        )
        for run_error, status in outcomes:
            with self.subTest(status=status):
                instance = DataSource.objects.create(name=f'Source {status}', type='local')
                job = TestJobRunner.enqueue(instance, interval=60, schedule_at=self.get_schedule_at())
                observed = []

                def record_end(sender, **kwargs):
                    waiting = TestJobRunner.get_jobs(instance).filter(
                        status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES,
                    )
                    observed.append((Job.objects.get(pk=sender.pk).status, list(waiting.values_list('pk', flat=True))))

                job_end.connect(record_end, sender=job)
                try:
                    with patch.object(TestJobRunner, 'run', side_effect=run_error), disable_warnings('netbox.jobs'):
                        TestJobRunner.handle(job)
                finally:
                    job_end.disconnect(record_end, sender=job)

                successor = TestJobRunner.get_jobs(instance).exclude(pk=job.pk).get()
                self.assertEqual(observed, [(status, [successor.pk])])
                self.assertEqual((successor.status, successor.interval), (JobStatusChoices.STATUS_SCHEDULED, 60))

    def test_handle_keeps_run_outcome_when_reschedule_is_invalid(self):
        """A reschedule rejected as invalid keeps the run's outcome and ends the job once."""
        user = User.objects.create_user(username='job-owner')
        outcomes = (
            (None, JobStatusChoices.STATUS_COMPLETED),
            (JobFailed(), JobStatusChoices.STATUS_FAILED),
            (RuntimeError('Simulated run error'), JobStatusChoices.STATUS_ERRORED),
        )
        for run_error, status in outcomes:
            with self.subTest(status=status):
                instance = DataSource.objects.create(name=f'Source {status}', type='local')
                job = TestJobRunner.enqueue(instance, interval=60, user=user)

                with (
                    patch.object(TestJobRunner, 'run', side_effect=run_error),
                    patch.object(TestJobRunner, 'enqueue', side_effect=ValidationError('Simulated validation error')),
                    patch.object(job_end, 'send', wraps=job_end.send) as send_end,
                    disable_logging(),
                ):
                    TestJobRunner.handle(job)

                job.refresh_from_db()
                self.assertEqual(job.status, status)
                self.assertEqual(job.error, repr(run_error) if status == JobStatusChoices.STATUS_ERRORED else '')
                self.assertEqual(job.log_entries[-1]['level'], 'error')
                self.assertIn('Simulated validation error', job.log_entries[-1]['message'])
                self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)
                send_end.assert_called_once_with(job)
                self.assertEqual(Notification.objects.filter(user=user, object_id=job.pk).count(), 1)

    def test_handle_terminates_job_when_reschedule_fails(self):
        """An unexpected reschedule failure still ends the job once, then propagates."""
        user = User.objects.create_user(username='job-owner')
        job = TestJobRunner.enqueue(interval=60, user=user)

        with (
            patch.object(TestJobRunner, 'run'),
            patch.object(TestJobRunner, 'enqueue', side_effect=RuntimeError('Simulated queue error')),
            patch.object(job_end, 'send', wraps=job_end.send) as send_end,
            self.assertRaisesMessage(RuntimeError, 'Simulated queue error'),
        ):
            TestJobRunner.handle(job)

        job.refresh_from_db()
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)
        self.assertIsNotNone(job.completed)
        send_end.assert_called_once_with(job)
        self.assertEqual(Notification.objects.filter(user=user, object_id=job.pk).count(), 1)

    def test_handle_terminates_job_once_when_end_receiver_fails(self):
        """A failing job_end receiver after a successful run leaves the job completed and propagates."""
        user = User.objects.create_user(username='job-owner')
        job = TestJobRunner.enqueue(user=user)

        with (
            patch.object(TestJobRunner, 'run'),
            patch.object(job_end, 'send', side_effect=RuntimeError('Simulated receiver error')) as send_end,
            self.assertRaisesMessage(RuntimeError, 'Simulated receiver error'),
        ):
            TestJobRunner.handle(job)

        job.refresh_from_db()
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)
        send_end.assert_called_once_with(job)
        self.assertEqual(Notification.objects.filter(user=user, object_id=job.pk).count(), 1)

    def test_handle_propagates_interrupt_and_reschedules(self):
        """An interrupted run propagates the interrupt, records no outcome and still schedules the successor."""
        instance = DataSource.objects.create(name='Interrupted Source', type='local')
        job = TestJobRunner.enqueue(instance, interval=60, schedule_at=self.get_schedule_at())

        with patch.object(TestJobRunner, 'run', side_effect=SystemExit), self.assertRaises(SystemExit):
            TestJobRunner.handle(job)

        job.refresh_from_db()
        self.assertEqual(job.status, JobStatusChoices.STATUS_RUNNING)
        self.assertIsNone(job.completed)
        successor = TestJobRunner.get_jobs(instance).exclude(pk=job.pk).get()
        self.assertEqual((successor.status, successor.interval), (JobStatusChoices.STATUS_SCHEDULED, 60))


class EnqueueTestCase(BaseJobRunnerTestCase):
    """
    Test enqueuing of `JobRunner`.
    """

    def test_enqueue(self):
        instance = DataSource()
        for i in range(1, 3):
            job = TestJobRunner.enqueue(instance, schedule_at=self.get_schedule_at())

            self.assertIsInstance(job, Job)
            self.assertEqual(TestJobRunner.get_jobs(instance).count(), i)

    def test_enqueue_once(self):
        job = TestJobRunner.enqueue_once(instance=DataSource(), schedule_at=self.get_schedule_at())

        self.assertIsInstance(job, Job)
        self.assertEqual(job.name, TestJobRunner.__name__)

    def test_enqueue_once_twice_same(self):
        instance = DataSource()
        schedule_at = self.get_schedule_at()
        job1 = TestJobRunner.enqueue_once(instance, schedule_at=schedule_at)
        job2 = TestJobRunner.enqueue_once(instance, schedule_at=schedule_at)

        self.assertEqual(job1, job2)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)

    def test_enqueue_once_twice_same_no_schedule_at(self):
        instance = DataSource()
        schedule_at = self.get_schedule_at()
        job1 = TestJobRunner.enqueue_once(instance, schedule_at=schedule_at)
        job2 = TestJobRunner.enqueue_once(instance)

        self.assertEqual(job1, job2)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)

    def test_enqueue_once_twice_different_schedule_at(self):
        instance = DataSource()
        job1 = TestJobRunner.enqueue_once(instance, schedule_at=self.get_schedule_at())
        job2 = TestJobRunner.enqueue_once(instance, schedule_at=self.get_schedule_at(2))

        self.assertNotEqual(job1, job2)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)

    def test_enqueue_once_twice_different_interval(self):
        instance = DataSource()
        schedule_at = self.get_schedule_at()
        job1 = TestJobRunner.enqueue_once(instance, schedule_at=schedule_at)
        job2 = TestJobRunner.enqueue_once(instance, schedule_at=schedule_at, interval=60)

        self.assertNotEqual(job1, job2)
        self.assertEqual(job1.interval, None)
        self.assertEqual(job2.interval, 60)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)

    def test_enqueue_once_replaces_stale_scheduled_system_job(self):
        """
        A system job scheduled in the past whose RQ-side entry is gone will never fire and must
        be replaced (see #22714). The bare Job row below has no RQ entry, mirroring the repro.
        """
        stale = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=60,
            scheduled=timezone.now() - timedelta(days=1),
            job_id=uuid.uuid4(),
        )

        # Mirrors how rqworker.py calls enqueue_once() for system jobs at startup: no
        # schedule_at, only the registered interval.
        job = TestSystemJobRunner.enqueue_once(interval=60)

        self.assertNotEqual(job, stale)
        self.assertRaises(Job.DoesNotExist, stale.refresh_from_db)
        self.assertEqual(TestSystemJobRunner.get_jobs().count(), 1)

    def test_enqueue_once_reuses_scheduled_system_job_still_in_rq(self):
        """
        An overdue system job whose RQ entry still exists is merely waiting its turn, not stale,
        so it must be reused rather than replaced.
        """
        scheduled = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=60,
            scheduled=timezone.now() - timedelta(days=1),
            job_id=uuid.uuid4(),
            queue_name='default',
        )
        # Register a real RQ-side scheduled entry for this job_id.
        get_queue('default').enqueue_at(
            timezone.now() + timedelta(days=1), _noop, job_id=str(scheduled.job_id)
        )

        job = TestSystemJobRunner.enqueue_once(interval=60)

        self.assertEqual(job, scheduled)
        self.assertEqual(TestSystemJobRunner.get_jobs().count(), 1)

    def test_enqueue_once_reuses_queued_system_job(self):
        """
        Once a due job is moved from the scheduled registry into its queue, it is still live and
        must be reused, not replaced, even though it is no longer in the scheduled registry.
        """
        queued = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=60,
            scheduled=timezone.now() - timedelta(days=1),
            job_id=uuid.uuid4(),
            queue_name='default',
        )
        # Enqueue directly onto the queue (not the scheduled registry), as RQ does once due.
        get_queue('default').enqueue(_noop, job_id=str(queued.job_id))

        job = TestSystemJobRunner.enqueue_once(interval=60)

        self.assertEqual(job, queued)
        self.assertEqual(TestSystemJobRunner.get_jobs().count(), 1)

    def test_enqueue_once_reuses_future_scheduled_system_job(self):
        """
        A system job scheduled for a future time has not come due, so it is not stale and must
        be reused regardless of its RQ state.
        """
        scheduled = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=60,
            scheduled=timezone.now() + timedelta(days=1),
            job_id=uuid.uuid4(),
        )

        job = TestSystemJobRunner.enqueue_once(interval=60)

        self.assertEqual(job, scheduled)
        self.assertEqual(TestSystemJobRunner.get_jobs().count(), 1)

    def test_enqueue_once_reuses_stale_scheduled_non_system_job(self):
        """
        Staleness replacement is limited to system jobs. A past-due non-system scheduled job
        (e.g. a DataSource sync) may legitimately await its turn and must be reused.
        """
        scheduled = Job.objects.create(
            name=TestJobRunner.name,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=60,
            scheduled=timezone.now() - timedelta(days=1),
            job_id=uuid.uuid4(),
        )

        job = TestJobRunner.enqueue_once(interval=60)

        self.assertEqual(job, scheduled)
        self.assertEqual(TestJobRunner.get_jobs().count(), 1)

    def test_enqueue_once_reuses_pending_job_with_no_schedule(self):
        """
        A pending job (not yet picked up by a worker) has no `scheduled` timestamp at all.
        That must not be mistaken for a stale schedule and must not raise when compared
        against the current time.
        """
        pending = Job.objects.create(
            name=TestJobRunner.name,
            status=JobStatusChoices.STATUS_PENDING,
            interval=60,
            scheduled=None,
            job_id=uuid.uuid4(),
        )

        job = TestJobRunner.enqueue_once(interval=60)

        self.assertEqual(job, pending)
        self.assertEqual(TestJobRunner.get_jobs().count(), 1)

    def test_enqueue_once_reuses_running_job_with_past_schedule(self):
        """
        Once a job starts, its `scheduled` timestamp is left in the past (that's normal —
        `start()` doesn't clear it) while status moves to "running". A concurrent
        enqueue_once() call (e.g. a second worker starting up mid-run) must not mistake
        that for staleness and delete an in-flight job out from under itself.
        """
        running = Job.objects.create(
            name=TestJobRunner.name,
            status=JobStatusChoices.STATUS_RUNNING,
            interval=60,
            scheduled=timezone.now() - timedelta(minutes=5),
            started=timezone.now(),
            job_id=uuid.uuid4(),
        )

        job = TestJobRunner.enqueue_once(interval=60)

        self.assertEqual(job, running)
        self.assertEqual(TestJobRunner.get_jobs().count(), 1)

    def test_enqueue_once_with_enqueue(self):
        instance = DataSource()
        job1 = TestJobRunner.enqueue_once(instance, schedule_at=self.get_schedule_at(2))
        job2 = TestJobRunner.enqueue(instance, schedule_at=self.get_schedule_at())

        self.assertNotEqual(job1, job2)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 2)

    def test_enqueue_once_after_enqueue(self):
        instance = DataSource()
        job1 = TestJobRunner.enqueue(instance, schedule_at=self.get_schedule_at())
        job2 = TestJobRunner.enqueue_once(instance, schedule_at=self.get_schedule_at(2))

        self.assertNotEqual(job1, job2)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
        self.assertEqual(TestJobRunner.get_jobs(instance).count(), 1)


class SystemJobTestCase(BaseJobRunnerTestCase):
    """
    Test that system jobs can be scheduled.

    General functionality already tested by `JobRunnerTestCase` and `EnqueueTestCase`.
    """

    def test_scheduling(self):
        # Can job be enqueued?
        job = TestJobRunner.enqueue(schedule_at=self.get_schedule_at())
        self.assertIsInstance(job, Job)
        self.assertEqual(TestJobRunner.get_jobs().count(), 1)

        # Can job be deleted again?
        job.delete()
        self.assertRaises(Job.DoesNotExist, job.refresh_from_db)
        self.assertEqual(TestJobRunner.get_jobs().count(), 0)

    def test_enqueue_once(self):
        schedule_at = self.get_schedule_at()
        job1 = TestJobRunner.enqueue_once(schedule_at=schedule_at)
        job2 = TestJobRunner.enqueue_once(schedule_at=schedule_at)

        self.assertEqual(job1, job2)
        self.assertEqual(TestJobRunner.get_jobs().count(), 1)

    def test_handle_skips_reschedule_when_successor_exists(self):
        """
        When `handle()` finishes a periodic system job, it must not create a duplicate
        scheduled job if a successor is already enqueued (issue #22232). This guards
        against a successor that another occurrence or `enqueue_once()` already created.
        """
        interval = 60

        # Simulate a successor that was already created by another worker.
        successor = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=interval,
            scheduled=self.get_schedule_at(),
            job_id=uuid.uuid4(),
        )

        # The just-finished job. `handle()` will run its finally block.
        finished = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_COMPLETED,
            interval=interval,
            started=timezone.now(),
            completed=timezone.now(),
            job_id=uuid.uuid4(),
        )

        TestSystemJobRunner.handle(finished)

        # Only the original successor should remain enqueued — no duplicate should have
        # been created.
        enqueued = Job.objects.filter(
            name=TestSystemJobRunner.name,
            status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES,
            interval=interval,
        )
        self.assertEqual(enqueued.count(), 1)
        self.assertEqual(enqueued.first().pk, successor.pk)

    def test_handle_reschedules_when_only_instance_bound_successor_exists(self):
        """
        For a system (object-less) job, an instance-bound job of the same JobRunner class
        must not be treated as a successor. The system job should still reschedule itself.
        """
        interval = 60
        instance = DataSource.objects.create(name='test-ds', type='local')

        # An instance-bound enqueued job of the same class and interval — must NOT be
        # treated as a successor of the object-less finished job.
        Job.objects.create(
            name=TestSystemJobRunner.name,
            object=instance,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=interval,
            scheduled=self.get_schedule_at(),
            job_id=uuid.uuid4(),
        )

        # Object-less finished system job.
        finished = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_COMPLETED,
            interval=interval,
            started=timezone.now(),
            completed=timezone.now(),
            job_id=uuid.uuid4(),
        )

        TestSystemJobRunner.handle(finished)

        # A new object-less successor should have been scheduled.
        enqueued = Job.objects.filter(
            name=TestSystemJobRunner.name,
            object_id__isnull=True,
            status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES,
            interval=interval,
        )
        self.assertEqual(enqueued.count(), 1)

    def test_handle_reschedules_non_system_job_independently(self):
        """
        Two recurring non-system jobs (e.g. scheduled scripts) for the same runner and
        object with the same interval but distinct runtime kwargs must each reschedule
        themselves; one must not be treated as the successor of the other and skipped.
        """
        interval = 60
        instance = DataSource.objects.create(name='test-ds-script', type='local')

        # An unrelated recurring schedule for the same runner/object/interval. Stands in
        # for a second scheduled-script entry with different `data`.
        Job.objects.create(
            name=TestJobRunner.name,
            object=instance,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=interval,
            scheduled=self.get_schedule_at(),
            job_id=uuid.uuid4(),
        )

        finished = Job.objects.create(
            name=TestJobRunner.name,
            object=instance,
            status=JobStatusChoices.STATUS_COMPLETED,
            interval=interval,
            started=timezone.now(),
            completed=timezone.now(),
            job_id=uuid.uuid4(),
        )

        with patch.object(TestJobRunner, 'run'):
            TestJobRunner.handle(finished)

        # Both the unrelated schedule and the finished job's successor should be enqueued.
        enqueued = Job.objects.filter(
            name=TestJobRunner.name,
            status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES,
            interval=interval,
        )
        self.assertEqual(enqueued.count(), 2)

    def test_handle_keeps_one_successor_for_overlapping_jobs(self):
        """Two occurrences of a system job ending back to back leave one successor."""
        first = TestSystemJobRunner.enqueue(interval=60)
        second = TestSystemJobRunner.enqueue(interval=60)
        waiting_runs = [second]

        @contextmanager
        def end_second_after_unlock(*args, **kwargs):
            with advisory_lock(*args, **kwargs):
                yield
            # Another worker ends the second occurrence as soon as the lock is free
            while waiting_runs:
                TestSystemJobRunner.handle(waiting_runs.pop())

        with patch('netbox.jobs.advisory_lock', side_effect=end_second_after_unlock):
            TestSystemJobRunner.handle(first)

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.status, JobStatusChoices.STATUS_COMPLETED)
        self.assertEqual(second.status, JobStatusChoices.STATUS_COMPLETED)
        waiting = TestSystemJobRunner.get_jobs().filter(status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES)
        self.assertEqual(list(waiting.values_list('status', 'interval')), [(JobStatusChoices.STATUS_SCHEDULED, 60)])

    def test_handle_terminates_job_when_schedule_lock_fails(self):
        """A failure to take the schedule lock still ends the job, then propagates."""
        job = TestSystemJobRunner.enqueue(interval=60)

        with (
            patch('netbox.jobs.advisory_lock') as lock,
            self.assertRaisesMessage(RuntimeError, 'Simulated lock error'),
        ):
            lock.return_value.__enter__.side_effect = RuntimeError('Simulated lock error')
            TestSystemJobRunner.handle(job)

        job.refresh_from_db()
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)


class AsyncViewJobTestCase(TestCase):
    """
    Test running UI views as background jobs.
    """

    def test_bulk_edit(self):
        user = User.objects.create_superuser(username='testuser')
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)
        request = RequestFactory().post(reverse('dcim:site_bulk_edit'), data={
            '_apply': True,
            'pk': [site.pk for site in sites],
            'description': 'Edited in a background job',
            'background_job': True,
        })
        request.user = user
        request.id = uuid.uuid4()
        job = Job.objects.create(name='Bulk edit', user=user, job_id=uuid.uuid4())

        # Run the view as process_request_as_job() would have it run in a worker
        AsyncViewJob(job).run(view_cls=SiteBulkEditView, request=copy_safe_request(request))

        self.assertEqual(Site.objects.filter(description='Edited in a background job').count(), len(sites))
