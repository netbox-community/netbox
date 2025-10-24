from django import forms
from django.utils.translation import gettext_lazy as _

from extras.choices import *
from extras.models import CustomField, Tag
from users.models import Owner
from utilities.forms import CSVModelForm
from utilities.forms.fields import CSVModelMultipleChoiceField, CSVModelChoiceField, SlugField
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
        return CustomField.objects.filter(
            object_types=content_type,
            ui_editable=CustomFieldUIEditableChoices.YES
        )

    def _get_form_field(self, customfield):
        return customfield.to_form_field(for_csv_import=True)


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
