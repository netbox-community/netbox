from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from taggit.managers import TaggableManager

from extras.models import CustomFieldModel
from utilities.models import ChangeLoggedModel


@python_2_unicode_compatible
class TenantGroup(ChangeLoggedModel):
    """
    An arbitrary collection of Tenants.
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )

    csv_headers = ['name', 'slug']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?group={}".format(reverse('tenancy:tenant_list'), self.slug)

    def to_csv(self):
        return (
            self.name,
            self.slug,
        )


@python_2_unicode_compatible
class Tenant(ChangeLoggedModel, CustomFieldModel):
    """
    A Tenant represents an organization served by the NetBox owner. This is typically a customer or an internal
    department.
    """
    name = models.CharField(
        max_length=30,
        unique=True
    )
    slug = models.SlugField(
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
        max_length=100,
        blank=True,
        help_text='Long-form name (optional)'
    )
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    tags = TaggableManager()

    csv_headers = ['name', 'slug', 'group', 'description', 'comments']

    class Meta:
        ordering = ['group', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:tenant', args=[self.slug])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.group.name if self.group else None,
            self.description,
            self.comments,
        )
