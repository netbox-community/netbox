from django.core.validators import ValidationError
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from extras.utils import is_taggable
from utilities.mptt import TreeManager
from utilities.querysets import RestrictedQuerySet
from netbox.models.features import *

__all__ = (
    'ChangeLoggedModel',
    'NestedGroupModel',
    'OrganizationalModel',
    'NetBoxModel',
)


class NetBoxFeatureSet(
    ChangeLoggingMixin,
    CustomFieldsMixin,
    CustomLinksMixin,
    CustomValidationMixin,
    ExportTemplatesMixin,
    JournalingMixin,
    TagsMixin,
    WebhooksMixin
):
    class Meta:
        abstract = True

    @classmethod
    def get_prerequisite_models(cls):
        """
        Return a list of model types that are required to create this model or empty list if none.  This is used for
        showing prequisite warnings in the UI on the list and detail views.
        """
        return []


#
# Base model classes
#

class ChangeLoggedModel(ChangeLoggingMixin, CustomValidationMixin, models.Model):
    """
    Base model for ancillary models; provides limited functionality for models which don't
    support NetBox's full feature set.
    """
    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True


class NetBoxModel(NetBoxFeatureSet, models.Model):
    """
    Primary models represent real objects within the infrastructure being modeled.
    """
    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True

    def clone(self):
        """
        Return a dictionary of attributes suitable for creating a copy of the current instance. This is used for pre-
        populating an object creation form in the UI.
        """
        attrs = {}

        for field_name in getattr(self, 'clone_fields', []):
            field = self._meta.get_field(field_name)
            field_value = field.value_from_object(self)
            if field_value not in (None, ''):
                attrs[field_name] = field_value

        # Include tags (if applicable)
        if is_taggable(self):
            attrs['tags'] = [tag.pk for tag in self.tags.all()]

        return attrs


class NestedGroupModel(NetBoxFeatureSet, MPTTModel):
    """
    Base model for objects which are used to form a hierarchy (regions, locations, etc.). These models nest
    recursively using MPTT. Within each parent, each child instance must have a unique name.
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = TreeManager()

    class Meta:
        abstract = True

    class MPTTMeta:
        order_insertion_by = ('name',)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # An MPTT model cannot be its own parent
        if self.pk and self.parent and self.parent in self.get_descendants(include_self=True):
            raise ValidationError({
                "parent": f"Cannot assign self or child {self._meta.verbose_name} as parent."
            })


class OrganizationalModel(NetBoxFeatureSet, models.Model):
    """
    Organizational models are those which are used solely to categorize and qualify other objects, and do not convey
    any real information about the infrastructure being modeled (for example, functional device roles). Organizational
    models provide the following standard attributes:
    - Unique name
    - Unique slug (automatically derived from name)
    - Optional description
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
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ('name',)
