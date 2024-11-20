from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from circuits.choices import (
    CircuitCommitRateChoices, CircuitTerminationPortSpeedChoices, VirtualCircuitTerminationRoleChoices,
)
from circuits.constants import *
from circuits.models import *
from dcim.models import Interface, Site
from ipam.models import ASN
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms import get_field_value
from utilities.forms.fields import (
    CommentField, ContentTypeChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, SlugField,
)
from utilities.forms.rendering import FieldSet, InlineFields
from utilities.forms.widgets import DatePicker, HTMXSelect, NumberWithOptions
from utilities.templatetags.builtins.filters import bettertitle

__all__ = (
    'CircuitForm',
    'CircuitGroupAssignmentForm',
    'CircuitGroupForm',
    'CircuitTerminationForm',
    'CircuitTypeForm',
    'ProviderForm',
    'ProviderAccountForm',
    'ProviderNetworkForm',
    'VirtualCircuitForm',
    'VirtualCircuitTerminationForm',
)


class ProviderForm(NetBoxModelForm):
    slug = SlugField()
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('ASNs'),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('name', 'slug', 'asns', 'description', 'tags'),
    )

    class Meta:
        model = Provider
        fields = [
            'name', 'slug', 'asns', 'description', 'comments', 'tags',
        ]


class ProviderAccountForm(NetBoxModelForm):
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        selector=True,
        quick_add=True
    )
    comments = CommentField()

    class Meta:
        model = ProviderAccount
        fields = [
            'provider', 'name', 'account', 'description', 'comments', 'tags',
        ]


class ProviderNetworkForm(NetBoxModelForm):
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        selector=True,
        quick_add=True
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('provider', 'name', 'service_id', 'description', 'tags'),
    )

    class Meta:
        model = ProviderNetwork
        fields = [
            'provider', 'name', 'service_id', 'description', 'comments', 'tags',
        ]


class CircuitTypeForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        FieldSet('name', 'slug', 'color', 'description', 'tags'),
    )

    class Meta:
        model = CircuitType
        fields = [
            'name', 'slug', 'color', 'description', 'tags',
        ]


class CircuitForm(TenancyForm, NetBoxModelForm):
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        selector=True,
        quick_add=True
    )
    provider_account = DynamicModelChoiceField(
        label=_('Provider account'),
        queryset=ProviderAccount.objects.all(),
        required=False,
        query_params={
            'provider_id': '$provider',
        }
    )
    type = DynamicModelChoiceField(
        queryset=CircuitType.objects.all(),
        quick_add=True
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'provider',
            'provider_account',
            'cid',
            'type',
            'status',
            InlineFields('distance', 'distance_unit', label=_('Distance')),
            'description',
            'tags',
            name=_('Circuit')
        ),
        FieldSet('install_date', 'termination_date', 'commit_rate', name=_('Service Parameters')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = Circuit
        fields = [
            'cid', 'type', 'provider', 'provider_account', 'status', 'install_date', 'termination_date', 'commit_rate',
            'distance', 'distance_unit', 'description', 'tenant_group', 'tenant', 'comments', 'tags',
        ]
        widgets = {
            'install_date': DatePicker(),
            'termination_date': DatePicker(),
            'commit_rate': NumberWithOptions(
                options=CircuitCommitRateChoices
            ),
        }


class CircuitTerminationForm(NetBoxModelForm):
    circuit = DynamicModelChoiceField(
        label=_('Circuit'),
        queryset=Circuit.objects.all(),
        selector=True
    )
    termination_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(model__in=CIRCUIT_TERMINATION_TERMINATION_TYPES),
        widget=HTMXSelect(),
        required=False,
        label=_('Termination type')
    )
    termination = DynamicModelChoiceField(
        label=_('Termination'),
        queryset=Site.objects.none(),  # Initial queryset
        required=False,
        disabled=True,
        selector=True
    )

    fieldsets = (
        FieldSet(
            'circuit', 'term_side', 'description', 'tags',
            'termination_type', 'termination',
            'mark_connected', name=_('Circuit Termination')
        ),
        FieldSet('port_speed', 'upstream_speed', 'xconnect_id', 'pp_info', name=_('Termination Details')),
    )

    class Meta:
        model = CircuitTermination
        fields = [
            'circuit', 'term_side', 'termination_type', 'mark_connected', 'port_speed', 'upstream_speed',
            'xconnect_id', 'pp_info', 'description', 'tags',
        ]
        widgets = {
            'port_speed': NumberWithOptions(
                options=CircuitTerminationPortSpeedChoices
            ),
            'upstream_speed': NumberWithOptions(
                options=CircuitTerminationPortSpeedChoices
            ),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})

        if instance is not None and instance.termination:
            initial['termination'] = instance.termination
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        if termination_type_id := get_field_value(self, 'termination_type'):
            try:
                termination_type = ContentType.objects.get(pk=termination_type_id)
                model = termination_type.model_class()
                self.fields['termination'].queryset = model.objects.all()
                self.fields['termination'].widget.attrs['selector'] = model._meta.label_lower
                self.fields['termination'].disabled = False
                self.fields['termination'].label = _(bettertitle(model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            if self.instance and termination_type_id != self.instance.termination_type_id:
                self.initial['termination'] = None

    def clean(self):
        super().clean()

        # Assign the selected termination (if any)
        self.instance.termination = self.cleaned_data.get('termination')


class CircuitGroupForm(TenancyForm, NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        FieldSet('name', 'slug', 'description', 'tags', name=_('Circuit Group')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = CircuitGroup
        fields = [
            'name', 'slug', 'description', 'tenant_group', 'tenant', 'tags',
        ]


class CircuitGroupAssignmentForm(NetBoxModelForm):
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=CircuitGroup.objects.all(),
    )
    circuit = DynamicModelChoiceField(
        label=_('Circuit'),
        queryset=Circuit.objects.all(),
        selector=True
    )

    class Meta:
        model = CircuitGroupAssignment
        fields = [
            'group', 'circuit', 'priority', 'tags',
        ]


class VirtualCircuitForm(TenancyForm, NetBoxModelForm):
    provider_network = DynamicModelChoiceField(
        label=_('Provider network'),
        queryset=ProviderNetwork.objects.all(),
        selector=True
    )
    provider_account = DynamicModelChoiceField(
        label=_('Provider account'),
        queryset=ProviderAccount.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'provider_network', 'provider_account', 'cid', 'status', 'description', 'tags', name=_('Virtual circuit'),
        ),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = VirtualCircuit
        fields = [
            'cid', 'provider_network', 'provider_account', 'status', 'description', 'tenant_group', 'tenant',
            'comments', 'tags',
        ]


class VirtualCircuitTerminationForm(NetBoxModelForm):
    virtual_circuit = DynamicModelChoiceField(
        label=_('Virtual circuit'),
        queryset=VirtualCircuit.objects.all(),
        selector=True
    )
    role = forms.ChoiceField(
        choices=VirtualCircuitTerminationRoleChoices,
        widget=HTMXSelect(),
        label=_('Role')
    )
    interface = DynamicModelChoiceField(
        label=_('Interface'),
        queryset=Interface.objects.all(),
        selector=True,
        query_params={
            'kind': 'virtual',
            'virtual_circuit_termination_id': 'null',
        },
        context={
            'parent': 'device',
        }
    )

    fieldsets = (
        FieldSet('virtual_circuit', 'role', 'interface', 'description', 'tags'),
    )

    class Meta:
        model = VirtualCircuitTermination
        fields = [
            'virtual_circuit', 'role', 'interface', 'description', 'tags',
        ]
