from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from extras.choices import CustomFieldFilterLogicChoices, CustomFieldTypeChoices
from extras.forms.customfields import CustomFieldsMixin
from extras.models import CustomField, Tag
from utilities.forms import BootstrapMixin, BulkEditBaseForm, CSVModelForm
from utilities.forms.fields import DynamicModelMultipleChoiceField

__all__ = (
    'NetBoxModelForm',
    'NetBoxModelCSVForm',
    'NetBoxModelBulkEditForm',
    'NetBoxModelFilterSetForm',
)


class NetBoxModelForm(BootstrapMixin, CustomFieldsMixin, forms.ModelForm):
    """
    Base form for creating & editing NetBox models. Adds support for custom fields.
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
        for cf_name, customfield in self.custom_fields.items():
            key = cf_name[3:]  # Strip "cf_" from field name
            value = self.cleaned_data.get(cf_name)

            # Convert "empty" values to null
            if value in self.fields[cf_name].empty_values:
                self.instance.custom_field_data[key] = None
            else:
                self.instance.custom_field_data[key] = customfield.serialize(value)

        return super().clean()


class NetBoxModelCSVForm(CSVModelForm, NetBoxModelForm):
    """
    Base form for creating a NetBox objects from CSV data. Used for bulk importing.
    """
    def _get_form_field(self, customfield):
        return customfield.to_form_field(for_csv_import=True)


class NetBoxModelBulkEditForm(BootstrapMixin, CustomFieldsMixin, BulkEditBaseForm):
    """
    Base form for modifying multiple NetBox objects (of the same type) in bulk via the UI. Adds support for custom
    fields and adding/removing tags.
    """
    add_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    remove_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

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
            self.custom_fields[customfield.name] = customfield


class NetBoxModelFilterSetForm(BootstrapMixin, CustomFieldsMixin, forms.Form):
    """
    Base form for FilerSet forms. These are used to filter object lists in the NetBox UI.

    The corresponding FilterSet *must* provide a `q` filter.
    """
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
