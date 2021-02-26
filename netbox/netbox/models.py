from collections import OrderedDict

from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import ValidationError
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from utilities.mptt import TreeManager
from utilities.utils import serialize_object

__all__ = (
    'BigIDModel',
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

    def to_objectchange(self, action):
        """
        Return a new ObjectChange representing a change made to this object. This will typically be called automatically
        by ChangeLoggingMiddleware.
        """
        from extras.models import ObjectChange
        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            object_data=serialize_object(self)
        )


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


class PrimaryModel(ChangeLoggingMixin, CustomFieldsMixin, BigIDModel):
    """
    Primary models represent real objects within the infrastructure being modeled.
    """
    # TODO
    # tags = TaggableManager(through=TaggedItem)

    class Meta:
        abstract = True


class NestedGroupModel(ChangeLoggingMixin, CustomFieldsMixin, BigIDModel, MPTTModel):
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

    def to_objectchange(self, action):
        # Remove MPTT-internal fields
        from extras.models import ObjectChange
        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            object_data=serialize_object(self, exclude=['level', 'lft', 'rght', 'tree_id'])
        )


class OrganizationalModel(ChangeLoggingMixin, CustomFieldsMixin, BigIDModel):
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
