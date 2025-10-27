import time
from decimal import Decimal

from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from utilities.forms.fields import ColorField, TagFilterField
from utilities.forms.widgets.modifiers import MODIFIER_EMPTY_FALSE, MODIFIER_EMPTY_TRUE

__all__ = (
    'BackgroundJobMixin',
    'CheckLastUpdatedMixin',
    'DistanceValidationMixin',
    'FilterModifierMixin',
)


class BackgroundJobMixin(forms.Form):
    background_job = forms.BooleanField(
        label=_('Background job'),
        help_text=_("Execute this task via a background job"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Declare background_job a meta field
        if hasattr(self, 'meta_fields'):
            self.meta_fields.append('background_job')
        else:
            self.meta_fields = ['background_job']


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


class DistanceValidationMixin(forms.Form):
    distance = forms.DecimalField(
        required=False,
        validators=[
            MinValueValidator(Decimal(0)),
            MaxValueValidator(Decimal(100000)),
        ]
    )


class FilterModifierMixin:
    """
    Mixin that enhances filter form fields with lookup modifier dropdowns.

    Automatically detects fields that could benefit from multiple lookup options
    and wraps their widgets with FilterModifierWidget.
    """

    # Mapping of form field types to their supported lookups
    FORM_FIELD_LOOKUPS = {
        forms.CharField: [
            ('exact', _('Is')),
            ('n', _('Is Not')),
            ('ic', _('Contains')),
            ('isw', _('Starts With')),
            ('iew', _('Ends With')),
            ('ie', _('Equals (case-insensitive)')),
            ('regex', _('Matches Pattern')),
            ('iregex', _('Matches Pattern (case-insensitive)')),
            (MODIFIER_EMPTY_TRUE, _('Is Empty')),
            (MODIFIER_EMPTY_FALSE, _('Is Not Empty')),
        ],
        forms.IntegerField: [
            ('exact', _('Is')),
            ('n', _('Is Not')),
            ('gt', _('Greater Than (>)')),
            ('gte', _('At Least (≥)')),
            ('lt', _('Less Than (<)')),
            ('lte', _('At Most (≤)')),
            (MODIFIER_EMPTY_TRUE, _('Is Empty')),
            (MODIFIER_EMPTY_FALSE, _('Is Not Empty')),
        ],
        forms.DecimalField: [
            ('exact', _('Is')),
            ('n', _('Is Not')),
            ('gt', _('Greater Than (>)')),
            ('gte', _('At Least (≥)')),
            ('lt', _('Less Than (<)')),
            ('lte', _('At Most (≤)')),
            (MODIFIER_EMPTY_TRUE, _('Is Empty')),
            (MODIFIER_EMPTY_FALSE, _('Is Not Empty')),
        ],
        forms.DateField: [
            ('exact', _('Is')),
            ('n', _('Is Not')),
            ('gt', _('After')),
            ('gte', _('On or After')),
            ('lt', _('Before')),
            ('lte', _('On or Before')),
            (MODIFIER_EMPTY_TRUE, _('Is Empty')),
            (MODIFIER_EMPTY_FALSE, _('Is Not Empty')),
        ],
        forms.ModelChoiceField: [
            ('exact', _('Is')),
            ('n', _('Is Not')),
            (MODIFIER_EMPTY_TRUE, _('Is Empty')),
            (MODIFIER_EMPTY_FALSE, _('Is Not Empty')),
        ],
        ColorField: [
            ('exact', _('Is')),
            ('n', _('Is Not')),
            (MODIFIER_EMPTY_TRUE, _('Is Empty')),
            (MODIFIER_EMPTY_FALSE, _('Is Not Empty')),
        ],
        TagFilterField: [
            ('exact', _('Has These Tags')),
            ('n', _('Does Not Have These Tags')),
            (MODIFIER_EMPTY_TRUE, _('Is Empty')),
            (MODIFIER_EMPTY_FALSE, _('Is Not Empty')),
        ],
        forms.MultipleChoiceField: [
            ('exact', _('Is')),
            ('n', _('Is Not')),
            (MODIFIER_EMPTY_TRUE, _('Is Empty')),
            (MODIFIER_EMPTY_FALSE, _('Is Not Empty')),
        ],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enhance_fields_with_modifiers()

    def _enhance_fields_with_modifiers(self):
        """Wrap compatible field widgets with FilterModifierWidget."""
        from utilities.forms.widgets import FilterModifierWidget
        from utilities.forms.filterset_mappings import FILTERSET_MAPPINGS

        # Get the corresponding FilterSet if registered
        filterset_class = FILTERSET_MAPPINGS.get(self.__class__)
        filterset = filterset_class() if filterset_class else None

        for field_name, field in self.fields.items():
            if self._should_skip_field(field_name, field):
                continue

            lookups = self._get_lookup_choices(field, field_name)

            # Verify lookups against FilterSet if available
            if filterset:
                lookups = self._verify_lookups_with_filterset(field_name, lookups, filterset)

            if len(lookups) > 1:
                field.widget = FilterModifierWidget(
                    original_widget=field.widget,
                    lookups=lookups
                )

    def _should_skip_field(self, field_name, field):
        """Determine if a field should be skipped for enhancement."""
        # Skip the global search field
        if field_name == 'q':
            return True

        # Skip boolean fields (no benefit from modifiers)
        if isinstance(field, (forms.BooleanField, forms.NullBooleanField)):
            return True

        # MultipleChoiceField and TagFilterField are now supported
        # (no longer skipped)

        # Skip API widget fields
        if self._is_api_widget_field(field):
            return True

        return False

    def _get_lookup_choices(self, field, field_name=None):
        """Determine the available lookup choices for a given field."""
        # Walk up the MRO to find a known field type
        for field_class in field.__class__.__mro__:
            if field_class in self.FORM_FIELD_LOOKUPS:
                return self.FORM_FIELD_LOOKUPS[field_class]

        # Unknown field type - return single exact option (no enhancement)
        return [('exact', _('Is'))]

    def _verify_lookups_with_filterset(self, field_name, lookups, filterset):
        """Verify which lookups are actually supported by the FilterSet."""
        verified_lookups = []

        for lookup_code, lookup_label in lookups:
            # Handle special empty_true/false codes that map to __empty
            if lookup_code in (MODIFIER_EMPTY_TRUE, MODIFIER_EMPTY_FALSE):
                filter_key = f'{field_name}__empty'
            else:
                filter_key = f'{field_name}__{lookup_code}' if lookup_code != 'exact' else field_name

            # Check if this filter exists in the FilterSet
            if filter_key in filterset.filters:
                verified_lookups.append((lookup_code, lookup_label))

        return verified_lookups

    def _is_api_widget_field(self, field):
        """Check if a field uses an API-based widget."""
        # Check field class name
        if 'Dynamic' in field.__class__.__name__:
            return True

        # Check widget attributes for API-related data
        if hasattr(field.widget, 'attrs') and field.widget.attrs:
            api_attrs = ['data-url', 'data-api-url', 'data-static-params']
            if any(attr in field.widget.attrs for attr in api_attrs):
                return True

        return False
