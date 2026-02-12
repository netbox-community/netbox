from django import forms

from netbox.choices import ColorChoices

from ..utils import add_blank_choice

__all__ = (
    'BulkEditNullBooleanSelect',
    'ClearableSelect',
    'ColorSelect',
    'HTMXSelect',
    'SelectWithPK',
    'SplitMultiSelectWidget',
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


class ClearableSelect(forms.Select):
    """
    A Select widget that will be automatically cleared when one or more required fields are cleared.

    Args:
        requires_fields: A list of field names that this field depends on. When any of these fields
                        are cleared, this field will also be cleared automatically via JavaScript.
    """

    def __init__(self, *args, requires_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        if requires_fields:
            self.attrs['data-requires-fields'] = ','.join(requires_fields)


class ColorSelect(forms.Select):
    """
    Extends the built-in Select widget to colorize each <option>.
    """
    option_template_name = 'widgets/colorselect_option.html'

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = add_blank_choice(ColorChoices)
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'color-select'


class HTMXSelect(forms.Select):
    """
    Selection widget that will re-generate the HTML form upon the selection of a new option.
    """
    def __init__(self, method='get', hx_url='.', hx_target_id='form_fields', attrs=None, **kwargs):
        method = method.lower()
        if method not in ('delete', 'get', 'patch', 'post', 'put'):
            raise ValueError(f"Unsupported HTTP method: {method}")
        _attrs = {
            f'hx-{method}': hx_url,
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


class SelectMultipleBase(forms.SelectMultiple):
    """
    Base class for select widgets that filter choices based on selected values.
    Subclasses should set `include_selected` to control filtering behavior.
    """
    include_selected = False

    def optgroups(self, name, value, attrs=None):
        filtered_choices = []
        include_selected = self.include_selected

        for choice in self.choices:
            if isinstance(choice[1], (list, tuple)):  # optgroup
                group_label, group_choices = choice
                filtered_group = [
                    c for c in group_choices if (str(c[0]) in value) == include_selected
                ]

                if filtered_group:  # Only include optgroup if it has choices left
                    filtered_choices.append((group_label, filtered_group))
            else:  # option, e.g. flat choice
                if (str(choice[0]) in value) == include_selected:
                    filtered_choices.append(choice)

        self.choices = filtered_choices
        value = []  # Clear selected choices
        return super().optgroups(name, value, attrs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option['attrs']['title'] = label  # Add title attribute to show full text on hover
        return option


class AvailableOptions(SelectMultipleBase):
    """
    Renders a <select multiple=true> including only choices that have been selected. (For unbound fields, this list
    will be empty.) Employed by SplitMultiSelectWidget.
    """

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # This widget should never require a selection
        context['widget']['attrs']['required'] = False

        return context


class SelectedOptions(SelectMultipleBase):
    """
    Renders a <select multiple=true> including only choices that have _not_ been selected. (For unbound fields, this
    will include _all_ choices.) Employed by SplitMultiSelectWidget.
    """
    include_selected = True


class SplitMultiSelectWidget(forms.MultiWidget):
    """
    Renders two <select multiple=true> widgets side-by-side: one listing available choices, the other listing selected
    choices. Options are selected by moving them from the left column to the right.

    Args:
        ordering: If true, the selected choices list will include controls to reorder items within the list. This should
                  be enabled only if the order of the selected choices is significant.
    """
    template_name = 'widgets/splitmultiselect.html'

    def __init__(self, choices, attrs=None, ordering=False):
        widgets = [
            AvailableOptions(
                attrs={'size': 8},
                choices=choices
            ),
            SelectedOptions(
                attrs={'size': 8, 'class': 'select-all'},
                choices=choices
            ),
        ]

        super().__init__(widgets, attrs)

        self.ordering = ordering

    def get_context(self, name, value, attrs):
        # Replicate value for each multi-select widget
        # Django bug? See django/forms/widgets.py L985
        value = [value, value]

        # Include ordering boolean in widget context
        context = super().get_context(name, value, attrs)
        context['widget']['ordering'] = self.ordering
        return context

    def value_from_datadict(self, data, files, name):
        # Return only the choices from the SelectedOptions widget
        return super().value_from_datadict(data, files, name)[1]
