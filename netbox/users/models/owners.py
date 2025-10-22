from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import AdminModel
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'Owner',
)


class Owner(AdminModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=150,
        unique=True,
    )
    groups = models.ManyToManyField(
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
    clone_fields = ('groups', 'users')

    class Meta:
        ordering = ('name',)
        verbose_name = _('owner')
        verbose_name_plural = _('owners')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('users:owner', args=[self.pk])
