import uuid
from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from core.choices import JobIntervalChoices, JobStatusChoices
from core.exceptions import JobFailed
from core.models import DataSource, Job
from utilities.testing import disable_warnings
from utilities.testing.mixins import RQQueueTestMixin

from ..jobs import *
from ..jobs import _INSTALL_ROOT, STALE_RUNNING_JOB_GRACE_SECONDS


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


class TestClassTimeoutJobRunner(JobRunner):
    job_timeout = 3600

    def run(self, *args, **kwargs):
        pass


class TestPropertyTimeoutJobRunner(JobRunner):
    # Mirrors plugins (e.g. netbox-branching) that expose job_timeout as an instance property.
    @property
    def job_timeout(self):
        return 7200

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

    def test_enqueue_once_replaces_stale_scheduled_job(self):
        """
        A job still in "scheduled" status whose time has already passed is stale (its RQ-side
        scheduler entry was lost, e.g. by a Redis restart between backup and restore — see
        #22714) and must be replaced, even though its recorded interval matches.
        """
        stale = Job.objects.create(
            name=TestJobRunner.name,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=60,
            scheduled=timezone.now() - timedelta(days=1),
            job_id=uuid.uuid4(),
        )

        # Mirrors how rqworker.py calls enqueue_once() for system jobs at startup: no
        # schedule_at, only the registered interval.
        job = TestJobRunner.enqueue_once(interval=60)

        self.assertNotEqual(job, stale)
        self.assertRaises(Job.DoesNotExist, stale.refresh_from_db)
        self.assertEqual(TestJobRunner.get_jobs().count(), 1)

    def test_enqueue_once_reuses_recently_scheduled_job(self):
        """
        A job whose scheduled time has only just passed is waiting its turn in the queue, not
        stranded. Within the grace margin it must be reused, not deleted and re-enqueued — a
        concurrent enqueue_once() (e.g. a DataSource save) must not disrupt a due-but-queued job.
        """
        queued = Job.objects.create(
            name=TestJobRunner.name,
            status=JobStatusChoices.STATUS_SCHEDULED,
            interval=60,
            scheduled=timezone.now() - timedelta(seconds=30),
            job_id=uuid.uuid4(),
        )

        job = TestJobRunner.enqueue_once(interval=60)

        self.assertEqual(job, queued)
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
        against the race where a worker starts up between `job.terminate()` and the
        finally block's reschedule, calling `enqueue_once()` which would create a parallel
        job.
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


