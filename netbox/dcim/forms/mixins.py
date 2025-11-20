from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.constants import LOCATION_SCOPE_TYPES
from dcim.models import PortAssignmentTemplate, Site
from utilities.forms import get_field_value
from utilities.forms.fields import (
    ContentTypeChoiceField, CSVContentTypeField, DynamicModelChoiceField,
)
from utilities.templatetags.builtins.filters import bettertitle
from utilities.forms.widgets import HTMXSelect

__all__ = (
    'FrontPortFormMixin',
    'ScopedBulkEditForm',
    'ScopedForm',
    'ScopedImportForm',
)


class ScopedForm(forms.Form):
    scope_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        widget=HTMXSelect(),
        required=False,
        label=_('Scope type')
    )
    scope = DynamicModelChoiceField(
        label=_('Scope'),
        queryset=Site.objects.none(),  # Initial queryset
        required=False,
        disabled=True,
        selector=True
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})

        if instance is not None and instance.scope:
            initial['scope'] = instance.scope
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)
        self._set_scoped_values()

    def clean(self):
        super().clean()

        scope = self.cleaned_data.get('scope')
        scope_type = self.cleaned_data.get('scope_type')
        if scope_type and not scope:
            raise ValidationError({
                'scope': _(
                    "Please select a {scope_type}."
                ).format(scope_type=scope_type.model_class()._meta.model_name)
            })

        # Assign the selected scope (if any)
        self.instance.scope = scope

    def _set_scoped_values(self):
        if scope_type_id := get_field_value(self, 'scope_type'):
            try:
                scope_type = ContentType.objects.get(pk=scope_type_id)
                model = scope_type.model_class()
                self.fields['scope'].queryset = model.objects.all()
                self.fields['scope'].widget.attrs['selector'] = model._meta.label_lower
                self.fields['scope'].disabled = False
                self.fields['scope'].label = _(bettertitle(model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            if self.instance and scope_type_id != self.instance.scope_type_id:
                self.initial['scope'] = None

        else:
            # Clear the initial scope value if scope_type is not set
            self.initial['scope'] = None


class ScopedBulkEditForm(forms.Form):
    scope_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        widget=HTMXSelect(method='post', attrs={'hx-select': '#form_fields'}),
        required=False,
        label=_('Scope type')
    )
    scope = DynamicModelChoiceField(
        label=_('Scope'),
        queryset=Site.objects.none(),  # Initial queryset
        required=False,
        disabled=True,
        selector=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if scope_type_id := get_field_value(self, 'scope_type'):
            try:
                scope_type = ContentType.objects.get(pk=scope_type_id)
                model = scope_type.model_class()
                self.fields['scope'].queryset = model.objects.all()
                self.fields['scope'].widget.attrs['selector'] = model._meta.label_lower
                self.fields['scope'].disabled = False
                self.fields['scope'].label = _(bettertitle(model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass


class ScopedImportForm(forms.Form):
    scope_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        required=False,
        label=_('Scope type (app & model)')
    )

    def clean(self):
        super().clean()

        scope_id = self.cleaned_data.get('scope_id')
        scope_type = self.cleaned_data.get('scope_type')
        if scope_type and not scope_id:
            raise ValidationError({
                'scope_id': _(
                    "Please select a {scope_type}."
                ).format(scope_type=scope_type.model_class()._meta.model_name)
            })


class FrontPortFormMixin(forms.Form):
    rear_ports = forms.MultipleChoiceField(
        choices=[],
        label=_('Rear ports'),
        widget=forms.SelectMultiple(attrs={'size': 8})
    )

    port_assignment_model = PortAssignmentTemplate

    def clean(self):
        super().clean()

        # FrontPort with no positions cannot be mapped to more than one RearPort
        if not self.cleaned_data['positions'] and len(self.cleaned_data['rear_ports']) > 1:
            raise forms.ValidationError({
                'positions': _("A front port with no positions cannot be mapped to multiple rear ports.")
            })

        # Count of selected rear port & position pairs much match the assigned number of positions
        if len(self.cleaned_data['rear_ports']) != self.cleaned_data['positions']:
            raise forms.ValidationError({
                'rear_ports': _(
                    "The number of rear port/position pairs selected must match the number of positions assigned."
                )
            })

    def _save_m2m(self):
        super()._save_m2m()

        # TODO: Can this be made more efficient?
        # Delete existing rear port assignments
        self.port_assignment_model.objects.filter(front_port_id=self.instance.pk).delete()

        # Create new rear port assignments
        assignments = []
        for i, rp_position in enumerate(self.cleaned_data['rear_ports'], start=1):
            rear_port_id, rear_port_position = rp_position.split(':')
            assignments.append(
                self.port_assignment_model(
                    front_port_id=self.instance.pk,
                    front_port_position=i,
                    rear_port_id=rear_port_id,
                    rear_port_position=rear_port_position,
                )
            )
        self.port_assignment_model.objects.bulk_create(assignments)
