import json

from django import forms
from django.contrib.contenttypes.models import ContentType

from extras.choices import *
from utilities.forms.fields import CommentField, SlugField
from utilities.forms.mixins import CheckLastUpdatedMixin

from .mixins import ChangelogMessageMixin, CustomFieldsMixin, OwnerMixin, TagsMixin

__all__ = (
    'NestedGroupModelForm',
    'NetBoxModelForm',
    'OrganizationalModelForm',
    'PrimaryModelForm',
)


class NetBoxModelForm(
    ChangelogMessageMixin,
    CheckLastUpdatedMixin,
    CustomFieldsMixin,
    TagsMixin,
    forms.ModelForm
):
    """
    Base form for creating & editing NetBox models. Extends Django's ModelForm to add support for custom fields.

    Attributes:
        fieldsets: An iterable of FieldSets which define a name and set of fields to display per section of
            the rendered form (optional). If not defined, the all fields will be rendered as a single section.
    """
    fieldsets = ()

    def _get_content_type(self):
        return ContentType.objects.get_for_model(self._meta.model)

    def _get_form_field(self, customfield):
        if self.instance.pk:
            form_field = customfield.to_form_field(set_initial=False)
            initial = self.instance.custom_field_data.get(customfield.name)
            if customfield.type == CustomFieldTypeChoices.TYPE_JSON:
                form_field.initial = json.dumps(initial)
            else:
                form_field.initial = initial
            return form_field

        return customfield.to_form_field()

    def clean(self):

        # Save custom field data on instance
        for cf_name, customfield in self.custom_fields.items():
            if cf_name not in self.fields:
                # Custom fields may be absent when performing bulk updates via import
                continue
            key = cf_name[3:]  # Strip "cf_" from field name
            value = self.cleaned_data.get(cf_name)

            # Convert "empty" values to null
            if value in self.fields[cf_name].empty_values:
                self.instance.custom_field_data[key] = None
            else:
                if customfield.type == CustomFieldTypeChoices.TYPE_JSON and type(value) is str:
                    value = json.loads(value)
                self.instance.custom_field_data[key] = customfield.serialize(value)

        return super().clean()

    def _post_clean(self):
        """
        Override BaseModelForm's _post_clean() to store many-to-many field values on the model instance.
        """
        self.instance._m2m_values = {}
        for field in self.instance._meta.local_many_to_many:
            if field.name in self.cleaned_data:
                self.instance._m2m_values[field.name] = list(self.cleaned_data[field.name])

        return super()._post_clean()


class PrimaryModelForm(OwnerMixin, NetBoxModelForm):
    """
    Form for models which inherit from PrimaryModel.
    """
    comments = CommentField()


class OrganizationalModelForm(OwnerMixin, NetBoxModelForm):
    """
    Form for models which inherit from OrganizationalModel.
    """
    slug = SlugField()
    comments = CommentField()


class NestedGroupModelForm(OwnerMixin, NetBoxModelForm):
    """
    Form for models which inherit from NestedGroupModel.
    """
    slug = SlugField()
    comments = CommentField()
