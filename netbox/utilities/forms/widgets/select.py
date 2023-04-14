from django import forms

from utilities.choices import ColorChoices
from ..utils import add_blank_choice

__all__ = (
    'BulkEditNullBooleanSelect',
    'ColorSelect',
    'HTMXSelect',
    'SelectDurationWidget',
    'SelectSpeedWidget',
    'SelectWithPK',
)


class BulkEditNullBooleanSelect(forms.NullBooleanSelect):
    """
    A Select widget for NullBooleanFields
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override the built-in choice labels
        self.choices = (
            ('1', '---------'),
            ('2', 'Yes'),
            ('3', 'No'),
        )
        self.attrs['class'] = 'netbox-static-select'


class ColorSelect(forms.Select):
    """
    Extends the built-in Select widget to colorize each <option>.
    """
    option_template_name = 'widgets/colorselect_option.html'

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = add_blank_choice(ColorChoices)
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'netbox-color-select'


class HTMXSelect(forms.Select):
    """
    Selection widget that will re-generate the HTML form upon the selection of a new option.
    """
    def __init__(self, hx_url='.', hx_target_id='form_fields', attrs=None, **kwargs):
        _attrs = {
            'hx-get': hx_url,
            'hx-include': f'#{hx_target_id}',
            'hx-target': f'#{hx_target_id}',
        }
        if attrs:
            _attrs.update(attrs)

        super().__init__(attrs=_attrs, **kwargs)


class SelectWithPK(forms.Select):
    """
    Include the primary key of each option in the option label (e.g. "Router7 (4721)").
    """
    option_template_name = 'widgets/select_option_with_pk.html'


class SelectDurationWidget(forms.NumberInput):
    """
    Dropdown to select one of several common options for a time duration (in minutes).
    """
    template_name = 'widgets/select_duration.html'


class SelectSpeedWidget(forms.NumberInput):
    """
    Speed field with dropdown selections for convenience.
    """
    template_name = 'widgets/select_speed.html'
