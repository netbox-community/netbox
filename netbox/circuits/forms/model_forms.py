from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from circuits.choices import (
    CircuitCommitRateChoices,
    CircuitTerminationPortSpeedChoices,
    VirtualCircuitTerminationRoleChoices,
)
from circuits.constants import *
from circuits.models import *
from dcim.models import Interface
from ipam.models import ASN
from netbox.forms import NetBoxModelForm, OrganizationalModelForm, PrimaryModelForm
from tenancy.forms import TenancyForm
from utilities.forms import GenericObjectFormMixin
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    GenericObjectChoiceField,
    SlugField,
)
from utilities.forms.mixins import DistanceValidationMixin
from utilities.forms.rendering import FieldSet, InlineFields, M2MAddRemoveFields
from utilities.forms.widgets import DatePicker, NumberWithOptions

__all__ = (
    'CircuitForm',
    'CircuitGroupAssignmentForm',
    'CircuitGroupForm',
    'CircuitTerminationForm',
    'CircuitTypeForm',
    'ProviderAccountForm',
    'ProviderForm',
    'ProviderNetworkForm',
    'VirtualCircuitForm',
    'VirtualCircuitTerminationForm',
    'VirtualCircuitTypeForm',
)


class ProviderForm(PrimaryModelForm):
    slug = SlugField()
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('ASNs'),
        required=False
    )
    add_asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('Add ASNs'),
        required=False
    )
    remove_asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('Remove ASNs'),
        required=False
    )

    fieldsets = (
        FieldSet('name', 'slug', M2MAddRemoveFields('asns'), 'description', 'tags'),
    )

    class Meta:
        model = Provider
        fields = [
            'name', 'slug', 'description', 'owner', 'comments', 'tags',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and (count := self.instance.asns.count()) >= M2MAddRemoveFields.THRESHOLD:
            # Add/remove mode for large M2M sets
            self.fields.pop('asns')
            self.fields['add_asns'].widget.add_query_param('provider_id__n', self.instance.pk)
            self.fields['remove_asns'].widget.add_query_param('provider_id', self.instance.pk)
            self.fields['remove_asns'].help_text = _("{count} ASNs currently assigned").format(count=count)
        else:
            # Simple mode for new objects or small M2M sets
            self.fields.pop('add_asns')
            self.fields.pop('remove_asns')
            if self.instance.pk:
                self.initial['asns'] = list(self.instance.asns.values_list('pk', flat=True))


class ProviderAccountForm(PrimaryModelForm):
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        selector=True,
        quick_add=True
    )

    fieldsets = (
        FieldSet('provider', 'account', 'name', 'description', 'tags'),
    )

    class Meta:
        model = ProviderAccount
        fields = [
            'provider', 'account', 'name', 'description', 'owner', 'comments', 'tags',
        ]


class ProviderNetworkForm(PrimaryModelForm):
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        selector=True,
        quick_add=True
    )

    fieldsets = (
        FieldSet('provider', 'name', 'service_id', 'description', 'tags'),
    )

    class Meta:
        model = ProviderNetwork
        fields = [
            'provider', 'name', 'service_id', 'description', 'owner', 'comments', 'tags',
        ]


class CircuitTypeForm(OrganizationalModelForm):
    fieldsets = (
        FieldSet('name', 'slug', 'color', 'description', 'tags'),
    )

    class Meta:
        model = CircuitType
        fields = [
            'name', 'slug', 'color', 'description', 'owner', 'comments', 'tags',
        ]


class CircuitForm(DistanceValidationMixin, TenancyForm, PrimaryModelForm):
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
            'distance', 'distance_unit', 'description', 'tenant_group', 'tenant', 'owner', 'comments', 'tags',
        ]
        widgets = {
            'install_date': DatePicker(),
            'termination_date': DatePicker(),
            'commit_rate': NumberWithOptions(
                options=CircuitCommitRateChoices
            ),
        }


class CircuitTerminationForm(GenericObjectFormMixin, NetBoxModelForm):
    circuit = DynamicModelChoiceField(
        label=_('Circuit'),
        queryset=Circuit.objects.all(),
        selector=True
    )
    termination = GenericObjectChoiceField(
        label=_('Termination'),
        content_type_queryset=ContentType.objects.filter(model__in=CIRCUIT_TERMINATION_TERMINATION_TYPES),
        required=True,
        selector=True,
        hx_target_id='circuit-termination',
    )

    fieldsets = (
        FieldSet(
            'circuit', 'term_side', 'description', 'tags', 'termination', 'mark_connected',
            name=_('Circuit Termination'), html_id='circuit-termination',
        ),
        FieldSet('port_speed', 'upstream_speed', 'xconnect_id', 'pp_info', name=_('Termination Details')),
    )

    class Meta:
        model = CircuitTermination
        fields = [
            'circuit', 'term_side', 'mark_connected', 'port_speed', 'upstream_speed',
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


class CircuitGroupForm(TenancyForm, OrganizationalModelForm):
    fieldsets = (
        FieldSet('name', 'slug', 'description', 'tags', name=_('Circuit Group')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = CircuitGroup
        fields = [
            'name', 'slug', 'description', 'tenant_group', 'tenant', 'owner', 'comments', 'tags',
        ]


class CircuitGroupAssignmentForm(GenericObjectFormMixin, NetBoxModelForm):
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=CircuitGroup.objects.all(),
    )
    member = GenericObjectChoiceField(
        label=_('Member'),
        content_type_queryset=ContentType.objects.filter(CIRCUIT_GROUP_ASSIGNMENT_MEMBER_MODELS),
        required=False,
        selector=True,
        hx_target_id='circuit-group-assignment',
    )

    fieldsets = (
        FieldSet(
            'group', 'member', 'priority', 'tags',
            name=_('Group Assignment'), html_id='circuit-group-assignment',
        ),
    )

    class Meta:
        model = CircuitGroupAssignment
        fields = [
            'group', 'priority', 'tags',
        ]


class VirtualCircuitTypeForm(OrganizationalModelForm):
    fieldsets = (
        FieldSet('name', 'slug', 'color', 'description', 'tags'),
    )

    class Meta:
        model = VirtualCircuitType
        fields = [
            'name', 'slug', 'color', 'description', 'owner', 'comments', 'tags',
        ]


class VirtualCircuitForm(TenancyForm, PrimaryModelForm):
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
    type = DynamicModelChoiceField(
        queryset=VirtualCircuitType.objects.all(),
        quick_add=True
    )

    fieldsets = (
        FieldSet(
            'provider_network', 'provider_account', 'cid', 'type', 'status', 'description', 'tags',
            name=_('Virtual circuit'),
        ),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
    )

    class Meta:
        model = VirtualCircuit
        fields = [
            'cid', 'provider_network', 'provider_account', 'type', 'status', 'description', 'tenant_group', 'tenant',
            'owner', 'comments', 'tags',
        ]


class VirtualCircuitTerminationForm(NetBoxModelForm):
    virtual_circuit = DynamicModelChoiceField(
        label=_('Virtual circuit'),
        queryset=VirtualCircuit.objects.all(),
        selector=True
    )
    role = forms.ChoiceField(
        choices=VirtualCircuitTerminationRoleChoices,
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
        FieldSet(
            'virtual_circuit', 'role', 'interface', 'description', 'tags',
        ),
    )

    class Meta:
        model = VirtualCircuitTermination
        fields = [
            'virtual_circuit', 'role', 'interface', 'description', 'tags',
        ]
