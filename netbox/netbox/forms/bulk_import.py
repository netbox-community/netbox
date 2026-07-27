from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from extras.choices import *
from extras.models import CustomField, Tag
from users.models import Owner
from utilities.forms import CSVModelForm
from utilities.forms.fields import CSVModelChoiceField, CSVModelMultipleChoiceField, SlugField

from .model_forms import NetBoxModelForm

__all__ = (
    'NestedGroupModelImportForm',
    'NetBoxModelImportForm',
    'OrganizationalModelImportForm',
    'OwnerCSVMixin',
    'PrimaryModelImportForm'
)


class NetBoxModelImportForm(CSVModelForm, NetBoxModelForm):
    """
    Base form for creating NetBox objects from CSV data. Used for bulk importing.
    """
    tags = CSVModelMultipleChoiceField(
        label=_('Tags'),
        queryset=Tag.objects.all(),
        required=False,
        to_field_name='slug',
        help_text=_('Tag slugs separated by commas, encased with double quotes (e.g. "tag1,tag2,tag3")')
    )

    def _get_custom_fields(self, content_type):
        # Return only custom fields that are editable in the UI
        return [
            cf for cf in CustomField.objects.get_for_model(content_type.model_class())
            if cf.ui_editable == CustomFieldUIEditableChoices.YES
        ]

    def _get_form_field(self, customfield):
        return customfield.to_form_field(for_csv_import=True)

    def clean(self):
        """
        Cleans data in a form, ensuring proper handling of model fields with `null=True`.
        Overrides the `clean` method from the parent form to process and sanitize cleaned
        data for defined fields in the associated model.
        """
        super().clean()
        cleaned = self.cleaned_data

        model = getattr(self._meta, "model", None)
        if not model:
            return cleaned

        for f in model._meta.get_fields():
            # Only forward, DB-backed fields (skip M2M & reverse relations)
            if not isinstance(f, models.Field) or not f.concrete or f.many_to_many:
                continue

            if getattr(f, "null", False):
                name = f.name
                if name not in cleaned:
                    continue
                val = cleaned[name]
                # Only coerce empty strings; leave other types alone
                if isinstance(val, str) and val.strip() == "":
                    cleaned[name] = None

        return cleaned

    def _update_errors(self, errors):
        """
        Override to handle ValidationErrors from model.full_clean() that reference
        fields not present on this import form. Rather than crashing with a ValueError,
        remap those errors to non-field errors so bulk import surfaces a readable
        validation message instead of a 500.
        """
        if hasattr(errors, 'error_dict'):
            new_error_dict = {}
            for field, error_list in errors.error_dict.items():
                if field == NON_FIELD_ERRORS or field not in self.fields:
                    new_error_dict.setdefault(NON_FIELD_ERRORS, []).extend(error_list)
                else:
                    new_error_dict[field] = error_list
            errors = ValidationError(new_error_dict)
        super()._update_errors(errors)


class OwnerCSVMixin(forms.Form):
    owner = CSVModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_("Name of the object's owner")
    )


class PrimaryModelImportForm(OwnerCSVMixin, NetBoxModelImportForm):
    """
    Bulk import form for models which inherit from PrimaryModel.
    """
    pass


class OrganizationalModelImportForm(OwnerCSVMixin, NetBoxModelImportForm):
    """
    Bulk import form for models which inherit from OrganizationalModel.
    """
    slug = SlugField()


class NestedGroupModelImportForm(OwnerCSVMixin, NetBoxModelImportForm):
    """
    Bulk import form for models which inherit from NestedGroupModel.
    """
    slug = SlugField()
