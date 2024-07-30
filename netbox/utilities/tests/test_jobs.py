from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django_rq import get_queue

from ..jobs import *
from core.models import Job
from core.choices import JobStatusChoices


class TestBackgroundJob(BackgroundJob):
    def run(self, *args, **kwargs):
        pass


class BackgroundJobTestCase(TestCase):
    def tearDown(self):
        super().tearDown()

        # Clear all queues after running each test
        get_queue('default').connection.flushall()
        get_queue('high').connection.flushall()
        get_queue('low').connection.flushall()

    @staticmethod
    def get_schedule_at(offset=1):
        # Schedule jobs a week in advance to avoid accidentally running jobs on worker nodes used for testing.
        return timezone.now() + timedelta(weeks=offset)


class BackgroundJobTest(BackgroundJobTestCase):
    """
    Test internal logic of `BackgroundJob`.
    """

    def test_name_default(self):
        self.assertEqual(TestBackgroundJob.name, TestBackgroundJob.__name__)

    def test_name_set(self):
        class NamedBackgroundJob(TestBackgroundJob):
            class Meta:
                name = 'TestName'

        self.assertEqual(NamedBackgroundJob.name, 'TestName')

    def test_handle(self):
        job = TestBackgroundJob.enqueue(immediate=True)

        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED)

    def test_handle_errored(self):
        class ErroredBackgroundJob(TestBackgroundJob):
            EXP = Exception('Test error')

            def run(self, *args, **kwargs):
                raise self.EXP

        job = ErroredBackgroundJob.enqueue(immediate=True)

        self.assertEqual(job.status, JobStatusChoices.STATUS_ERRORED)
        self.assertEqual(job.error, repr(ErroredBackgroundJob.EXP))


class EnqueueTest(BackgroundJobTestCase):
    """
    Test enqueuing of `BackgroundJob`.
    """

    def test_enqueue(self):
        instance = Job()
        for i in range(1, 3):
            job = TestBackgroundJob.enqueue(instance, schedule_at=self.get_schedule_at())

            self.assertIsInstance(job, Job)
            self.assertEqual(TestBackgroundJob.get_jobs(instance).count(), i)

    def test_enqueue_once(self):
        job = TestBackgroundJob.enqueue_once(instance=Job(), schedule_at=self.get_schedule_at())

        self.assertIsInstance(job, Job)
        self.assertEqual(job.name, TestBackgroundJob.__name__)

    def test_enqueue_once_twice_same(self):
        instance = Job()
        schedule_at = self.get_schedule_at()
        job1 = TestBackgroundJob.enqueue_once(instance, schedule_at=schedule_at)
        job2 = TestBackgroundJob.enqueue_once(instance, schedule_at=schedule_at)

        self.assertEqual(job1, job2)
        self.assertEqual(TestBackgroundJob.get_jobs(instance).count(), 1)

    def test_enqueue_once_twice_different_schedule_at(self):
        instance = Job()
        job1 = TestBackgroundJob.enqueue_once(instance, schedule_at=self.get_schedule_at())
        job2 = TestBackgroundJob.enqueue_once(instance, schedule_at=self.get_schedule_at(2))

        self.assertNotEqual(job1, job2)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
        self.assertEqual(TestBackgroundJob.get_jobs(instance).count(), 1)

    def test_enqueue_once_twice_different_interval(self):
        instance = Job()
        schedule_at = self.get_schedule_at()
        job1 = TestBackgroundJob.enqueue_once(instance, schedule_at=schedule_at)
        job2 = TestBackgroundJob.enqueue_once(instance, schedule_at=schedule_at, interval=60)

        self.assertNotEqual(job1, job2)
        self.assertEqual(job1.interval, None)
        self.assertEqual(job2.interval, 60)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
        self.assertEqual(TestBackgroundJob.get_jobs(instance).count(), 1)

    def test_enqueue_once_with_enqueue(self):
        instance = Job()
        job1 = TestBackgroundJob.enqueue_once(instance, schedule_at=self.get_schedule_at(2))
        job2 = TestBackgroundJob.enqueue(instance, schedule_at=self.get_schedule_at())

        self.assertNotEqual(job1, job2)
        self.assertEqual(TestBackgroundJob.get_jobs(instance).count(), 2)

    def test_enqueue_once_after_enqueue(self):
        instance = Job()
        job1 = TestBackgroundJob.enqueue(instance, schedule_at=self.get_schedule_at())
        job2 = TestBackgroundJob.enqueue_once(instance, schedule_at=self.get_schedule_at(2))

        self.assertNotEqual(job1, job2)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
        self.assertEqual(TestBackgroundJob.get_jobs(instance).count(), 1)
