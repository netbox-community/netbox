from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django_rq import get_queue

from ..jobs import *
from core.models import Job


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


class ScheduledJobTest(BackgroundJobTestCase):
    """
    Test internal logic of `ScheduledJob`.
    """

    class TestScheduledJob(ScheduledJob):
        @classmethod
        def run(cls, *args, **kwargs):
            pass

    def test_schedule(self):
        job = self.TestScheduledJob.schedule(instance=Job(), schedule_at=self.get_schedule_at())

        self.assertIsInstance(job, Job)
        self.assertEqual(job.name, self.TestScheduledJob.__name__)

    def test_schedule_twice_same(self):
        instance = Job()
        job1 = self.TestScheduledJob.schedule(instance, schedule_at=self.get_schedule_at())
        job2 = self.TestScheduledJob.schedule(instance, schedule_at=self.get_schedule_at())

        self.assertEqual(job1, job2)
        self.assertEqual(self.TestScheduledJob.get_jobs(instance).count(), 1)

    def test_schedule_twice_different(self):
        instance = Job()
        job1 = self.TestScheduledJob.schedule(instance, schedule_at=self.get_schedule_at())
        job2 = self.TestScheduledJob.schedule(instance, schedule_at=self.get_schedule_at(), interval=60)

        self.assertNotEqual(job1, job2)
        self.assertEqual(job1.interval, None)
        self.assertEqual(job2.interval, 60)
        self.assertRaises(Job.DoesNotExist, job1.refresh_from_db)
