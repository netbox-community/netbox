import logging
from abc import ABC, abstractmethod
from datetime import timedelta

from django.db.backends.signals import connection_created
from django_pglocks import advisory_lock
from rq.timeouts import JobTimeoutException

from core.choices import JobStatusChoices
from core.models import Job, ObjectType
from netbox.constants import ADVISORY_LOCK_KEYS

__all__ = (
    'BackgroundJob',
    'ScheduledJob',
)


class BackgroundJob(ABC):
    """
    Background Job helper class.

    This class handles the execution of a background job. It is responsible for maintaining its state, reporting errors,
    and scheduling recurring jobs.
    """

    @classmethod
    @abstractmethod
    def run(cls, *args, **kwargs):
        """
        Run the job.

        A `BackgroundJob` class needs to implement this method to execute all commands of the job.
        """
        pass

    @classmethod
    def handle(cls, job, *args, **kwargs):
        """
        Handle the execution of a `BackgroundJob`.

        This method is called by the Job Scheduler to handle the execution of all job commands. It will maintain the
        job's metadata and handle errors. For periodic jobs, a new job is automatically scheduled using its `interval'.
        """
        try:
            job.start()
            cls.run(job, *args, **kwargs)
            job.terminate()

        except Exception as e:
            job.terminate(status=JobStatusChoices.STATUS_ERRORED, error=repr(e))
            if type(e) is JobTimeoutException:
                logging.error(e)

        # If the executed job is a periodic job, schedule its next execution at the specified interval.
        finally:
            if job.interval:
                new_scheduled_time = (job.scheduled or job.started) + timedelta(minutes=job.interval)
                cls.enqueue(
                    instance=job.object,
                    name=job.name,
                    user=job.user,
                    schedule_at=new_scheduled_time,
                    interval=job.interval,
                    **kwargs,
                )

    @classmethod
    def enqueue(cls, *args, **kwargs):
        """
        Enqueue a new `BackgroundJob`.

        This method is a wrapper of `Job.enqueue()` using `handle()` as function callback. See its documentation for
        parameters.
        """
        return Job.enqueue(cls.handle, *args, **kwargs)


class ScheduledJob(BackgroundJob):
    """
    A periodic `BackgroundJob` that is scheduled only once for each configuration.

    This class can be used to schedule a `BackgroundJob` with a specific configuration. However, it will ensure that
    this job is scheduled exactly once in the queue of scheduled jobs, i.e. it will be skipped if an instance of this
    job is already scheduled. Like a regular `BackgroundJob`, this class also accepts intervals.

    The purpose of this class is to decouple jobs from the usual request-based approach. A practical example of this is
    to schedule a periodic synchronization job for a particular object. All that matters is that the job is scheduled
    and executed periodically. However, a new periodic job does not need to be scheduled every time the object is saved.
    Calling the `schedule()` method of this class will ensure that the job's schedule is set up no matter how often the
    method is called.
    """

    ENQUEUED_STATUS = [
        JobStatusChoices.STATUS_PENDING,
        JobStatusChoices.STATUS_SCHEDULED,
        JobStatusChoices.STATUS_RUNNING,
    ]

    @classmethod
    def get_jobs(cls, instance):
        """
        Get all jobs of this schedule related to a specific instance.
        """
        object_type = ObjectType.objects.get_for_model(instance, for_concrete_model=False)
        return Job.objects.filter(
            object_type=object_type,
            object_id=instance.pk,
            name=cls.__name__,
        )

    @classmethod
    def enqueue(cls, *args, **kwargs):
        """
        Enqueue a new `BackgroundJob`.

        This method is a wrapper of `Job.enqueue()` using `handle()` as function callback. See its documentation for
        parameters. Note that specifying a custom `name` is not supported, as a `ScheduledJob` is identified by the job
        class `__name__` automatically.
        """
        kwargs.pop('name', None)
        return super().enqueue(name=cls.__name__, *args, **kwargs)

    @classmethod
    @advisory_lock(ADVISORY_LOCK_KEYS['job-schedules'])
    def schedule(cls, instance, interval=None, *args, **kwargs):
        """
        Schedule a `ScheduledJob`.

        This method adds a new `ScheduledJob` to the job queue. If the job schedule identified by its `instance` and
        name is already active, the existing job will be updated if needed. However, this doesn't forbid running
        additional jobs using the `enqueue()` method, e.g. to schedule an immediate synchronization job in addition to
        periodic synchronization scheduled by this method.

        For additional parameters see `enqueue()`.

        Args:
            instance: The NetBox object to which this `ScheduledJob` pertains
            interval: Recurrence interval (in minutes)
        """
        job = cls.get_jobs(instance).filter(status__in=cls.ENQUEUED_STATUS).first()
        if job:
            # If the job parameters haven't changed, don't schedule a new job and keep the current schedule. Otherwise,
            # delete the existing job and schedule a new job instead.
            if job.interval == interval:
                return job
            job.delete()

        return cls.enqueue(instance=instance, interval=interval, *args, **kwargs)

    @classmethod
    def setup(cls, *args, **kwargs):
        """
        Setu p a new `ScheduledJob` during plugin initialization.

        This method should be called from the plugins `ready()` function to set up the schedule as early as possible.
        For interactive setup of schedules (e.g. on user requests), use either `schedule()` or `enqueue()` instead.
        """
        connection_created.connect(lambda sender, **signal_kwargs: cls.schedule(*args, **kwargs))
