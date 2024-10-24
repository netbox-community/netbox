import uuid

import django_rq
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from core.choices import JobStatusChoices
from core.models import ObjectType
from core.signals import job_end, job_start
from utilities.querysets import RestrictedQuerySet
from utilities.rqworker import get_queue_for_model

__all__ = (
    'Job',
)


class Job(models.Model):
    """
    Tracks the lifecycle of a job which represents a background task (e.g. the execution of a custom script).
    """
    object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        related_name='jobs',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    object = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id',
        for_concrete_model=False
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=200
    )
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True
    )
    scheduled = models.DateTimeField(
        verbose_name=_('scheduled'),
        null=True,
        blank=True
    )
    interval = models.PositiveIntegerField(
        verbose_name=_('interval'),
        blank=True,
        null=True,
        validators=(
            MinValueValidator(1),
        ),
        help_text=_('Recurrence interval (in minutes)')
    )
    started = models.DateTimeField(
        verbose_name=_('started'),
        null=True,
        blank=True
    )
    completed = models.DateTimeField(
        verbose_name=_('completed'),
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=30,
        choices=JobStatusChoices,
        default=JobStatusChoices.STATUS_PENDING
    )
    data = models.JSONField(
        verbose_name=_('data'),
        null=True,
        blank=True
    )
    error = models.TextField(
        verbose_name=_('error'),
        editable=False,
        blank=True
    )
    job_id = models.UUIDField(
        verbose_name=_('job ID'),
        unique=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['-created']
        indexes = (
            models.Index(fields=('object_type', 'object_id')),
        )
        verbose_name = _('job')
        verbose_name_plural = _('jobs')

    def __str__(self):
        return str(self.job_id)

    def get_absolute_url(self):
        # TODO: Employ dynamic registration
        if self.object_type:
            if self.object_type.model == 'reportmodule':
                return reverse('extras:report_result', kwargs={'job_pk': self.pk})
            elif self.object_type.model == 'scriptmodule':
                return reverse('extras:script_result', kwargs={'job_pk': self.pk})
        return reverse('core:job', args=[self.pk])

    def get_status_color(self):
        return JobStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if self.object_type and self.object_type not in ObjectType.objects.with_feature('jobs'):
            raise ValidationError(
                _("Jobs cannot be assigned to this object type ({type}).").format(type=self.object_type)
            )

    @property
    def duration(self):
        if not self.completed:
            return None

        start_time = self.started or self.created

        if not start_time:
            return None

        duration = self.completed - start_time
        minutes, seconds = divmod(duration.total_seconds(), 60)

        return f"{int(minutes)} minutes, {seconds:.2f} seconds"

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        rq_queue_name = get_queue_for_model(self.object_type.model if self.object_type else None)
        queue = django_rq.get_queue(rq_queue_name)
        job = queue.fetch_job(str(self.job_id))

        if job:
            job.cancel()

    def start(self):
        """
        Record the job's start time and update its status to "running."
        """
        if self.started is not None:
            return

        # Start the job
        self.started = timezone.now()
        self.status = JobStatusChoices.STATUS_RUNNING
        self.save()

        # Send signal
        job_start.send(self)

    def terminate(self, status=JobStatusChoices.STATUS_COMPLETED, error=None):
        """
        Mark the job as completed, optionally specifying a particular termination status.
        """
        valid_statuses = JobStatusChoices.TERMINAL_STATE_CHOICES
        if status not in valid_statuses:
            raise ValueError(
                _("Invalid status for job termination. Choices are: {choices}").format(
                    choices=', '.join(valid_statuses)
                )
            )

        # Mark the job as completed
        self.status = status
        if error:
            self.error = error
        self.completed = timezone.now()
        self.save()

        # Send signal
        job_end.send(self)

    @classmethod
    def enqueue(cls, func, instance=None, name='', user=None, schedule_at=None, interval=None, immediate=False, **kwargs):
        """
        Create a Job instance and enqueue a job using the given callable

        Args:
            func: The callable object to be enqueued for execution
            instance: The NetBox object to which this job pertains (optional)
            name: Name for the job (optional)
            user: The user responsible for running the job
            schedule_at: Schedule the job to be executed at the passed date and time
            interval: Recurrence interval (in minutes)
            immediate: Run the job immediately without scheduling it in the background. Should be used for interactive
                management commands only.
        """
        if schedule_at and immediate:
            raise ValueError(_("enqueue() cannot be called with values for both schedule_at and immediate."))

        if instance:
            object_type = ObjectType.objects.get_for_model(instance, for_concrete_model=False)
            object_id = instance.pk
        else:
            object_type = object_id = None
        rq_queue_name = get_queue_for_model(object_type.model if object_type else None)
        queue = django_rq.get_queue(rq_queue_name)
        status = JobStatusChoices.STATUS_SCHEDULED if schedule_at else JobStatusChoices.STATUS_PENDING
        job = Job(
            object_type=object_type,
            object_id=object_id,
            name=name,
            status=status,
            scheduled=schedule_at,
            interval=interval,
            user=user,
            job_id=uuid.uuid4()
        )
        job.full_clean()
        job.save()

        # Run the job immediately, rather than enqueuing it as a background task. Note that this is a synchronous
        # (blocking) operation, and execution will pause until the job completes.
        if immediate:
            func(job_id=str(job.job_id), job=job, **kwargs)

        # Schedule the job to run at a specific date & time.
        elif schedule_at:
            queue.enqueue_at(schedule_at, func, job_id=str(job.job_id), job=job, **kwargs)

        # Schedule the job to run asynchronously at this first available opportunity.
        else:
            queue.enqueue(func, job_id=str(job.job_id), job=job, **kwargs)

        return job
