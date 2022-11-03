from circuits.choices import CircuitStatusChoices
from circuits.models import *
from django.utils.translation import gettext as _
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
            'name', 'slug', 'account', 'description', 'comments', 'tags',
        )


class ProviderNetworkCSVForm(NetBoxModelCSVForm):
    provider = CSVModelChoiceField(
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text=_('Assigned provider')
    )

    class Meta:
        model = ProviderNetwork
        fields = [
            'provider', 'name', 'service_id', 'description', 'comments', 'tags'
        ]


class CircuitTypeCSVForm(NetBoxModelCSVForm):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = ('name', 'slug', 'description', 'tags')
        help_texts = {
            'name': _('Name of circuit type'),
        }


class CircuitCSVForm(NetBoxModelCSVForm):
    provider = CSVModelChoiceField(
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text=_('Assigned provider')
    )
    type = CSVModelChoiceField(
        queryset=CircuitType.objects.all(),
        to_field_name='name',
        help_text=_('Type of circuit')
    )
    status = CSVChoiceField(
        choices=CircuitStatusChoices,
        help_text=_('Operational status')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = Circuit
        fields = [
            'cid', 'provider', 'type', 'status', 'tenant', 'install_date', 'termination_date', 'commit_rate',
            'description', 'comments', 'tags'
        ]
