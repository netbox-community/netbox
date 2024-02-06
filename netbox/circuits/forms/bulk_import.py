from django import forms

from circuits.choices import CircuitStatusChoices
from circuits.models import *
from dcim.models import Site
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField, SlugField

__all__ = (
    'CircuitImportForm',
    'CircuitTerminationImportForm',
    'CircuitTypeImportForm',
    'ProviderImportForm',
    'ProviderAccountImportForm',
    'ProviderNetworkImportForm',
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
        help_texts = {
            'color': mark_safe(_('RGB color in hexadecimal. Example:') + ' <code>00ff00</code>'),
        }


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
            'commit_rate', 'description', 'comments', 'tags'
        ]


class CircuitTerminationImportForm(forms.ModelForm):
    site = CSVModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False
    )
    provider_network = CSVModelChoiceField(
        label=_('Provider network'),
        queryset=ProviderNetwork.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = CircuitTermination
        fields = [
            'circuit', 'term_side', 'site', 'provider_network', 'port_speed', 'upstream_speed', 'xconnect_id',
            'pp_info', 'description',
        ]