class ReconcileStaleJobsTestCase(BaseJobRunnerTestCase):
    """
    Test recovery of system jobs stranded in "running" status by a killed worker (#22714).
    """

    def test_reconcile_terminates_orphaned_running_job(self):
        """A running system job whose `started` predates the run timeout window is an
        orphan (its worker died) and must be moved to `errored`."""
        orphan = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_RUNNING,
            interval=60,
            scheduled=timezone.now() - timedelta(hours=2),
            started=timezone.now() - timedelta(hours=2),
            job_id=uuid.uuid4(),
        )

        reconcile_stale_system_jobs(TestSystemJobRunner, 60)

        orphan.refresh_from_db()
        self.assertEqual(orphan.status, JobStatusChoices.STATUS_ERRORED)
        self.assertIsNotNone(orphan.completed)
        self.assertEqual(orphan.error, "Worker terminated before job completed")

    def test_reconcile_preserves_recently_started_running_job(self):
        """A running system job that started recently (within the run timeout window) is a
        legitimately in-flight job and must NOT be reaped, regardless of its interval."""
        live = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_RUNNING,
            interval=60,
            scheduled=timezone.now() - timedelta(minutes=1),
            started=timezone.now(),
            job_id=uuid.uuid4(),
        )

        reconcile_stale_system_jobs(TestSystemJobRunner, 60)

        live.refresh_from_db()
        self.assertEqual(live.status, JobStatusChoices.STATUS_RUNNING)

    def test_reconcile_window_is_run_timeout_not_interval(self):
        """The window is keyed on the RQ run timeout, not the recurrence interval, so a
        long-interval job whose worker was just killed is recovered promptly. A daily job
        started well past its run timeout (but far short of a day) must be reaped."""
        grace = settings.RQ_DEFAULT_TIMEOUT + STALE_RUNNING_JOB_GRACE_SECONDS
        orphan = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_RUNNING,
            interval=JobIntervalChoices.INTERVAL_DAILY,
            scheduled=timezone.now() - timedelta(seconds=grace + 60),
            started=timezone.now() - timedelta(seconds=grace + 60),
            job_id=uuid.uuid4(),
        )

        reconcile_stale_system_jobs(TestSystemJobRunner, JobIntervalChoices.INTERVAL_DAILY)

        orphan.refresh_from_db()
        self.assertEqual(orphan.status, JobStatusChoices.STATUS_ERRORED)

    def test_reconcile_preserves_job_within_run_timeout(self):
        """A job started just inside the run timeout window is still legitimately running
        and must be preserved."""
        grace = settings.RQ_DEFAULT_TIMEOUT + STALE_RUNNING_JOB_GRACE_SECONDS
        live = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_RUNNING,
            interval=JobIntervalChoices.INTERVAL_DAILY,
            scheduled=timezone.now() - timedelta(seconds=grace - 60),
            started=timezone.now() - timedelta(seconds=grace - 60),
            job_id=uuid.uuid4(),
        )

        reconcile_stale_system_jobs(TestSystemJobRunner, JobIntervalChoices.INTERVAL_DAILY)

        live.refresh_from_db()
        self.assertEqual(live.status, JobStatusChoices.STATUS_RUNNING)

    def test_reconcile_ignores_instance_bound_job(self):
        """The sweep targets object-less system jobs only. An instance-bound job of the
        same runner class must be left alone even if it looks stale."""
        instance = DataSource.objects.create(name='test-ds-reconcile', type='local')
        bound = Job.objects.create(
            name=TestSystemJobRunner.name,
            object=instance,
            status=JobStatusChoices.STATUS_RUNNING,
            interval=60,
            scheduled=timezone.now() - timedelta(hours=2),
            started=timezone.now() - timedelta(hours=2),
            job_id=uuid.uuid4(),
        )

        reconcile_stale_system_jobs(TestSystemJobRunner, 60)

        bound.refresh_from_db()
        self.assertEqual(bound.status, JobStatusChoices.STATUS_RUNNING)

    def test_reconcile_then_enqueue_once_rearms(self):
        """After a stranded job is reconciled to `errored`, the startup `enqueue_once()`
        call must re-arm a fresh scheduled successor."""
        orphan = Job.objects.create(
            name=TestSystemJobRunner.name,
            status=JobStatusChoices.STATUS_RUNNING,
            interval=60,
            scheduled=timezone.now() - timedelta(hours=2),
            started=timezone.now() - timedelta(hours=2),
            job_id=uuid.uuid4(),
        )

        # Mirror rqworker startup: reconcile stale jobs, then enqueue_once.
        reconcile_stale_system_jobs(TestSystemJobRunner, 60)
        successor = TestSystemJobRunner.enqueue_once(interval=60)

        orphan.refresh_from_db()
        self.assertEqual(orphan.status, JobStatusChoices.STATUS_ERRORED)
        self.assertNotEqual(successor.pk, orphan.pk)
        self.assertIn(successor.status, JobStatusChoices.ENQUEUED_STATE_CHOICES)

        # Exactly one live (enqueued) successor should remain.
        enqueued = Job.objects.filter(
            name=TestSystemJobRunner.name,
            object_id__isnull=True,
            status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES,
        )
        self.assertEqual(enqueued.count(), 1)

    def test_reconcile_honors_longer_per_job_timeout(self):
        """A runner that declares a large `job_timeout` gets a proportionally longer window. A
        job started past the default window but within its own declared timeout must be preserved,
        so a legitimately long run (e.g. a bulk branch archival) is not reaped."""
        interval = JobIntervalChoices.INTERVAL_DAILY
        default_window = settings.RQ_DEFAULT_TIMEOUT + STALE_RUNNING_JOB_GRACE_SECONDS
        # Older than the default window, but well within this runner's 3600s job_timeout.
        started = timezone.now() - timedelta(seconds=default_window + 120)
        live = Job.objects.create(
            name=TestClassTimeoutJobRunner.name,
            status=JobStatusChoices.STATUS_RUNNING,
            interval=interval,
            scheduled=started,
            started=started,
            job_id=uuid.uuid4(),
        )

        reconcile_stale_system_jobs(TestClassTimeoutJobRunner, interval)

        live.refresh_from_db()
        self.assertEqual(live.status, JobStatusChoices.STATUS_RUNNING)


class ResolveJobTimeoutTestCase(BaseJobRunnerTestCase):
    """
    Test resolution of a runner's RQ run timeout across the ad-hoc conventions (#22714).
    """

    def test_falls_back_to_rq_default(self):
        job = Job(name=TestSystemJobRunner.name)
        self.assertEqual(resolve_job_timeout(TestSystemJobRunner, job), settings.RQ_DEFAULT_TIMEOUT)

    def test_reads_class_attribute(self):
        job = Job(name=TestClassTimeoutJobRunner.name)
        self.assertEqual(resolve_job_timeout(TestClassTimeoutJobRunner, job), 3600)

    def test_reads_instance_property(self):
        job = Job(name=TestPropertyTimeoutJobRunner.name)
        self.assertEqual(resolve_job_timeout(TestPropertyTimeoutJobRunner, job), 7200)
