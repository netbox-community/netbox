import time

from django import forms
from django.utils.translation import gettext_lazy as _

from .widgets import APISelect, APISelectMultiple, ClearableFileInput

__all__ = (
    'BootstrapMixin',
    'CheckLastUpdatedMixin',
)


class BootstrapMixin:
    """
    Add the base Bootstrap CSS classes to form elements.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exempt_widgets = [
            forms.FileInput,
            forms.RadioSelect,
            APISelect,
            APISelectMultiple,
            ClearableFileInput,
        ]

        for field_name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')

            if field.widget.__class__ in exempt_widgets:
                continue

            # elif isinstance(field.widget, forms.CheckboxInput):
            #     field.widget.attrs['class'] = f'{css} form-check-input'
            #
            # elif isinstance(field.widget, forms.SelectMultiple) and 'size' in field.widget.attrs:
            #     # Use native Bootstrap class for multi-line <select> widgets
            #     field.widget.attrs['class'] = f'{css} form-select form-select-sm'
            #
            # elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
            #     field.widget.attrs['class'] = f'{css} netbox-static-select'
            #
            # else:
            #     field.widget.attrs['class'] = f'{css} form-control'

            # if field.required and not isinstance(field.widget, forms.FileInput):
            #     field.widget.attrs['required'] = 'required'

            # if 'placeholder' not in field.widget.attrs and field.label is not None:
            #     field.widget.attrs['placeholder'] = field.label

    def is_valid(self):
        is_valid = super().is_valid()

        # Apply is-invalid CSS class to fields with errors
        if not is_valid:
            for field_name in self.errors:
                # Ignore e.g. __all__
                if field := self.fields.get(field_name):
                    css = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = f'{css} is-invalid'

        return is_valid


class CheckLastUpdatedMixin(forms.Form):
    """
    Checks whether the object being saved has been updated since the form was initialized. If so, validation fails.
    This prevents a user from inadvertently overwriting any changes made to the object between when the form was
    initialized and when it was submitted.

    This validation does not apply to newly created objects, or if the `_init_time` field is not present in the form
    data.
    """
    _init_time = forms.DecimalField(
        initial=time.time,
        required=False,
        widget=forms.HiddenInput()
    )

    def clean(self):
        super().clean()

        # Skip for absent or newly created instances
        if not self.instance or not self.instance.pk:
            return

        # Skip if a form init time has not been specified
        if not (form_init_time := self.cleaned_data.get('_init_time')):
            return

        # Skip if the object does not have a last_updated value
        if not (last_updated := getattr(self.instance, 'last_updated', None)):
            return

        # Check that the submitted initialization time is not earlier than the object's modification time
        if form_init_time < last_updated.timestamp():
            raise forms.ValidationError(_(
                "This object has been modified since the form was rendered. Please consult the object's change "
                "log for details."
            ))
