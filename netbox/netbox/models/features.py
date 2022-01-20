import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.signals import class_prepared
from django.dispatch import receiver

from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import ValidationError
from django.db import models
from taggit.managers import TaggableManager

from extras.choices import ObjectChangeActionChoices
from extras.utils import register_features
from netbox.signals import post_clean
from utilities.utils import serialize_object

__all__ = (
    'ChangeLoggingMixin',
    'CustomFieldsMixin',
    'CustomLinksMixin',
    'CustomValidationMixin',
    'ExportTemplatesMixin',
    'JobResultsMixin',
    'JournalingMixin',
    'TagsMixin',
    'WebhooksMixin',
)


#
# Feature mixins
#

class ChangeLoggingMixin(models.Model):
    """
    Provides change logging support for a model. Adds the `created` and `last_updated` fields.
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
            object_repr=str(self)[:200],
            action=action
        )
        if hasattr(self, '_prechange_snapshot'):
            objectchange.prechange_data = self._prechange_snapshot
        if action in (ObjectChangeActionChoices.ACTION_CREATE, ObjectChangeActionChoices.ACTION_UPDATE):
            objectchange.postchange_data = serialize_object(self)

        return objectchange


class CustomFieldsMixin(models.Model):
    """
    Enables support for custom fields.
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
        A pass-through convenience alias for accessing `custom_field_data` (read-only).

        ```python
        >>> tenant = Tenant.objects.first()
        >>> tenant.cf
        {'cust_id': 'CYB01'}
        ```
        """
        return self.custom_field_data

    def get_custom_fields(self):
        """
        Return a dictionary of custom fields for a single object in the form `{field: value}`.

        ```python
        >>> tenant = Tenant.objects.first()
        >>> tenant.get_custom_fields()
        {<CustomField: Customer ID>: 'CYB01'}
        ```
        """
        from extras.models import CustomField

        data = {}
        for field in CustomField.objects.get_for_model(self):
            value = self.custom_field_data.get(field.name)
            data[field] = field.deserialize(value)

        return data

    def clean(self):
        super().clean()
        from extras.models import CustomField

        custom_fields = {
            cf.name: cf for cf in CustomField.objects.get_for_model(self)
        }

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


class CustomLinksMixin(models.Model):
    """
    Enables support for custom links.
    """
    class Meta:
        abstract = True


class CustomValidationMixin(models.Model):
    """
    Enables user-configured validation rules for models.
    """
    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        # Send the post_clean signal
        post_clean.send(sender=self.__class__, instance=self)


class ExportTemplatesMixin(models.Model):
    """
    Enables support for export templates.
    """
    class Meta:
        abstract = True


class JobResultsMixin(models.Model):
    """
    Enables support for job results.
    """
    class Meta:
        abstract = True


class JournalingMixin(models.Model):
    """
    Enables support for object journaling. Adds a generic relation (`journal_entries`)
    to NetBox's JournalEntry model.
    """
    journal_entries = GenericRelation(
        to='extras.JournalEntry',
        object_id_field='assigned_object_id',
        content_type_field='assigned_object_type'
    )

    class Meta:
        abstract = True


class TagsMixin(models.Model):
    """
    Enables support for tag assignment. Assigned tags can be managed via the `tags` attribute,
    which is a `TaggableManager` instance.
    """
    tags = TaggableManager(
        through='extras.TaggedItem'
    )

    class Meta:
        abstract = True


class WebhooksMixin(models.Model):
    """
    Enables support for webhooks.
    """
    class Meta:
        abstract = True


FEATURES_MAP = (
    ('custom_fields', CustomFieldsMixin),
    ('custom_links', CustomLinksMixin),
    ('export_templates', ExportTemplatesMixin),
    ('job_results', JobResultsMixin),
    ('journaling', JournalingMixin),
    ('tags', TagsMixin),
    ('webhooks', WebhooksMixin),
)


@receiver(class_prepared)
def _register_features(sender, **kwargs):
    features = {
        feature for feature, cls in FEATURES_MAP if issubclass(sender, cls)
    }
    register_features(sender, features)
