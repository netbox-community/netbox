from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

from extras.utils import extras_features
from netbox.models import ChangeLoggedModel, NestedGroupModel, OrganizationalModel, PrimaryModel
from utilities.querysets import RestrictedQuerySet
from .choices import *


__all__ = (
    'ContactAssignment',
    'Contact',
    'ContactGroup',
    'ContactRole',
    'Tenant',
    'TenantGroup',
)


#
# Tenants
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
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
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('tenancy:tenantgroup', args=[self.pk])


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
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
    description = models.CharField(
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = [
        'group', 'description',
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:tenant', args=[self.pk])


#
# Contacts
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class ContactGroup(NestedGroupModel):
    """
    An arbitrary collection of Contacts.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('tenancy:contactgroup', args=[self.pk])


@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class ContactRole(OrganizationalModel):
    """
    Functional role for a Contact assigned to an object.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:contactrole', args=[self.pk])


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class Contact(PrimaryModel):
    """
    Contact information for a particular object(s) in NetBox.
    """
    group = models.ForeignKey(
        to='tenancy.ContactGroup',
        on_delete=models.SET_NULL,
        related_name='contacts',
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=100
    )
    title = models.CharField(
        max_length=100,
        blank=True
    )
    phone = models.CharField(
        max_length=50,
        blank=True
    )
    email = models.EmailField(
        blank=True
    )
    address = models.CharField(
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = [
        'group',
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:contact', args=[self.pk])


@extras_features('webhooks')
class ContactAssignment(ChangeLoggedModel):
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    contact = models.ForeignKey(
        to='tenancy.Contact',
        on_delete=models.PROTECT,
        related_name='assignments'
    )
    role = models.ForeignKey(
        to='tenancy.ContactRole',
        on_delete=models.PROTECT,
        related_name='assignments'
    )
    priority = models.CharField(
        max_length=50,
        choices=ContactPriorityChoices,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('priority', 'contact')
