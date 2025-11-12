from django import forms
from django.utils.translation import gettext_lazy as _

__all__ = ('FilterModifierWidget',)

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

    def __init__(self, original_widget, lookups, attrs=None):
        """
        Args:
            original_widget: The widget being wrapped (e.g., TextInput, NumberInput)
            lookups: List of (lookup_code, label) tuples (e.g., [('exact', 'Is'), ('ic', 'Contains')])
            attrs: Additional widget attributes
        """
        self.original_widget = original_widget
        self.lookups = lookups
        super().__init__(attrs or getattr(original_widget, 'attrs', {}))

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
        # Get context from the original widget
        original_context = self.original_widget.get_context(name, value, attrs)

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
