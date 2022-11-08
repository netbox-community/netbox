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
    'Change',
)

logger = logging.getLogger('netbox.staging')


class Branch(ChangeLoggedModel):
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

    def merge(self):
        logger.info(f'Merging changes in branch {self}')
        with transaction.atomic():
            for change in self.changes.all():
                change.apply()
        self.changes.all().delete()


class Change(ChangeLoggedModel):
    branch = models.ForeignKey(
        to=Branch,
        on_delete=models.CASCADE,
        related_name='changes'
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
        constraints = (
            models.UniqueConstraint(
                fields=('branch', 'object_type', 'object_id'),
                name='extras_change_unique_branch_object'
            ),
        )

    def apply(self):
        model = self.object_type.model_class()
        pk = self.object_id

        if self.action == ChangeActionChoices.ACTION_CREATE:
            instance = deserialize_object(model, self.data, pk=pk)
            logger.info(f'Creating {model} {instance}')
            instance.save()

        if self.action == ChangeActionChoices.ACTION_UPDATE:
            instance = deserialize_object(model, self.data, pk=pk)
            logger.info(f'Updating {model} {instance}')
            instance.save()

        if self.action == ChangeActionChoices.ACTION_DELETE:
            instance = model.objects.get(pk=self.object_id)
            logger.info(f'Deleting {model} {instance}')
            instance.delete()
