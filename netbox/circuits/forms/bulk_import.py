from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from circuits.choices import *
from circuits.constants import *
from circuits.models import *
from dcim.models import Interface
from netbox.choices import DistanceUnitChoices
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import CSVChoiceField, CSVContentTypeField, CSVModelChoiceField, SlugField

__all__ = (
    'CircuitImportForm',
    'CircuitGroupAssignmentImportForm',
    'CircuitGroupImportForm',
    'CircuitTerminationImportForm',
    'CircuitTerminationImportRelatedForm',
    'CircuitTypeImportForm',
    'ProviderImportForm',
    'ProviderAccountImportForm',
    'ProviderNetworkImportForm',
    'VirtualCircuitImportForm',
    'VirtualCircuitTerminationImportForm',
    'VirtualCircuitTerminationImportRelatedForm',
)


class ProviderImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = Provider
        fields = (
            'name', 'slug', 'description', 'comments', 'tags',
        )


class ProviderAccountImportForm(NetBoxModelImportForm):
    provider = CSVModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text=_('Assigned provider')
    )

    class Meta:
        model = ProviderAccount
        fields = (
            'provider', 'name', 'account', 'description', 'comments', 'tags',
        )


class ProviderNetworkImportForm(NetBoxModelImportForm):
    provider = CSVModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text=_('Assigned provider')
    )

    class Meta:
        model = ProviderNetwork
        fields = [
            'provider', 'name', 'service_id', 'description', 'comments', 'tags'
        ]


class CircuitTypeImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = ('name', 'slug', 'color', 'description', 'tags')


class CircuitImportForm(NetBoxModelImportForm):
    provider = CSVModelChoiceField(
        label=_('Provider'),
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text=_('Assigned provider')
    )
    provider_account = CSVModelChoiceField(
        label=_('Provider account'),
        queryset=ProviderAccount.objects.all(),
        to_field_name='name',
        help_text=_('Assigned provider account'),
        required=False
    )
    type = CSVModelChoiceField(
        label=_('Type'),
        queryset=CircuitType.objects.all(),
        to_field_name='name',
        help_text=_('Type of circuit')
    )
    status = CSVChoiceField(
        label=_('Status'),
        choices=CircuitStatusChoices,
        help_text=_('Operational status')
    )
    distance_unit = CSVChoiceField(
        label=_('Distance unit'),
        choices=DistanceUnitChoices,
        required=False,
        help_text=_('Distance unit')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = Circuit
        fields = [
            'cid', 'provider', 'provider_account', 'type', 'status', 'tenant', 'install_date', 'termination_date',
            'commit_rate', 'distance', 'distance_unit', 'description', 'comments', 'tags'
        ]


class BaseCircuitTerminationImportForm(forms.ModelForm):
    circuit = CSVModelChoiceField(
        label=_('Circuit'),
        queryset=Circuit.objects.all(),
        to_field_name='cid',
    )
    term_side = CSVChoiceField(
        label=_('Termination'),
        choices=CircuitTerminationSideChoices,
    )
    termination_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(model__in=CIRCUIT_TERMINATION_TERMINATION_TYPES),
        required=False,
        label=_('Termination type (app & model)')
    )


class CircuitTerminationImportRelatedForm(BaseCircuitTerminationImportForm):
    class Meta:
        model = CircuitTermination
        fields = [
            'circuit', 'term_side', 'termination_type', 'termination_id', 'port_speed', 'upstream_speed', 'xconnect_id',
            'pp_info', 'description'
        ]
        labels = {
            'termination_id': _('Termination ID'),
        }


class CircuitTerminationImportForm(NetBoxModelImportForm, BaseCircuitTerminationImportForm):

    class Meta:
        model = CircuitTermination
        fields = [
            'circuit', 'term_side', 'termination_type', 'termination_id', 'port_speed', 'upstream_speed', 'xconnect_id',
            'pp_info', 'description', 'tags'
        ]
        labels = {
            'termination_id': _('Termination ID'),
        }


class CircuitGroupImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = CircuitGroup
        fields = ('name', 'slug', 'description', 'tenant', 'tags')


class CircuitGroupAssignmentImportForm(NetBoxModelImportForm):

    class Meta:
        model = CircuitGroupAssignment
        fields = ('circuit', 'group', 'priority')


class VirtualCircuitImportForm(NetBoxModelImportForm):
    provider_network = CSVModelChoiceField(
        label=_('Provider network'),
        queryset=ProviderNetwork.objects.all(),
        to_field_name='name',
        help_text=_('The network to which this virtual circuit belongs')
    )
    provider_account = CSVModelChoiceField(
        label=_('Provider account'),
        queryset=ProviderAccount.objects.all(),
        to_field_name='account',
        help_text=_('Assigned provider account (if any)'),
        required=False
    )
    status = CSVChoiceField(
        label=_('Status'),
        choices=CircuitStatusChoices,
        help_text=_('Operational status')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = VirtualCircuit
        fields = [
            'cid', 'provider_network', 'provider_account', 'status', 'tenant', 'description', 'comments', 'tags',
        ]


class BaseVirtualCircuitTerminationImportForm(forms.ModelForm):
    virtual_circuit = CSVModelChoiceField(
        label=_('Virtual circuit'),
        queryset=VirtualCircuit.objects.all(),
        to_field_name='cid',
    )
    role = CSVChoiceField(
        label=_('Role'),
        choices=VirtualCircuitTerminationRoleChoices,
        help_text=_('Operational role')
    )
    interface = CSVModelChoiceField(
        label=_('Interface'),
        queryset=Interface.objects.all(),
        to_field_name='pk',
    )


class VirtualCircuitTerminationImportRelatedForm(BaseVirtualCircuitTerminationImportForm):

    class Meta:
        model = VirtualCircuitTermination
        fields = [
            'virtual_circuit', 'role', 'interface', 'description',
        ]


class VirtualCircuitTerminationImportForm(NetBoxModelImportForm, BaseVirtualCircuitTerminationImportForm):

    class Meta:
        model = VirtualCircuitTermination
        fields = [
            'virtual_circuit', 'role', 'interface', 'description', 'tags',
        ]
