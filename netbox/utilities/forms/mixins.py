import time
import warnings
from decimal import Decimal

from django import forms
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from netbox.registry import registry
from utilities.forms.fields import ColorField, GenericObjectChoiceField, QueryField, TagFilterField
from utilities.forms.widgets import FilterModifierWidget
from utilities.forms.widgets.modifiers import MODIFIER_EMPTY_FALSE, MODIFIER_EMPTY_TRUE

__all__ = (
    'FORM_FIELD_LOOKUPS',
    'BackgroundJobMixin',
    'CheckLastUpdatedMixin',
    'DistanceValidationMixin',
    'FilterModifierMixin',
    'GenericObjectFormMixin',
)


# Mapping of form field types to their supported lookups
FORM_FIELD_LOOKUPS = {
    QueryField: [],
    forms.BooleanField: [],
    forms.NullBooleanField: [],
    forms.CharField: [
        ('exact', _('is')),
        ('n', _('is not')),
        ('ic', _('contains')),
        ('isw', _('starts with')),
        ('iew', _('ends with')),
        ('ie', _('equals (case-insensitive)')),
        ('regex', _('matches pattern')),
        ('iregex', _('matches pattern (case-insensitive)')),
        (MODIFIER_EMPTY_TRUE, _('is empty')),
        (MODIFIER_EMPTY_FALSE, _('is not empty')),
    ],
    forms.IntegerField: [
        ('exact', _('is')),
        ('n', _('is not')),
        ('gt', _('greater than')),
        ('gte', _('at least')),
        ('lt', _('less than')),
        ('lte', _('at most')),
        (MODIFIER_EMPTY_TRUE, _('is empty')),
        (MODIFIER_EMPTY_FALSE, _('is not empty')),
    ],
    forms.DecimalField: [
        ('exact', _('is')),
        ('n', _('is not')),
        ('gt', _('greater than')),
        ('gte', _('at least')),
        ('lt', _('less than')),
        ('lte', _('at most')),
        (MODIFIER_EMPTY_TRUE, _('is empty')),
        (MODIFIER_EMPTY_FALSE, _('is not empty')),
    ],
    forms.DateField: [
        ('exact', _('is')),
        ('n', _('is not')),
        ('gt', _('after')),
        ('gte', _('on or after')),
        ('lt', _('before')),
        ('lte', _('on or before')),
        (MODIFIER_EMPTY_TRUE, _('is empty')),
        (MODIFIER_EMPTY_FALSE, _('is not empty')),
    ],
    forms.ModelChoiceField: [
        ('exact', _('is')),
        ('n', _('is not')),
        (MODIFIER_EMPTY_TRUE, _('is empty')),
        (MODIFIER_EMPTY_FALSE, _('is not empty')),
    ],
    ColorField: [
        ('exact', _('is')),
        ('n', _('is not')),
        (MODIFIER_EMPTY_TRUE, _('is empty')),
        (MODIFIER_EMPTY_FALSE, _('is not empty')),
    ],
    TagFilterField: [
        ('exact', _('has these tags')),
        ('n', _('does not have these tags')),
        (MODIFIER_EMPTY_TRUE, _('is empty')),
        (MODIFIER_EMPTY_FALSE, _('is not empty')),
    ],
    forms.ChoiceField: [
        ('exact', _('is')),
        ('n', _('is not')),
        (MODIFIER_EMPTY_TRUE, _('is empty')),
        (MODIFIER_EMPTY_FALSE, _('is not empty')),
    ],
    forms.MultipleChoiceField: [
        ('exact', _('is')),
        ('n', _('is not')),
        (MODIFIER_EMPTY_TRUE, _('is empty')),
        (MODIFIER_EMPTY_FALSE, _('is not empty')),
    ],
}


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


