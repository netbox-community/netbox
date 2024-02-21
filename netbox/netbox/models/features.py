import json
from collections import defaultdict
from functools import cached_property

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from core.choices import JobStatusChoices
from core.models import ContentType
from extras.choices import *
from extras.utils import is_taggable
from netbox.config import get_config
from netbox.registry import registry
from netbox.signals import post_clean
from utilities.json import CustomFieldJSONEncoder
from utilities.utils import serialize_object
from utilities.views import register_model_view

__all__ = (
    'BookmarksMixin',
    'ChangeLoggingMixin',
    'CloningMixin',
    'ContactsMixin',
    'CustomFieldsMixin',
    'CustomLinksMixin',
    'CustomValidationMixin',
    'EventRulesMixin',
    'ExportTemplatesMixin',
    'ImageAttachmentsMixin',
    'JobsMixin',
    'JournalingMixin',
    'SyncedDataMixin',
    'TagsMixin',
    'register_models',
)


#
# Feature mixins
#

class ChangeLoggingMixin(models.Model):
    """
    Provides change logging support for a model. Adds the `created` and `last_updated` fields.
    """
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True,
        blank=True,
        null=True
    )
    last_updated = models.DateTimeField(
        verbose_name=_('last updated'),
        auto_now=True,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def serialize_object(self, exclude=None):
        """
        Return a JSON representation of the instance. Models can override this method to replace or extend the default
        serialization logic provided by the `serialize_object()` utility function.

        Args:
            exclude: An iterable of attribute names to omit from the serialized output
        """
        return serialize_object(self, exclude=exclude or [])

    def snapshot(self):
        """
        Save a snapshot of the object's current state in preparation for modification. The snapshot is saved as
        `_prechange_snapshot` on the instance.
        """
        exclude_fields = []
        if get_config().CHANGELOG_SKIP_EMPTY_CHANGES:
            exclude_fields = ['last_updated',]

        self._prechange_snapshot = self.serialize_object(exclude=exclude_fields)
    snapshot.alters_data = True

    def to_objectchange(self, action):
        """
        Return a new ObjectChange representing a change made to this object. This will typically be called automatically
        by ChangeLoggingMiddleware.
        """
        from extras.models import ObjectChange

        exclude = []
        if get_config().CHANGELOG_SKIP_EMPTY_CHANGES:
            exclude = ['last_updated']

        objectchange = ObjectChange(
            changed_object=self,
            object_repr=str(self)[:200],
            action=action
        )
        if hasattr(self, '_prechange_snapshot'):
            objectchange.prechange_data = self._prechange_snapshot
        if action in (ObjectChangeActionChoices.ACTION_CREATE, ObjectChangeActionChoices.ACTION_UPDATE):
            objectchange.postchange_data = self.serialize_object(exclude=exclude)

        return objectchange


class CloningMixin(models.Model):
    """
    Provides the clone() method used to prepare a copy of existing objects.
    """
    class Meta:
        abstract = True

    def clone(self):
        """
        Returns a dictionary of attributes suitable for creating a copy of the current instance. This is used for pre-
        populating an object creation form in the UI. By default, this method will replicate any fields listed in the
        model's `clone_fields` list (if defined), but it can be overridden to apply custom logic.

        ```python
        class MyModel(NetBoxModel):
            def clone(self):
                attrs = super().clone()
                attrs['extra-value'] = 123
                return attrs
        ```
        """
        attrs = {}

        for field_name in getattr(self, 'clone_fields', []):
            field = self._meta.get_field(field_name)
            field_value = field.value_from_object(self)
            if field_value and isinstance(field, models.ManyToManyField):
                attrs[field_name] = [v.pk for v in field_value]
            elif field_value and isinstance(field, models.JSONField):
                attrs[field_name] = json.dumps(field_value)
            elif field_value not in (None, ''):
                attrs[field_name] = field_value

        # Include tags (if applicable)
        if is_taggable(self):
            attrs['tags'] = [tag.pk for tag in self.tags.all()]

        # Include any cloneable custom fields
        if hasattr(self, 'custom_fields'):
            for field in self.custom_fields:
                if field.is_cloneable:
                    attrs[f'cf_{field.name}'] = self.custom_field_data.get(field.name)

        return attrs


class CustomFieldsMixin(models.Model):
    """
    Enables support for custom fields.
    """
    custom_field_data = models.JSONField(
        encoder=CustomFieldJSONEncoder,
        blank=True,
        default=dict
    )

    class Meta:
        abstract = True

    @cached_property
    def cf(self):
        """
        Return a dictionary mapping each custom field for this instance to its deserialized value.

        ```python
        >>> tenant = Tenant.objects.first()
        >>> tenant.cf
        {'primary_site': <Site: DM-NYC>, 'cust_id': 'DMI01', 'is_active': True}
        ```
        """
        return {
            cf.name: cf.deserialize(self.custom_field_data.get(cf.name))
            for cf in self.custom_fields
        }

    @cached_property
    def custom_fields(self):
        """
        Return the QuerySet of CustomFields assigned to this model.

        ```python
        >>> tenant = Tenant.objects.first()
        >>> tenant.custom_fields
        <RestrictedQuerySet [<CustomField: Primary site>, <CustomField: Customer ID>, <CustomField: Is active>]>
        ```
        """
        from extras.models import CustomField
        return CustomField.objects.get_for_model(self)

    def get_custom_fields(self, omit_hidden=False):
        """
        Return a dictionary of custom fields for a single object in the form `{field: value}`.

        ```python
        >>> tenant = Tenant.objects.first()
        >>> tenant.get_custom_fields()
        {<CustomField: Customer ID>: 'CYB01'}
        ```

        Args:
            omit_hidden: If True, custom fields with no UI visibility will be omitted.
        """
        from extras.models import CustomField
        data = {}

        for field in CustomField.objects.get_for_model(self):
            value = self.custom_field_data.get(field.name)

            # Skip hidden fields if 'omit_hidden' is True
            if omit_hidden and field.ui_visible == CustomFieldUIVisibleChoices.HIDDEN:
                continue
            elif omit_hidden and field.ui_visible == CustomFieldUIVisibleChoices.IF_SET and not value:
                continue

            data[field] = field.deserialize(value)

        return data

    def get_custom_fields_by_group(self):
        """
        Return a dictionary of custom field/value mappings organized by group. Hidden fields are omitted.

        ```python
        >>> tenant = Tenant.objects.first()
        >>> tenant.get_custom_fields_by_group()
        {
            '': {<CustomField: Primary site>: <Site: DM-NYC>},
            'Billing': {<CustomField: Customer ID>: 'DMI01', <CustomField: Is active>: True}
        }
        ```
        """
        from extras.models import CustomField
        groups = defaultdict(dict)
        visible_custom_fields = CustomField.objects.get_for_model(self).exclude(
            ui_visible=CustomFieldUIVisibleChoices.HIDDEN
        )

        for cf in visible_custom_fields:
            value = self.custom_field_data.get(cf.name)
            if value in (None, '', []) and cf.ui_visible == CustomFieldUIVisibleChoices.IF_SET:
                continue
            value = cf.deserialize(value)
            groups[cf.group_name][cf] = value

        return dict(groups)

    def populate_custom_field_defaults(self):
        """
        Apply the default value for each custom field
        """
        for cf in self.custom_fields:
            self.custom_field_data[cf.name] = cf.default
    populate_custom_field_defaults.alters_data = True

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

        # If the instance is a base for replications, skip custom validation
        if getattr(self, '_replicated_base', False):
            return

        # Send the post_clean signal
        post_clean.send(sender=self.__class__, instance=self)


class ExportTemplatesMixin(models.Model):
    """
    Enables support for export templates.
    """
    class Meta:
        abstract = True


class ImageAttachmentsMixin(models.Model):
    """
    Enables the assignments of ImageAttachments.
    """
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    class Meta:
        abstract = True


class ContactsMixin(models.Model):
    """
    Enables the assignments of Contacts (via ContactAssignment).
    """
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    class Meta:
        abstract = True


class BookmarksMixin(models.Model):
    """
    Enables support for user bookmarks.
    """
    bookmarks = GenericRelation(
        to='extras.Bookmark',
        content_type_field='object_type',
        object_id_field='object_id'
    )

    class Meta:
        abstract = True


class JobsMixin(models.Model):
    """
    Enables support for job results.
    """
    jobs = GenericRelation(
        to='core.Job',
        content_type_field='object_type',
        object_id_field='object_id',
        for_concrete_model=False
    )

    class Meta:
        abstract = True

    def get_latest_jobs(self):
        """
        Return a dictionary mapping of the most recent jobs for this instance.
        """
        return {
            job.name: job
            for job in self.jobs.filter(
                status__in=JobStatusChoices.TERMINAL_STATE_CHOICES
            ).order_by('name', '-created').distinct('name').defer('data')
        }


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


class EventRulesMixin(models.Model):
    """
    Enables support for event rules, which can be used to transmit webhooks or execute scripts automatically.
    """
    class Meta:
        abstract = True


class SyncedDataMixin(models.Model):
    """
    Enables population of local data from a DataFile object, synchronized from a remote DataSource.
    """
    data_source = models.ForeignKey(
        to='core.DataSource',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='+',
        help_text=_("Remote data source")
    )
    data_file = models.ForeignKey(
        to='core.DataFile',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+'
    )
    data_path = models.CharField(
        verbose_name=_('data path'),
        max_length=1000,
        blank=True,
        editable=False,
        help_text=_("Path to remote file (relative to data source root)")
    )
    auto_sync_enabled = models.BooleanField(
        verbose_name=_('auto sync enabled'),
        default=False,
        help_text=_("Enable automatic synchronization of data when the data file is updated")
    )
    data_synced = models.DateTimeField(
        verbose_name=_('date synced'),
        blank=True,
        null=True,
        editable=False
    )

    class Meta:
        abstract = True

    @property
    def is_synced(self):
        return self.data_file and self.data_synced >= self.data_file.last_updated

    def clean(self):

        if self.data_file:
            self.data_source = self.data_file.source
            self.data_path = self.data_file.path
            self.sync()
        else:
            self.data_source = None
            self.data_path = ''
            self.auto_sync_enabled = False
            self.data_synced = None

        super().clean()
    clean.alters_data = True

    def save(self, *args, **kwargs):
        from core.models import AutoSyncRecord

        ret = super().save(*args, **kwargs)

        # Create/delete AutoSyncRecord as needed
        content_type = ContentType.objects.get_for_model(self)
        if self.auto_sync_enabled:
            AutoSyncRecord.objects.get_or_create(
                datafile=self.data_file,
                object_type=content_type,
                object_id=self.pk
            )
        else:
            AutoSyncRecord.objects.filter(
                datafile=self.data_file,
                object_type=content_type,
                object_id=self.pk
            ).delete()

        return ret

    def delete(self, *args, **kwargs):
        from core.models import AutoSyncRecord

        # Delete AutoSyncRecord
        content_type = ContentType.objects.get_for_model(self)
        AutoSyncRecord.objects.filter(
            datafile=self.data_file,
            object_type=content_type,
            object_id=self.pk
        ).delete()

        return super().delete(*args, **kwargs)

    def resolve_data_file(self):
        """
        Determine the designated DataFile object identified by its parent DataSource and its path. Returns None if
        either attribute is unset, or if no matching DataFile is found.
        """
        from core.models import DataFile

        if self.data_source and self.data_path:
            try:
                return DataFile.objects.get(source=self.data_source, path=self.data_path)
            except DataFile.DoesNotExist:
                pass

    def sync(self, save=False):
        """
        Synchronize the object from it's assigned DataFile (if any). This wraps sync_data() and updates
        the synced_data timestamp.

        :param save: If true, save() will be called after data has been synchronized
        """
        self.sync_data()
        self.data_synced = timezone.now()
        if save:
            self.save()
    sync.alters_data = True

    def sync_data(self):
        """
        Inheriting models must override this method with specific logic to copy data from the assigned DataFile
        to the local instance. This method should *NOT* call save() on the instance.
        """
        raise NotImplementedError(f"{self.__class__} must implement a sync_data() method.")


#
# Feature registration
#

FEATURES_MAP = {
    'bookmarks': BookmarksMixin,
    'change_logging': ChangeLoggingMixin,
    'cloning': CloningMixin,
    'contacts': ContactsMixin,
    'custom_fields': CustomFieldsMixin,
    'custom_links': CustomLinksMixin,
    'custom_validation': CustomValidationMixin,
    'export_templates': ExportTemplatesMixin,
    'image_attachments': ImageAttachmentsMixin,
    'jobs': JobsMixin,
    'journaling': JournalingMixin,
    'synced_data': SyncedDataMixin,
    'tags': TagsMixin,
    'event_rules': EventRulesMixin,
}

registry['model_features'].update({
    feature: defaultdict(set) for feature in FEATURES_MAP.keys()
})


def register_models(*models):
    """
    Register one or more models in NetBox. This entails:

     - Determining whether the model is considered "public" (available for reference by other models)
     - Registering which features the model supports (e.g. bookmarks, custom fields, etc.)
     - Registering any feature-specific views for the model (e.g. ObjectJournalView instances)

    register_model() should be called for each relevant model under the ready() of an app's AppConfig class.
    """
    for model in models:
        app_label, model_name = model._meta.label_lower.split('.')

        # Register public models
        if not getattr(model, '_netbox_private', False):
            registry['models'][app_label].add(model_name)

        # Record each applicable feature for the model in the registry
        features = {
            feature for feature, cls in FEATURES_MAP.items() if issubclass(model, cls)
        }
        for feature in features:
            try:
                registry['model_features'][feature][app_label].add(model_name)
            except KeyError:
                raise KeyError(
                    f"{feature} is not a valid model feature! Valid keys are: {registry['model_features'].keys()}"
                )

        # Register applicable feature views for the model
        if issubclass(model, JournalingMixin):
            register_model_view(model, 'journal', kwargs={'model': model})(
                'netbox.views.generic.ObjectJournalView'
            )
        if issubclass(model, ChangeLoggingMixin):
            register_model_view(model, 'changelog', kwargs={'model': model})(
                'netbox.views.generic.ObjectChangeLogView'
            )
        if issubclass(model, JobsMixin):
            register_model_view(model, 'jobs', kwargs={'model': model})(
                'netbox.views.generic.ObjectJobsView'
            )
        if issubclass(model, SyncedDataMixin):
            register_model_view(model, 'sync', kwargs={'model': model})(
                'netbox.views.generic.ObjectSyncDataView'
            )
