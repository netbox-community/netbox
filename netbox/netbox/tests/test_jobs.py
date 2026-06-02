import uuid
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from core.choices import JobStatusChoices
from core.exceptions import JobFailed
from core.models import DataSource, Job
from utilities.testing import disable_warnings
from utilities.testing.mixins import RQQueueTestMixin

from ..jobs import *
from ..jobs import _INSTALL_ROOT


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
