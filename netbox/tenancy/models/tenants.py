from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.urls import reverse

from netbox.models import NestedGroupModel, PrimaryModel

__all__ = (
    'Tenant',
    'TenantGroup',
)


class TenantGroup(NestedGroupModel):
    """
    An arbitrary collection of Tenants.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('tenancy:tenantgroup', args=[self.pk])


class Tenant(PrimaryModel):
    """
    A Tenant represents an organization served by the NetBox owner. This is typically a customer or an internal
    department.
    """
    name = models.CharField(
        max_length=100
    )
    slug = models.SlugField(
        max_length=100
    )
    group = models.ForeignKey(
        to='tenancy.TenantGroup',
        on_delete=models.SET_NULL,
        related_name='tenants',
        blank=True,
        null=True
    )

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    clone_fields = (
        'group', 'description',
    )

    class Meta:
        ordering = ['name']
        constraints = (
            models.UniqueConstraint(
                fields=('group', 'name'),
                name='%(app_label)s_%(class)s_unique_group_name',
                violation_error_message="Tenant name must be unique per group."
            ),
            models.UniqueConstraint(
                fields=('name',),
                name='%(app_label)s_%(class)s_unique_name',
                condition=Q(group__isnull=True)
            ),
            models.UniqueConstraint(
                fields=('group', 'slug'),
                name='%(app_label)s_%(class)s_unique_group_slug',
                violation_error_message="Tenant slug must be unique per group."
            ),
            models.UniqueConstraint(
                fields=('slug',),
                name='%(app_label)s_%(class)s_unique_slug',
                condition=Q(group__isnull=True)
            ),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:tenant', args=[self.pk])
