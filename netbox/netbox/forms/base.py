from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from extras.choices import CustomFieldFilterLogicChoices, CustomFieldTypeChoices
from extras.forms.customfields import CustomFieldsMixin
from extras.models import CustomField, Tag
from utilities.forms import BootstrapMixin, CSVModelForm
from utilities.forms.fields import DynamicModelMultipleChoiceField

__all__ = (
    'NetBoxModelForm',
    'NetBoxModelCSVForm',
    'NetBoxModelBulkEditForm',
    'NetBoxModelFilterSetForm',
)


class NetBoxModelForm(BootstrapMixin, CustomFieldsMixin, forms.ModelForm):
    """
    Base form for creating & editing NetBox models. Extends Django's ModelForm to add support for custom fields.

    Attributes:
        fieldsets: An iterable of two-tuples which define a heading and field set to display per section of
            the rendered form (optional). If not defined, the all fields will be rendered as a single section.
    """
    fieldsets = ()

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


class NetBoxModelBulkEditForm(BootstrapMixin, CustomFieldsMixin, forms.Form):
    """
    Base form for modifying multiple NetBox objects (of the same type) in bulk via the UI. Adds support for custom
    fields and adding/removing tags.

    Attributes:
        nullable_fields: A list of field names indicating which fields support being set to null/empty
    """
    nullable_fields = ()

    pk = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.MultipleHiddenInput
    )
    add_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    remove_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pk'].queryset = self.model.objects.all()

    def _get_form_field(self, customfield):
        return customfield.to_form_field(set_initial=False, enforce_required=False)

    def _append_customfield_fields(self):
        """
        Append form fields for all CustomFields assigned to this object type.
        """
        nullable_custom_fields = []
        for customfield in self._get_custom_fields(self._get_content_type()):
            field_name = f'cf_{customfield.name}'
            self.fields[field_name] = self._get_form_field(customfield)

            # Record non-required custom fields as nullable
            if not customfield.required:
                nullable_custom_fields.append(field_name)

            # Annotate the field in the list of CustomField form fields
            self.custom_fields[field_name] = customfield

        # Annotate nullable custom fields (if any) on the form instance
        if nullable_custom_fields:
            self.nullable_fields = (*self.nullable_fields, *nullable_custom_fields)


class NetBoxModelFilterSetForm(BootstrapMixin, CustomFieldsMixin, forms.Form):
    """
    Base form for FilerSet forms. These are used to filter object lists in the NetBox UI. Note that the
    corresponding FilterSet *must* provide a `q` filter.

    Attributes:
        model: The model class associated with the form
        fieldsets: An iterable of two-tuples which define a heading and field set to display per section of
            the rendered form (optional). If not defined, the all fields will be rendered as a single section.
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
