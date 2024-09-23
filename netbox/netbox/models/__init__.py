from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from netbox.models.features import *
from utilities.mptt import TreeManager
from utilities.querysets import RestrictedQuerySet


__all__ = (
    'ChangeLoggedModel',
    'NestedGroupModel',
    'NetBoxModel',
    'OrganizationalModel',
    'PrimaryModel',
)


class NetBoxFeatureSet(
    BookmarksMixin,
    ChangeLoggingMixin,
    CloningMixin,
    CustomFieldsMixin,
    CustomLinksMixin,
    CustomValidationMixin,
    ExportTemplatesMixin,
    JournalingMixin,
    NotificationsMixin,
    TagsMixin,
    EventRulesMixin
):
    class Meta:
        abstract = True

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/{self._meta.app_label}/{self._meta.model_name}/'


#
# Base model classes
#

class ChangeLoggedModel(ChangeLoggingMixin, CustomValidationMixin, EventRulesMixin, models.Model):
    """
    Base model for ancillary models; provides limited functionality for models which don't
    support NetBox's full feature set.
    """
    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True


class NetBoxModel(NetBoxFeatureSet, models.Model):
    """
    Base model for most object types. Suitable for use by plugins.
    """
    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True

    def clean(self):
        """
        Validate the model for GenericForeignKey fields to ensure that the content type and object ID exist.
        """
        super().clean()

        for field in self._meta.get_fields():
            if isinstance(field, GenericForeignKey):
                ct_value = getattr(self, field.ct_field, None)
                fk_value = getattr(self, field.fk_field, None)

                if ct_value is None and fk_value is not None:
                    raise ValidationError({
                        field.ct_field: "This field cannot be null.",
                    })
                if fk_value is None and ct_value is not None:
                    raise ValidationError({
                        field.fk_field: "This field cannot be null.",
                    })

                if ct_value and fk_value:
                    klass = getattr(self, field.ct_field).model_class()
                    try:
                        obj = klass.objects.get(pk=fk_value)
                    except ObjectDoesNotExist:
                        raise ValidationError({
                            field.fk_field: f"Related object not found using the provided value: {fk_value}."
                        })

                    # update the GFK field value
                    setattr(self, field.name, obj)


#
# NetBox internal base models
#

class PrimaryModel(NetBoxModel):
    """
    Primary models represent real objects within the infrastructure being modeled.
    """
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        verbose_name=_('comments'),
        blank=True
    )

    class Meta:
        abstract = True


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
        verbose_name=_('name'),
        max_length=100
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100
    )
    description = models.CharField(
        verbose_name=_('description'),
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
        if not self._state.adding and self.parent and self.parent in self.get_descendants(include_self=True):
            raise ValidationError({
                "parent": "Cannot assign self or child {type} as parent.".format(type=self._meta.verbose_name)
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
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name
