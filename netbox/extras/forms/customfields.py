from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from extras.choices import *
from extras.models import *
from utilities.forms import BootstrapMixin, BulkEditBaseForm, CSVModelForm

__all__ = (
    'CustomFieldModelCSVForm',
    'CustomFieldModelBulkEditForm',
    'CustomFieldModelFilterForm',
    'CustomFieldModelForm',
    'CustomFieldsMixin',
)


class CustomFieldsMixin:
    """
    Extend a Form to include custom field support.
    """
    def __init__(self, *args, **kwargs):
        self.custom_fields = []

        super().__init__(*args, **kwargs)

        self._append_customfield_fields()

    def _get_content_type(self):
        """
        Return the ContentType of the form's model.
        """
        if not hasattr(self, 'model'):
            raise NotImplementedError(f"{self.__class__.__name__} must specify a model class.")
        return ContentType.objects.get_for_model(self.model)

    def _get_custom_fields(self, content_type):
        return CustomField.objects.filter(content_types=content_type)

    def _get_form_field(self, customfield):
        return customfield.to_form_field()

    def _append_customfield_fields(self):
        """
        Append form fields for all CustomFields assigned to this object type.
        """
        for customfield in self._get_custom_fields(self._get_content_type()):
            field_name = f'cf_{customfield.name}'
            self.fields[field_name] = self._get_form_field(customfield)

            # Annotate the field in the list of CustomField form fields
            self.custom_fields.append(field_name)


class CustomFieldModelForm(BootstrapMixin, CustomFieldsMixin, forms.ModelForm):
    """
    Extend ModelForm to include custom field support.
    """
    def _get_content_type(self):
        return ContentType.objects.get_for_model(self._meta.model)

    def _get_form_field(self, customfield):
        if self.instance.pk:
            form_field = customfield.to_form_field(set_initial=False)
            form_field.initial = self.instance.custom_field_data.get(customfield.name, None)
            return form_field

        return customfield.to_form_field()

    def clean(self):

        # Save custom field data on instance
        for cf_name in self.custom_fields:
            key = cf_name[3:]  # Strip "cf_" from field name
            value = self.cleaned_data.get(cf_name)
            empty_values = self.fields[cf_name].empty_values
            # Convert "empty" values to null
            self.instance.custom_field_data[key] = value if value not in empty_values else None

        return super().clean()


class CustomFieldModelCSVForm(CSVModelForm, CustomFieldModelForm):

    def _get_form_field(self, customfield):
        return customfield.to_form_field(for_csv_import=True)


class CustomFieldModelBulkEditForm(BootstrapMixin, CustomFieldsMixin, BulkEditBaseForm):

    def _get_form_field(self, customfield):
        return customfield.to_form_field(set_initial=False, enforce_required=False)

    def _append_customfield_fields(self):
        """
        Append form fields for all CustomFields assigned to this object type.
        """
        for customfield in self._get_custom_fields(self._get_content_type()):
            # Annotate non-required custom fields as nullable
            if not customfield.required:
                self.nullable_fields.append(customfield.name)

            self.fields[customfield.name] = self._get_form_field(customfield)

            # Annotate the field in the list of CustomField form fields
            self.custom_fields.append(customfield.name)


class CustomFieldModelFilterForm(BootstrapMixin, CustomFieldsMixin, forms.Form):
    q = forms.CharField(
        required=False,
        label='Search'
    )

    def _get_custom_fields(self, content_type):
        return CustomField.objects.filter(content_types=content_type).exclude(
            Q(filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED) |
            Q(type=CustomFieldTypeChoices.TYPE_JSON)
        )

    def _get_form_field(self, customfield):
        return customfield.to_form_field(set_initial=False, enforce_required=False)
