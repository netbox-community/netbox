from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from users.constants import OBJECTPERMISSION_OBJECT_TYPES
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'ObjectPermission',
)


class ObjectPermission(models.Model):
    """
    A mapping of view, add, change, and/or delete permission for users and/or groups to an arbitrary set of objects
    identified by ORM query parameters.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    object_types = models.ManyToManyField(
        to='core.ObjectType',
        limit_choices_to=OBJECTPERMISSION_OBJECT_TYPES,
        related_name='object_permissions'
    )
    actions = ArrayField(
        base_field=models.CharField(max_length=30),
        help_text=_("The list of actions granted by this permission")
    )
    constraints = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('constraints'),
        help_text=_("Queryset filter matching the applicable objects of the selected type(s)")
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['name']
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')

    def __str__(self):
        return self.name

    @property
    def can_view(self):
        return 'view' in self.actions

    @property
    def can_add(self):
        return 'add' in self.actions

    @property
    def can_change(self):
        return 'change' in self.actions

    @property
    def can_delete(self):
        return 'delete' in self.actions

    def list_constraints(self):
        """
        Return all constraint sets as a list (even if only a single set is defined).
        """
        if type(self.constraints) is not list:
            return [self.constraints]
        return self.constraints

    def get_absolute_url(self):
        return reverse('users:objectpermission', args=[self.pk])
