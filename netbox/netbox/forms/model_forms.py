import json

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import ManyToManyRel

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
        Handles both forward and reverse M2M relationships, and supports both simple (single field)
        and add/remove (dual field) modes.
        """
        self.instance._m2m_values = {}

        # Collect names to process: local M2M fields (includes TaggableManager from django-taggit)
        # plus reverse M2M relations (ManyToManyRel).
        names = [field.name for field in self.instance._meta.local_many_to_many]
        names += [
            field.get_accessor_name()
            for field in self.instance._meta.get_fields()
            if isinstance(field, ManyToManyRel)
        ]

        for name in names:
            if name in self.cleaned_data:
                # Simple mode: single multi-select field
                self.instance._m2m_values[name] = list(self.cleaned_data[name])
            elif f'add_{name}' in self.cleaned_data or f'remove_{name}' in self.cleaned_data:
                # Add/remove mode: compute the effective set
                current = set(getattr(self.instance, name).values_list('pk', flat=True)) \
                    if self.instance.pk else set()
                add_values = set(
                    v.pk for v in self.cleaned_data.get(f'add_{name}', [])
                )
                remove_values = set(
                    v.pk for v in self.cleaned_data.get(f'remove_{name}', [])
                )
                self.instance._m2m_values[name] = list((current | add_values) - remove_values)

        return super()._post_clean()

    def _save_m2m(self):
        """
        Save many-to-many field values that were computed in _post_clean(). This handles M2M fields
        not included in Meta.fields (e.g. those managed via M2MAddRemoveFields).
        """
        super()._save_m2m()
        meta_fields = self._meta.fields
        for field_name, values in self.instance._m2m_values.items():
            if not meta_fields or field_name not in meta_fields:
                getattr(self.instance, field_name).set(values)


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
