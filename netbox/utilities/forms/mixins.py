from django import forms

from .widgets import APISelect, APISelectMultiple, ClearableFileInput

__all__ = (
    'BootstrapMixin',
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

            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = f'{css} form-check-input'

            elif isinstance(field.widget, forms.SelectMultiple):
                if 'size' not in field.widget.attrs:
                    field.widget.attrs['class'] = f'{css} netbox-static-select'

            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = f'{css} netbox-static-select'

            else:
                field.widget.attrs['class'] = f'{css} form-control'

            if field.required and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['required'] = 'required'

            if 'placeholder' not in field.widget.attrs and field.label is not None:
                field.widget.attrs['placeholder'] = field.label

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
