from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from extras.choices import *
from extras.querysets import NotificationQuerySet
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'Notification',
    'NotificationGroup',
    'Subscription',
)


class Notification(models.Model):
    """
    A notification message for a User relating to a specific object in NetBox.
    """
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True
    )
    read = models.DateTimeField(
        verbose_name=_('read'),
        null=True
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id'
    )
    kind = models.CharField(
        verbose_name=_('kind'),
        max_length=30,
        choices=NotificationKindChoices,
        default=NotificationKindChoices.KIND_INFO
    )
    event = models.CharField(
        verbose_name=_('event'),
        max_length=30,
        choices=NotificationEventChoices
    )

    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ('-created', 'pk')
        indexes = (
            models.Index(fields=('object_type', 'object_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('object_type', 'object_id', 'user'),
                name='%(app_label)s_%(class)s_unique_per_object_and_user'
            ),
        )
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')

    def __str__(self):
        if self.object:
            return str(self.object)
        return super().__str__()

    def get_absolute_url(self):
        return self.object.get_absolute_url()

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if self.object_type not in ObjectType.objects.with_feature('notifications'):
            raise ValidationError(
                _("Objects of this type ({type}) do not support notifications.").format(type=self.object_type)
            )


class NotificationGroup(models.Model):
    """
    A collection of users and/or groups to be informed for certain notifications.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    groups = models.ManyToManyField(
        to='users.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='notification_groups'
    )
    users = models.ManyToManyField(
        to='users.User',
        verbose_name=_('users'),
        blank=True,
        related_name='notification_groups'
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('name',)
        verbose_name = _('notification group')
        verbose_name_plural = _('notification groups')


class Subscription(models.Model):
    """
    A User's subscription to a particular object, to be notified of changes.
    """
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id'
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('-created', 'user')
        indexes = (
            models.Index(fields=('object_type', 'object_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('object_type', 'object_id', 'user'),
                name='%(app_label)s_%(class)s_unique_per_object_and_user'
            ),
        )
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if self.object_type not in ObjectType.objects.with_feature('notifications'):
            raise ValidationError(
                _("Objects of this type ({type}) do not support notifications.").format(type=self.object_type)
            )
