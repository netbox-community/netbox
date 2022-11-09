from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
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
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:tenant', args=[self.pk])
