import logging

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.conf import settings
from django.urls import reverse

from extras.choices import ChangeActionChoices, \
    ReviewRequestStateChoices, \
    ReviewRequestStatusChoices
from netbox.models import ChangeLoggedModel, NetBoxModel
from utilities.utils import deserialize_object

__all__ = (
    'Branch',
    'StagedChange',
    'Notification',
    'ReviewRequest',
)

logger = logging.getLogger('netbox.staging')


class Branch(ChangeLoggedModel):
    """
    A collection of related StagedChanges.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        models_changed = set()
        for sc in self.staged_changes.all().exclude(object_type__model='objectchange'):
            models_changed.add(sc.model_name)
        models_changed = list(models_changed)
        if len(models_changed) == 1:
            return f'Changes on {models_changed[0]} by {self.user}'
        else:
            dots = '' if len(models_changed) <= 3 else '...'
            changed = ', '.join(models_changed[:3])
            return f'Multiple changes on {changed}{dots} by {self.user}'

    def merge(self):
        logger.info(f'Merging changes in branch {self}')
        with transaction.atomic():
            for change in self.staged_changes.all():
                change.apply()


class StagedChange(ChangeLoggedModel):
    """
    The prepared creation, modification, or deletion of an object to be applied to the active database at a
    future point.
    """
    branch = models.ForeignKey(
        to=Branch,
        on_delete=models.CASCADE,
        related_name='staged_changes'
    )
    action = models.CharField(
        max_length=20,
        choices=ChangeActionChoices
    )
    object_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        related_name='+'
    )
    object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    object = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id'
    )
    data = models.JSONField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('pk',)

    def __str__(self):
        action = self.get_action_display()
        app_label, model_name = self.object_type.natural_key()
        return f"{action} {app_label}.{model_name} ({self.object_id})"

    @property
    def model(self):
        return self.object_type.model_class()

    @property
    def model_name(self):
        return self.object_type.name

    @property
    def diff_added(self):
        return getattr(self, '_diff_added', {})

    @property
    def diff_removed(self):
        return getattr(self, '_diff_removed', {})

    def apply(self):
        """
        Apply the staged create/update/delete action to the database.
        """
        if self.action == ChangeActionChoices.ACTION_CREATE:
            instance = deserialize_object(self.model, self.data, pk=self.object_id)
            logger.info(f'Creating {self.model._meta.verbose_name} {instance}')
            instance.save()

        if self.action == ChangeActionChoices.ACTION_UPDATE:
            instance = deserialize_object(self.model, self.data, pk=self.object_id)
            logger.info(f'Updating {self.model._meta.verbose_name} {instance}')
            instance.save()

        if self.action == ChangeActionChoices.ACTION_DELETE:
            instance = self.model.objects.get(pk=self.object_id)
            logger.info(f'Deleting {self.model._meta.verbose_name} {instance}')
            instance.delete()


class Notification(NetBoxModel):
    """
    Notifications allow users to keep up to date with system events or requests.

    Originally implemented to support the use case when a user is notified that a ReviewRequest
    has been assigned to her.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        max_length=256
    )

    content = models.TextField()

    read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f'[UserID: {self.user.pk}, Read: {self.read}] {self.title} {self.content}'

    def get_absolute_url(self):
        return reverse('extras-api:notifications-detail', args=[self.pk])

    class Meta:
        ordering = ('pk',)


class ReviewRequest(ChangeLoggedModel):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_requests'
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_review_requests'
    )

    # TODO: Make sure its corresponding branch and staged
    #       changes are deleted when this entry is deleted.
    #       atm this is not happening.
    branch = models.ForeignKey(
        to=Branch,
        on_delete=models.CASCADE,
        related_name='review_request'
    )

    status = models.CharField(
        max_length=256,
        choices=ReviewRequestStatusChoices,
        default=ReviewRequestStatusChoices.STATUS_OPEN
    )

    state = models.CharField(
        max_length=256,
        choices=ReviewRequestStateChoices,
        default=ReviewRequestStateChoices.STATE_UNDER_REVIEW
    )

    def __str__(self):
        return f'{self.branch}'

    def get_absolute_url(self):
        return reverse('extras:reviewrequest', args=[self.pk])

    class Meta:
        ordering = ('pk',)
