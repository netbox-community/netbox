from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import AdminModel
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'Owner',
    'OwnerGroup',
)


class OwnerGroup(AdminModel):
    """
    An arbitrary grouping of Owners.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('owner group')
        verbose_name_plural = _('owner groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('users:ownergroup', args=[self.pk])


class Owner(AdminModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
    )
    group = models.ForeignKey(
        to='users.OwnerGroup',
        on_delete=models.PROTECT,
        related_name='members',
        verbose_name=_('group'),
        blank=True,
        null=True,
    )
    user_groups = models.ManyToManyField(
        to='users.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='owners',
        related_query_name='owner',
    )
    users = models.ManyToManyField(
        to='users.User',
        verbose_name=_('users'),
        blank=True,
        related_name='owners',
        related_query_name='owner',
    )

    objects = RestrictedQuerySet.as_manager()
    clone_fields = ('user_groups', 'users')

    class Meta:
        ordering = ('name',)
        verbose_name = _('owner')
        verbose_name_plural = _('owners')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('users:owner', args=[self.pk])