class GenericObjectFormMixin:
    """
    Initialize and assign any GenericObjectChoiceField fields on a form.

    Seeds each field's initial value from the model's GFK descriptor, configures the API-backed object
    selector for the current content type, and copies the cleaned object back to the instance before model
    validation runs. Keeps the common GFK form pattern out of individual model forms.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        for field_name, field in self._generic_object_fields():
            gfk_name = field.gfk_name or field_name
            # On an HTMX re-render the submitted subwidget values take precedence over the stored instance value.
            rerendered = any(f'{field_name}_{suffix}' in self.initial for suffix in ('content_type', 'object_id'))
            if instance is not None and not self.is_bound and field_name not in self.initial and not rerendered:
                if (initial := getattr(instance, gfk_name, None)) is not None:
                    self.initial[field_name] = initial
            # Prepare eagerly so forms can read field.selected_model in their own __init__ (e.g. PrefixForm).
            # prepare() is idempotent and re-runs at render via get_bound_field().
            field.prepare(self, field_name)

        if settings.DEBUG:
            self._warn_missing_htmx_fieldsets()

    def _generic_object_fields(self):
        for field_name, field in self.fields.items():
            if isinstance(field, GenericObjectChoiceField):
                yield field_name, field

    def _warn_missing_htmx_fieldsets(self):
        # Each GenericObjectChoiceField with an HTMX target needs a matching FieldSet(html_id=...) for the
        # partial swap to land; warn in development if a consumer forgot to declare one.
        fieldset_ids = {getattr(fs, 'html_id', None) for fs in getattr(self, 'fieldsets', [])}
        for field_name, field in self._generic_object_fields():
            if field.hx_target_id and field.hx_target_id not in fieldset_ids:
                warnings.warn(
                    f"{type(self).__name__} has a GenericObjectChoiceField '{field_name}' targeting "
                    f"#{field.hx_target_id} for HTMX swap but declares no FieldSet with "
                    f"html_id='{field.hx_target_id}'; the partial swap will fail silently.",
                    stacklevel=3,
                )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = self.cleaned_data

        instance = getattr(self, 'instance', None)
        if instance is not None:
            for field_name, field in self._generic_object_fields():
                if field_name in cleaned_data:
                    setattr(instance, field.gfk_name or field_name, cleaned_data[field_name])

        return cleaned_data


class FilterModifierMixin:
    """
    Mixin that enhances filter form fields with lookup modifier dropdowns.

    Automatically detects fields that could benefit from multiple lookup options
    and wraps their widgets with FilterModifierWidget.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enhance_fields_with_modifiers()

    def _enhance_fields_with_modifiers(self):
        """Wrap compatible field widgets with FilterModifierWidget."""

        model = getattr(self, 'model', None)
        if model is None and hasattr(self, '_meta'):
            model = getattr(self._meta, 'model', None)

        filterset_class = None
        if model:
            key = f'{model._meta.app_label}.{model._meta.model_name}'
            filterset_class = registry['filtersets'].get(key)

        filterset = filterset_class() if filterset_class else None

        for field_name, field in self.fields.items():
            lookups = self._get_lookup_choices(field)

            if filterset:
                lookups = self._verify_lookups_with_filterset(field_name, lookups, filterset)

                if len(lookups) > 1:
                    field.widget = FilterModifierWidget(
                        widget=field.widget,
                        lookups=lookups
                    )

    def _get_lookup_choices(self, field):
        """Determine the available lookup choices for a given field.

        Returns an empty list for fields that should not be enhanced.
        """
        for field_class in field.__class__.__mro__:
            if field_lookups := FORM_FIELD_LOOKUPS.get(field_class):
                return field_lookups

        return []

    def _verify_lookups_with_filterset(self, field_name, lookups, filterset):
        """Verify which lookups are actually supported by the FilterSet."""
        verified_lookups = []

        for lookup_code, lookup_label in lookups:
            if lookup_code in (MODIFIER_EMPTY_TRUE, MODIFIER_EMPTY_FALSE):
                filter_key = f'{field_name}__empty'
            else:
                filter_key = f'{field_name}__{lookup_code}' if lookup_code != 'exact' else field_name

            if filter_key in filterset.filters:
                verified_lookups.append((lookup_code, lookup_label))

        return verified_lookups
