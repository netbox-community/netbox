from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from circuits.choices import (
    CircuitCommitRateChoices, CircuitPriorityChoices, CircuitStatusChoices, VirtualCircuitTerminationRoleChoices,
)
from circuits.constants import CIRCUIT_TERMINATION_TERMINATION_TYPES
from circuits.models import *
from dcim.models import Site
from ipam.models import ASN
from netbox.choices import DistanceUnitChoices
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import add_blank_choice, get_field_value
from utilities.forms.fields import (
    ColorField, CommentField, ContentTypeChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import BulkEditNullBooleanSelect, DatePicker, HTMXSelect, NumberWithOptions
from utilities.templatetags.builtins.filters import bettertitle

__all__ = (
    'CircuitBulkEditForm',
    'CircuitGroupAssignmentBulkEditForm',
    'CircuitGroupBulkEditForm',
    'CircuitTerminationBulkEditForm',
    'CircuitTypeBulkEditForm',
    'ProviderBulkEditForm',
    'ProviderAccountBulkEditForm',
    'ProviderNetworkBulkEditForm',
    'VirtualCircuitBulkEditForm',
    'VirtualCircuitTerminationBulkEditForm',
    'VirtualCircuitTypeBulkEditForm',
)


class ProviderBulkEditForm(NetBoxModelBulkEditForm):
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('ASNs'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Provider
    fieldsets = (
        FieldSet('asns', 'description'),
    )
    nullable_fields = (
        'asns', 'description', 'comments',
    )


class ProviderAccountBulkEditForm(NetBoxModelBulkEditForm):
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = ProviderAccount
    fieldsets = (
        FieldSet('provider', 'description'),
    )
    nullable_fields = (
        'description', 'comments',
    )


class ProviderNetworkBulkEditForm(NetBoxModelBulkEditForm):
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        required=False
    )
    service_id = forms.CharField(
        max_length=100,
        required=False,
        label=_('Service ID')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = ProviderNetwork
    fieldsets = (
        FieldSet('provider', 'service_id', 'description'),
    )
    nullable_fields = (
        'service_id', 'description', 'comments',
    )


class CircuitTypeBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        label=_('Color'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = CircuitType
    fieldsets = (
        FieldSet('color', 'description'),
    )
    nullable_fields = ('color', 'description')


class CircuitBulkEditForm(NetBoxModelBulkEditForm):
    type = DynamicModelChoiceField(
        label=_('Type'),
        queryset=CircuitType.objects.all(),
        required=False
    )
    provider = DynamicModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        required=False
    )
    provider_account = DynamicModelChoiceField(
        label=_('Provider account'),
        queryset=ProviderAccount.objects.all(),
        required=False,
        query_params={
            'provider': '$provider'
        }
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(CircuitStatusChoices),
        required=False,
        initial=''
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    install_date = forms.DateField(
        label=_('Install date'),
        required=False,
        widget=DatePicker()
    )
    termination_date = forms.DateField(
        label=_('Termination date'),
        required=False,
        widget=DatePicker()
    )
    commit_rate = forms.IntegerField(
        required=False,
        label=_('Commit rate (Kbps)'),
        widget=NumberWithOptions(
            options=CircuitCommitRateChoices
        )
    )
    distance = forms.DecimalField(
        label=_('Distance'),
        min_value=0,
        required=False
    )
    distance_unit = forms.ChoiceField(
        label=_('Distance unit'),
        choices=add_blank_choice(DistanceUnitChoices),
        required=False,
        initial=''
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=100,
        required=False
    )
    comments = CommentField()

    model = Circuit
    fieldsets = (
        FieldSet('provider', 'type', 'status', 'description', name=_('Circuit')),
        FieldSet('provider_account', 'install_date', 'termination_date', 'commit_rate', name=_('Service Parameters')),
        FieldSet('distance', 'distance_unit', name=_('Attributes')),
        FieldSet('tenant', name=_('Tenancy')),
    )
    nullable_fields = (
        'tenant', 'commit_rate', 'description', 'comments',
    )


class CircuitTerminationBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    termination_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(model__in=CIRCUIT_TERMINATION_TERMINATION_TYPES),
        widget=HTMXSelect(method='post', attrs={'hx-select': '#form_fields'}),
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
    port_speed = forms.IntegerField(
        required=False,
        label=_('Port speed (Kbps)'),
    )
    upstream_speed = forms.IntegerField(
        required=False,
        label=_('Upstream speed (Kbps)'),
    )
    mark_connected = forms.NullBooleanField(
        label=_('Mark connected'),
        required=False,
        widget=BulkEditNullBooleanSelect
    )

    model = CircuitTermination
    fieldsets = (
        FieldSet(
            'description',
            'termination_type', 'termination',
            'mark_connected', name=_('Circuit Termination')
        ),
        FieldSet('port_speed', 'upstream_speed', name=_('Termination Details')),
    )
    nullable_fields = ('description', 'termination')

    def __init__(self, *args, **kwargs):
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


class CircuitGroupBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )

    model = CircuitGroup
    nullable_fields = (
        'description', 'tenant',
    )


class CircuitGroupAssignmentBulkEditForm(NetBoxModelBulkEditForm):
    member = DynamicModelChoiceField(
        label=_('Circuit'),
        queryset=Circuit.objects.all(),
        required=False
    )
    priority = forms.ChoiceField(
        label=_('Priority'),
        choices=add_blank_choice(CircuitPriorityChoices),
        required=False
    )

    model = CircuitGroupAssignment
    fieldsets = (
        FieldSet('member', 'priority'),
    )
    nullable_fields = ('priority',)


class VirtualCircuitTypeBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        label=_('Color'),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = VirtualCircuitType
    fieldsets = (
        FieldSet('color', 'description'),
    )
    nullable_fields = ('color', 'description')


class VirtualCircuitBulkEditForm(NetBoxModelBulkEditForm):
    provider_network = DynamicModelChoiceField(
        label=_('Provider network'),
        queryset=ProviderNetwork.objects.all(),
        required=False
    )
    provider_account = DynamicModelChoiceField(
        label=_('Provider account'),
        queryset=ProviderAccount.objects.all(),
        required=False
    )
    type = DynamicModelChoiceField(
        label=_('Type'),
        queryset=VirtualCircuitType.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(CircuitStatusChoices),
        required=False,
        initial=''
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=100,
        required=False
    )
    comments = CommentField()

    model = VirtualCircuit
    fieldsets = (
        FieldSet('provider_network', 'provider_account', 'status', 'description', name=_('Virtual circuit')),
        FieldSet('tenant', name=_('Tenancy')),
    )
    nullable_fields = (
        'provider_account', 'tenant', 'description', 'comments',
    )


class VirtualCircuitTerminationBulkEditForm(NetBoxModelBulkEditForm):
    role = forms.ChoiceField(
        label=_('Role'),
        choices=add_blank_choice(VirtualCircuitTerminationRoleChoices),
        required=False,
        initial=''
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = VirtualCircuitTermination
    fieldsets = (
        FieldSet('role', 'description'),
    )
    nullable_fields = ('description',)
