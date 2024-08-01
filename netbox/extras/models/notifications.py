from functools import cached_property

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from extras.querysets import NotificationQuerySet
from netbox.models import ChangeLoggedModel
from netbox.registry import registry
from users.models import User
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'Notification',
    'NotificationGroup',
    'Subscription',
)


def get_event_type_choices():
    """
    Compile a list of choices from all registered event types
    """
    return [
        (name, event.text)
        for name, event in registry['event_types'].items()
    ]


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
        null=True,
        blank=True
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
    event_type = models.CharField(
        verbose_name=_('event'),
        max_length=50,
        choices=get_event_type_choices
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
        return reverse('account:notifications')

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if self.object_type not in ObjectType.objects.with_feature('notifications'):
            raise ValidationError(
                _("Objects of this type ({type}) do not support notifications.").format(type=self.object_type)
            )

    @cached_property
    def event(self):
        """
        Returns the registered Event which triggered this Notification.
        """
        return registry['event_types'].get(self.event_type)


class NotificationGroup(ChangeLoggedModel):
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:notificationgroup', args=[self.pk])

    @cached_property
    def members(self):
        """
        Return all Users who belong to this notification group.
        """
        return self.users.union(
            User.objects.filter(groups__in=self.groups.all())
        ).order_by('username')

    def notify(self, **kwargs):
        """
        Bulk-create Notifications for all members of this group.
        """
        Notification.objects.bulk_create([
            Notification(user=member, **kwargs)
            for member in self.members
        ])
    notify.alters_data = True


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
        on_delete=models.CASCADE,
        related_name='subscriptions'
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

    def __str__(self):
        if self.object:
            return str(self.object)
        return super().__str__()

    def get_absolute_url(self):
        return reverse('account:subscriptions')

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if self.object_type not in ObjectType.objects.with_feature('notifications'):
            raise ValidationError(
                _("Objects of this type ({type}) do not support notifications.").format(type=self.object_type)
            )
