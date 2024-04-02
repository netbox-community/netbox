from django.contrib.auth.models import (
    AbstractUser,
    GroupManager as DjangoGroupManager,
    Permission,
    UserManager as DjangoUserManager
)
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from utilities.querysets import RestrictedQuerySet

__all__ = (
    'Group',
    'GroupManager',
    'User',
    'UserManager',
)


class GroupManager(DjangoGroupManager.from_queryset(RestrictedQuerySet)):
    pass


class Group(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=150,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    object_permissions = models.ManyToManyField(
        to='users.ObjectPermission',
        blank=True,
        related_name='groups'
    )

    # Replicate legacy Django permissions support from stock Group model
    # to ensure authentication backend compatibility
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
        related_name='groups',
        related_query_name='group'
    )

    objects = GroupManager()

    class Meta:
        ordering = ('name',)
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('users:group', args=[self.pk])

    def natural_key(self):
        return (self.name,)


class UserManager(DjangoUserManager.from_queryset(RestrictedQuerySet)):
    pass


class User(AbstractUser):
    groups = models.ManyToManyField(
        to='users.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='users',
        related_query_name='user'
    )
    object_permissions = models.ManyToManyField(
        to='users.ObjectPermission',
        blank=True,
        related_name='users'
    )

    objects = UserManager()

    class Meta:
        ordering = ('username',)
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return reverse('users:user', args=[self.pk])

    def clean(self):
        super().clean()

        # Check for any existing Users with names that differ only in case
        model = self._meta.model
        if model.objects.exclude(pk=self.pk).filter(username__iexact=self.username).exists():
            raise ValidationError(_("A user with this username already exists."))
