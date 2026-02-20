from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from utilities.forms.widgets.apiselect import APISelect, APISelectMultiple

__all__ = (
    'MODIFIER_EMPTY_FALSE',
    'MODIFIER_EMPTY_TRUE',
    'FilterModifierWidget',
)

# Modifier codes for empty/null checking
# These map to Django's 'empty' lookup: field__empty=true/false
MODIFIER_EMPTY_TRUE = 'empty_true'
MODIFIER_EMPTY_FALSE = 'empty_false'


class FilterModifierWidget(forms.Widget):
    """
    Wraps an existing widget to add a modifier dropdown for filter lookups.

    The original widget's semantics (name, id, attributes) are preserved.
    The modifier dropdown controls which lookup type is used (exact, contains, etc.).
    """
    template_name = 'widgets/filter_modifier.html'

    def __init__(self, widget, lookups, attrs=None):
        """
        Args:
            widget: The widget being wrapped (e.g., TextInput, NumberInput)
            lookups: List of (lookup_code, label) tuples (e.g., [('exact', 'Is'), ('ic', 'Contains')])
            attrs: Additional widget attributes
        """
        self.original_widget = widget
        self.lookups = lookups
        super().__init__(attrs or getattr(widget, 'attrs', {}))

    def value_from_datadict(self, data, files, name):
        """
        Extract value from data, checking all possible lookup variants.

        When form redisplays after validation error, the data may contain
        serial__ic=test but the field is named serial. This method searches
        all lookup variants to find the value.

        Returns:
            Just the value string for form validation. The modifier is reconstructed
            during rendering from the query parameter names.
        """
        # Special handling for empty - check if field__empty exists
        empty_param = f"{name}__empty"
        if empty_param in data:
            # Return the boolean value for empty lookup
            return data.get(empty_param)

        # Try exact field name first
        value = self.original_widget.value_from_datadict(data, files, name)

        # If not found, check all modifier variants
        # Note: SelectMultiple returns [] (empty list) when not found, not None
        if value is None or (isinstance(value, list) and len(value) == 0):
            for lookup, _ in self.lookups:
                if lookup == 'exact':
                    continue  # Already checked above
                # Skip empty_true/false variants - they're handled above
                if lookup in (MODIFIER_EMPTY_TRUE, MODIFIER_EMPTY_FALSE):
                    continue
                lookup_name = f"{name}__{lookup}"
                test_value = self.original_widget.value_from_datadict(data, files, lookup_name)
                if test_value is not None:
                    value = test_value
                    break

        # Return None if no value found (prevents field appearing in changed_data)
        # Handle all widget empty value representations
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        if isinstance(value, (list, tuple)) and len(value) == 0:
            return None

        # Return just the value for form validation
        return value

    def get_context(self, name, value, attrs):
        """
        Build context for template rendering.

        Includes both the original widget's context and our modifier-specific data.
        Note: value is now just a simple value (string/int/etc), not a dict.
        The JavaScript initializeFromURL() will set the correct modifier dropdown
        value based on URL parameters.
        """
        # Propagate any attrs set on the wrapper (like data-url from get_bound_field)
        # to the original widget before rendering
        self.original_widget.attrs.update(self.attrs)

        # For APISelect/APISelectMultiple widgets, temporarily clear choices to prevent queryset evaluation
        original_choices = None
        if isinstance(self.original_widget, (APISelect, APISelectMultiple)):
            original_choices = self.original_widget.choices

            # Only keep selected choices to preserve the current selection in HTML
            if value:
                values = value if isinstance(value, (list, tuple)) else [value]

                if hasattr(original_choices, 'queryset'):
                    # Extract valid PKs (exclude special null choice string)
                    pk_values = [v for v in values if v != settings.FILTERS_NULL_CHOICE_VALUE]

                    # Build a minimal choice list with just the selected values
                    choices = []
                    if pk_values:
                        selected_objects = original_choices.queryset.filter(pk__in=pk_values)
                        choices = [(obj.pk, str(obj)) for obj in selected_objects]

                    # Re-add the "None" option if it was selected via the null choice value
                    if settings.FILTERS_NULL_CHOICE_VALUE in values:
                        choices.append((settings.FILTERS_NULL_CHOICE_VALUE, settings.FILTERS_NULL_CHOICE_LABEL))

                    self.original_widget.choices = choices
                else:
                    self.original_widget.choices = [choice for choice in original_choices if choice[0] in values]
            else:
                # No selection - render empty select element
                self.original_widget.choices = []

        # Get context from the original widget
        original_context = self.original_widget.get_context(name, value, attrs)

        # Restore original choices if we modified them
        if original_choices is not None:
            self.original_widget.choices = original_choices

        # Build our wrapper context
        context = super().get_context(name, value, attrs)
        context['widget']['original_widget'] = original_context['widget']
        context['widget']['lookups'] = self.lookups
        context['widget']['field_name'] = name

        # Default to 'exact' - JavaScript will update based on URL params
        context['widget']['current_modifier'] = 'exact'
        context['widget']['current_value'] = value or ''

        # Translatable placeholder for empty lookups
        context['widget']['empty_placeholder'] = _('(automatically set)')

        return context
