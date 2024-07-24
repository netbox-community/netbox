from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django_rq import get_queue

from ..jobs import *
from core.models import Job


class TestBackgroundJob(BackgroundJob):
    @classmethod
    def run(cls, *args, **kwargs):
        pass


class BackgroundJobTestCase(TestCase):
    def tearDown(self):
        super().tearDown()

        # Clear all queues after running each test
        get_queue('default').connection.flushall()
        get_queue('high').connection.flushall()
        get_queue('low').connection.flushall()

    @staticmethod
    def get_schedule_at():
        # Schedule jobs a week in advance to avoid accidentally running jobs on worker nodes used for testing.
        return timezone.now() + timedelta(weeks=1)


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
        job1 = TestBackgroundJob.enqueue_once(instance, schedule_at=self.get_schedule_at())
        job2 = TestBackgroundJob.enqueue_once(instance, schedule_at=self.get_schedule_at())

        self.assertEqual(job1, job2)
        self.assertEqual(TestBackgroundJob.get_jobs(instance).count(), 1)

    def test_enqueue_once_twice_different(self):
        instance = Job()
        job1 = TestBackgroundJob.enqueue_once(instance, schedule_at=self.get_schedule_at())
        job2 = TestBackgroundJob.enqueue_once(instance, schedule_at=self.get_schedule_at(), interval=60)

        self.assertNotEqual(job1, job2)
        self.assertEqual(job1.interval, None)
        self.assertEqual(job2.interval, 60)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)


class SystemJobTest(BackgroundJobTestCase):
    """
    Test internal logic of `SystemJob`.
    """

    class TestSystemJob(SystemJob):
        @classmethod
        def run(cls, *args, **kwargs):
            pass

    def test_enqueue_once(self):
        job = self.TestSystemJob.enqueue_once(schedule_at=self.get_schedule_at())

        self.assertIsInstance(job, Job)
        self.assertEqual(job.object, None)
