from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import connection
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from dcim.constants import LOCATION_SCOPE_TYPES
from dcim.models import PortMapping, PortTemplateMapping, Site
from utilities.forms import get_field_value
from utilities.forms.fields import (
    ContentTypeChoiceField,
    CSVContentTypeField,
    DynamicModelChoiceField,
)
from utilities.forms.widgets import HTMXSelect
from utilities.templatetags.builtins.filters import bettertitle

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

            if self.instance and self.instance.pk and scope_type_id != self.instance.scope_type_id:
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

    def clean(self):
        super().clean()

        # Check that the total number of FrontPorts and positions matches the selected number of RearPort:position
        # mappings. Note that `name` will be a list under FrontPortCreateForm, in which cases we multiply the number of
        # FrontPorts being creation by the number of positions.
        positions = self.cleaned_data['positions']
        frontport_count = len(self.cleaned_data['name']) if type(self.cleaned_data['name']) is list else 1
        rearport_count = len(self.cleaned_data['rear_ports'])
        if frontport_count * positions != rearport_count:
            raise forms.ValidationError({
                'rear_ports': _(
                    "The total number of front port positions ({frontport_count}) must match the selected number of "
                    "rear port positions ({rearport_count})."
                ).format(
                    frontport_count=frontport_count,
                    rearport_count=rearport_count
                )
            })

    def _save_m2m(self):
        super()._save_m2m()

        # TODO: Can this be made more efficient?
        # Delete existing rear port mappings
        self.port_mapping_model.objects.filter(front_port_id=self.instance.pk).delete()

        # Create new rear port mappings
        mappings = []
        if self.port_mapping_model is PortTemplateMapping:
            params = {
                'device_type_id': self.instance.device_type_id,
                'module_type_id': self.instance.module_type_id,
            }
        else:
            params = {
                'device_id': self.instance.device_id,
            }
        for i, rp_position in enumerate(self.cleaned_data['rear_ports'], start=1):
            rear_port_id, rear_port_position = rp_position.split(':')
            mappings.append(
                self.port_mapping_model(**{
                    **params,
                    'front_port_id': self.instance.pk,
                    'front_port_position': i,
                    'rear_port_id': rear_port_id,
                    'rear_port_position': rear_port_position,
                })
            )
        self.port_mapping_model.objects.bulk_create(mappings)
        # Send post_save signals
        for mapping in mappings:
            post_save.send(
                sender=PortMapping,
                instance=mapping,
                created=True,
                raw=False,
                using=connection,
                update_fields=None
            )

    def _get_rear_port_choices(self, parent_filter, front_port):
        """
        Return a list of choices representing each available rear port & position pair on the parent object (identified
        by a Q filter), excluding those assigned to the specified instance.
        """
        occupied_rear_port_positions = [
            f'{mapping.rear_port_id}:{mapping.rear_port_position}'
            for mapping in self.port_mapping_model.objects.filter(parent_filter).exclude(front_port=front_port.pk)
        ]

        choices = []
        for rear_port in self.rear_port_model.objects.filter(parent_filter):
            for i in range(1, rear_port.positions + 1):
                pair_id = f'{rear_port.pk}:{i}'
                if pair_id not in occupied_rear_port_positions:
                    pair_label = f'{rear_port.name}:{i}'
                    choices.append((pair_id, pair_label))
        return choices
