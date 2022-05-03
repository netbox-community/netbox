from circuits.choices import CircuitStatusChoices
from circuits.models import *
from netbox.forms import NetBoxModelCSVForm
from tenancy.models import Tenant
from utilities.forms import CSVChoiceField, CSVModelChoiceField, SlugField

__all__ = (
    'CircuitCSVForm',
    'CircuitTypeCSVForm',
    'ProviderCSVForm',
    'ProviderNetworkCSVForm',
)


class ProviderCSVForm(NetBoxModelCSVForm):
    slug = SlugField()

    class Meta:
        model = Provider
        fields = (
            'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
        )


class ProviderNetworkCSVForm(NetBoxModelCSVForm):
    provider = CSVModelChoiceField(
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text='Assigned provider'
    )

    class Meta:
        model = ProviderNetwork
        fields = [
            'provider', 'name', 'service_id', 'description', 'comments',
        ]


class CircuitTypeCSVForm(NetBoxModelCSVForm):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = ('name', 'slug', 'description')
        help_texts = {
            'name': 'Name of circuit type',
        }


class CircuitCSVForm(NetBoxModelCSVForm):
    provider = CSVModelChoiceField(
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text='Assigned provider'
    )
    type = CSVModelChoiceField(
        queryset=CircuitType.objects.all(),
        to_field_name='name',
        help_text='Type of circuit'
    )
    status = CSVChoiceField(
        choices=CircuitStatusChoices,
        help_text='Operational status'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = Circuit
        fields = [
            'cid', 'provider', 'type', 'status', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
        ]
