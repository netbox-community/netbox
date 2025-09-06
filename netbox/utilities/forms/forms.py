import re

from django import forms
from django.utils.translation import gettext as _

from netbox.models.features import ChangeLoggingMixin
from utilities.forms.mixins import BackgroundJobMixin

__all__ = (
    'BulkDeleteForm',
    'BulkEditForm',
    'BulkRenameForm',
    'ConfirmationForm',
    'CSVModelForm',
    'DeleteForm',
    'FilterForm',
    'TableConfigForm',
)


class ConfirmationForm(forms.Form):
    """
    A generic confirmation form. The form is not valid unless the `confirm` field is checked.
    """
    return_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    confirm = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput(),
        initial=True
    )


class DeleteForm(ConfirmationForm):
    """
    Confirm the deletion of an object, optionally providing a changelog message.
    """
    changelog_message = forms.CharField(
        required=False,
        max_length=200
    )

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide the changelog_message filed if the model doesn't support change logging
        if instance is None or not issubclass(instance._meta.model, ChangeLoggingMixin):
            self.fields.pop('changelog_message')


class BulkEditForm(BackgroundJobMixin, forms.Form):
    """
    Provides bulk edit support for objects.

    Attributes:
        nullable_fields: A list of field names indicating which fields support being set to null/empty
    """
    nullable_fields = ()


class BulkRenameForm(forms.Form):
    """
    An extendable form to be used for renaming objects in bulk.
    """
    find = forms.CharField(
        strip=False
    )
    replace = forms.CharField(
        strip=False,
        required=False
    )
    use_regex = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Use regular expressions')
    )

    def clean(self):
        super().clean()

        # Validate regular expression in "find" field
        if self.cleaned_data['use_regex']:
            try:
                re.compile(self.cleaned_data['find'])
            except re.error:
                raise forms.ValidationError({
                    'find': "Invalid regular expression"
                })


class BulkDeleteForm(BackgroundJobMixin, ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.MultipleHiddenInput
    )
    changelog_message = forms.CharField(
        required=False,
        max_length=200
    )

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pk'].queryset = model.objects.all()

        # Hide the changelog_message filed if the model doesn't support change logging
        if model is None or not issubclass(model, ChangeLoggingMixin):
            self.fields.pop('changelog_message')


class CSVModelForm(forms.ModelForm):
    """
    ModelForm used for the import of objects in CSV format.
    """
    id = forms.IntegerField(
        label=_('ID'),
        required=False,
        help_text=_('Numeric ID of an existing object to update (if not creating a new object)')
    )

    def __init__(self, *args, headers=None, **kwargs):
        self.headers = headers or {}
        super().__init__(*args, **kwargs)

        # Modify the model form to accommodate any customized to_field_name properties
        for field, to_field in self.headers.items():
            if to_field is not None:
                self.fields[field].to_field_name = to_field

    def clean(self):
        # Flag any invalid CSV headers
        for header in self.headers:
            if header not in self.fields:
                raise forms.ValidationError(
                    _("Unrecognized header: {name}").format(name=header)
                )

        return super().clean()


class FilterForm(forms.Form):
    """
    Base Form class for FilterSet forms.
    """
    q = forms.CharField(
        required=False,
        label=_('Search')
    )


class TableConfigForm(forms.Form):
    """
    Form for configuring user's table preferences.
    """
    available_columns = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.SelectMultiple(
            attrs={'size': 10, 'class': 'form-select'}
        ),
        label=_('Available Columns')
    )
    columns = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.SelectMultiple(
            attrs={'size': 10, 'class': 'form-select select-all'}
        ),
        label=_('Selected Columns')
    )

    def __init__(self, table, *args, **kwargs):
        self.table = table

        super().__init__(*args, **kwargs)

        # Initialize columns field based on table attributes
        if table:
            self.fields['available_columns'].choices = table.available_columns
            self.fields['columns'].choices = table.selected_columns

    @property
    def table_name(self):
        return self.table.__class__.__name__
