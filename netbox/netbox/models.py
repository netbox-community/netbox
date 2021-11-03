import logging
from collections import OrderedDict

from django.contrib.contenttypes.fields import GenericRelation
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import ValidationError
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager

from extras.choices import ObjectChangeActionChoices
from netbox.signals import post_clean
from utilities.mptt import TreeManager
from utilities.utils import serialize_object

__all__ = (
    'BigIDModel',
    'ChangeLoggedModel',
    'NestedGroupModel',
    'OrganizationalModel',
    'PrimaryModel',
)


#
# Mixins
#

class ChangeLoggingMixin(models.Model):
    """
    Provides change logging support.
    """
    created = models.DateField(
        auto_now_add=True,
        blank=True,
        null=True
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def snapshot(self):
        """
        Save a snapshot of the object's current state in preparation for modification.
        """
        logger = logging.getLogger('netbox')
        logger.debug(f"Taking a snapshot of {self}")
        self._prechange_snapshot = serialize_object(self)

    def to_objectchange(self, action, related_object=None):
        """
        Return a new ObjectChange representing a change made to this object. This will typically be called automatically
        by ChangeLoggingMiddleware.
        """
        from extras.models import ObjectChange
        objectchange = ObjectChange(
            changed_object=self,
            related_object=related_object,
            object_repr=str(self),
            action=action
        )
        if hasattr(self, '_prechange_snapshot'):
            objectchange.prechange_data = self._prechange_snapshot
        if action in (ObjectChangeActionChoices.ACTION_CREATE, ObjectChangeActionChoices.ACTION_UPDATE):
            objectchange.postchange_data = serialize_object(self)

        return objectchange


class CustomFieldsMixin(models.Model):
    """
    Provides support for custom fields.
    """
    custom_field_data = models.JSONField(
        encoder=DjangoJSONEncoder,
        blank=True,
        default=dict
    )

    class Meta:
        abstract = True

    @property
    def cf(self):
        """
        Convenience wrapper for custom field data.
        """
        return self.custom_field_data

    def get_custom_fields(self):
        """
        Return a dictionary of custom fields for a single object in the form {<field>: value}.
        """
        from extras.models import CustomField

        fields = CustomField.objects.get_for_model(self)
        return OrderedDict([
            (field, self.custom_field_data.get(field.name)) for field in fields
        ])

    def clean(self):
        super().clean()
        from extras.models import CustomField

        custom_fields = {cf.name: cf for cf in CustomField.objects.get_for_model(self)}

        # Validate all field values
        for field_name, value in self.custom_field_data.items():
            if field_name not in custom_fields:
                raise ValidationError(f"Unknown field name '{field_name}' in custom field data.")
            try:
                custom_fields[field_name].validate(value)
            except ValidationError as e:
                raise ValidationError(f"Invalid value for custom field '{field_name}': {e.message}")

        # Check for missing required values
        for cf in custom_fields.values():
            if cf.required and cf.name not in self.custom_field_data:
                raise ValidationError(f"Missing required custom field '{cf.name}'.")


class CustomValidationMixin(models.Model):
    """
    Enables user-configured validation rules for built-in models by extending the clean() method.
    """
    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        # Send the post_clean signal
        post_clean.send(sender=self.__class__, instance=self)


#
# Base model classes

class BigIDModel(models.Model):
    """
    Abstract base model for all data objects. Ensures the use of a 64-bit PK.
    """
    id = models.BigAutoField(
        primary_key=True
    )

    class Meta:
        abstract = True


class ChangeLoggedModel(ChangeLoggingMixin, CustomValidationMixin, BigIDModel):
    """
    Base model for all objects which support change logging.
    """
    class Meta:
        abstract = True


class PrimaryModel(ChangeLoggingMixin, CustomFieldsMixin, CustomValidationMixin, BigIDModel):
    """
    Primary models represent real objects within the infrastructure being modeled.
    """
    journal_entries = GenericRelation(
        to='extras.JournalEntry',
        object_id_field='assigned_object_id',
        content_type_field='assigned_object_type'
    )
    tags = TaggableManager(
        through='extras.TaggedItem'
    )

    class Meta:
        abstract = True


class NestedGroupModel(ChangeLoggingMixin, CustomFieldsMixin, CustomValidationMixin, BigIDModel, MPTTModel):
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
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({
                "parent": "Cannot assign self as parent."
            })


class OrganizationalModel(ChangeLoggingMixin, CustomFieldsMixin, CustomValidationMixin, BigIDModel):
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

    class Meta:
        abstract = True
        ordering = ('name',)
