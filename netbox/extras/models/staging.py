import logging

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from extras.choices import ChangeActionChoices
from netbox.models import ChangeLoggedModel
from utilities.utils import deserialize_object

__all__ = (
    'Branch',
    'StagedChange',
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
        return f'{self.name} ({self.pk})'

    def merge(self):
        logger.info(f'Merging changes in branch {self}')
        with transaction.atomic():
            for change in self.staged_changes.all():
                change.apply()
        self.staged_changes.all().delete()


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
