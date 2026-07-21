from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.constants import LOCATION_SCOPE_TYPES
from dcim.utils import reconcile_port_mappings
from utilities.forms import GenericObjectFormMixin
from utilities.forms.fields import (
    CSVContentTypeField,
    GenericObjectChoiceField,
)
from utilities.templatetags.builtins.filters import bettertitle

__all__ = (
    'FrontPortFormMixin',
    'ScopedBulkEditForm',
    'ScopedForm',
    'ScopedImportForm',
)


class ScopedForm(GenericObjectFormMixin, forms.Form):
    scope = GenericObjectChoiceField(
        label=_('Scope'),
        content_type_queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        required=False,
        selector=True,
        hx_target_id='scope',
    )


class ScopedBulkEditForm(GenericObjectFormMixin, forms.Form):
    scope = GenericObjectChoiceField(
        label=_('Scope'),
        content_type_queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        required=False,
        selector=True,
        hx_method='post',
    )


class ScopedImportForm(forms.Form):
    scope_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        required=False,
        label=_('Scope type (app & model)')
    )
    scope_name = forms.CharField(
        required=False,
        label=_('Scope name'),
        help_text=_('Name of the assigned scope object (if not using ID)')
    )

    def clean(self):
        super().clean()

        scope_id = self.cleaned_data.get('scope_id')
        scope_name = self.cleaned_data.get('scope_name')
        scope_type = self.cleaned_data.get('scope_type')

        # Cannot specify both scope_name and scope_id
        if scope_name and scope_id:
            raise ValidationError(_("scope_name and scope_id are mutually exclusive."))

        # Must specify scope_type with scope_name or scope_id
        if scope_name and not scope_type:
            raise ValidationError(_("scope_type must be specified when using scope_name"))
        if scope_id and not scope_type:
            raise ValidationError(_("scope_type must be specified when using scope_id"))

        # Look up the scope object by name
        if scope_type and scope_name:
            model = scope_type.model_class()
            try:
                scope_obj = model.objects.get(name=scope_name)
            except model.DoesNotExist:
                raise ValidationError({
                    'scope_name': _('{scope_type} "{name}" not found.').format(
                        scope_type=bettertitle(model._meta.verbose_name),
                        name=scope_name
                    )
                })
            except model.MultipleObjectsReturned:
                raise ValidationError({
                    'scope_name': _(
                        'Multiple {scope_type} objects match "{name}". Use scope_id to specify the intended object.'
                    ).format(
                        scope_type=bettertitle(model._meta.verbose_name),
                        name=scope_name,
                    )
                })
            self.cleaned_data['scope_id'] = scope_obj.pk
        elif scope_type and not scope_id:
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

        # Build the desired set of mappings from the submitted rear port pairs, assigning front port
        # positions in order. reconcile_port_mappings() then writes only the difference, so re-saving
        # a front port without changing its wiring produces no writes (and no changelog churn).
        desired = []
        for i, rp_position in enumerate(self.cleaned_data['rear_ports'], start=1):
            rear_port_id, rear_port_position = rp_position.split(':')
            desired.append({
                'front_port_position': i,
                'rear_port_id': int(rear_port_id),
                'rear_port_position': int(rear_port_position),
            })

        reconcile_port_mappings(
            self.port_mapping_model,
            parent_field='front_port',
            parent=self.instance,
            desired=desired,
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
