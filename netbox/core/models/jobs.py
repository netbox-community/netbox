import uuid

import django_rq
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from core.choices import JobStatusChoices
from extras.constants import EVENT_JOB_END, EVENT_JOB_START
from extras.utils import FeatureQuery
from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT
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
        to=ContentType,
        related_name='jobs',
        limit_choices_to=FeatureQuery('jobs'),
        on_delete=models.CASCADE,
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
        max_length=200
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    scheduled = models.DateTimeField(
        null=True,
        blank=True
    )
    interval = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=(
            MinValueValidator(1),
        ),
        help_text=_("Recurrence interval (in minutes)")
    )
    started = models.DateTimeField(
        null=True,
        blank=True
    )
    completed = models.DateTimeField(
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=30,
        choices=JobStatusChoices,
        default=JobStatusChoices.STATUS_PENDING
    )
    data = models.JSONField(
        null=True,
        blank=True
    )
    job_id = models.UUIDField(
        unique=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return str(self.job_id)

    def get_absolute_url(self):
        # TODO: Employ dynamic registration
        if self.object_type.model == 'reportmodule':
            return reverse(f'extras:report_result', kwargs={'job_pk': self.pk})
        if self.object_type.model == 'scriptmodule':
            return reverse(f'extras:script_result', kwargs={'job_pk': self.pk})
        return reverse('core:job', args=[self.pk])

    def get_status_color(self):
        return JobStatusChoices.colors.get(self.status)

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

        rq_queue_name = get_config().QUEUE_MAPPINGS.get(self.object_type.model, RQ_QUEUE_DEFAULT)
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

        # Handle webhooks
        self.trigger_webhooks(event=EVENT_JOB_START)

    def terminate(self, status=JobStatusChoices.STATUS_COMPLETED):
        """
        Mark the job as completed, optionally specifying a particular termination status.
        """
        valid_statuses = JobStatusChoices.TERMINAL_STATE_CHOICES
        if status not in valid_statuses:
            raise ValueError(f"Invalid status for job termination. Choices are: {', '.join(valid_statuses)}")

        # Mark the job as completed
        self.status = status
        self.completed = timezone.now()
        self.save()

        # Handle webhooks
        self.trigger_webhooks(event=EVENT_JOB_END)

    @classmethod
    def enqueue(cls, func, instance, name='', user=None, schedule_at=None, interval=None, **kwargs):
        """
        Create a Job instance and enqueue a job using the given callable

        Args:
            func: The callable object to be enqueued for execution
            instance: The NetBox object to which this job pertains
            name: Name for the job (optional)
            user: The user responsible for running the job
            schedule_at: Schedule the job to be executed at the passed date and time
            interval: Recurrence interval (in minutes)
        """
        object_type = ContentType.objects.get_for_model(instance, for_concrete_model=False)
        rq_queue_name = get_queue_for_model(object_type.model)
        queue = django_rq.get_queue(rq_queue_name)
        status = JobStatusChoices.STATUS_SCHEDULED if schedule_at else JobStatusChoices.STATUS_PENDING
        job = Job.objects.create(
            object_type=object_type,
            object_id=instance.pk,
            name=name,
            status=status,
            scheduled=schedule_at,
            interval=interval,
            user=user,
            job_id=uuid.uuid4()
        )

        if schedule_at:
            queue.enqueue_at(schedule_at, func, job_id=str(job.job_id), job=job, **kwargs)
        else:
            queue.enqueue(func, job_id=str(job.job_id), job=job, **kwargs)

        return job

    def trigger_webhooks(self, event):
        from extras.models import Webhook

        rq_queue_name = get_config().QUEUE_MAPPINGS.get('webhook', RQ_QUEUE_DEFAULT)
        rq_queue = django_rq.get_queue(rq_queue_name, is_async=False)

        # Fetch any webhooks matching this object type and action
        webhooks = Webhook.objects.filter(
            **{f'type_{event}': True},
            content_types=self.object_type,
            enabled=True
        )

        for webhook in webhooks:
            rq_queue.enqueue(
                "extras.webhooks_worker.process_webhook",
                webhook=webhook,
                model_name=self.object_type.model,
                event=event,
                data=self.data,
                timestamp=str(timezone.now()),
                username=self.user.username
            )
