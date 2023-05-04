from django.utils.translation import gettext as _

from circuits.choices import CircuitCommitRateChoices, CircuitTerminationPortSpeedChoices
from circuits.models import *
from dcim.models import Site
from ipam.models import ASN
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, SlugField
from utilities.forms.widgets import DatePicker, NumberWithOptions

__all__ = (
    'CircuitForm',
    'CircuitTerminationForm',
    'CircuitTypeForm',
    'ProviderForm',
    'ProviderAccountForm',
    'ProviderNetworkForm',
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
        ('Provider', ('name', 'slug', 'asns', 'description', 'tags')),
    )

    class Meta:
        model = Provider
        fields = [
            'name', 'slug', 'asns', 'description', 'comments', 'tags',
        ]


class ProviderAccountForm(NetBoxModelForm):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all()
    )
    comments = CommentField()

    class Meta:
        model = ProviderAccount
        fields = [
            'provider', 'name', 'account', 'description', 'comments', 'tags',
        ]


class ProviderNetworkForm(NetBoxModelForm):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all()
    )
    comments = CommentField()

    fieldsets = (
        ('Provider Network', ('provider', 'name', 'service_id', 'description', 'tags')),
    )

    class Meta:
        model = ProviderNetwork
        fields = [
            'provider', 'name', 'service_id', 'description', 'comments', 'tags',
        ]


class CircuitTypeForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        ('Circuit Type', (
            'name', 'slug', 'description', 'tags',
        )),
    )

    class Meta:
        model = CircuitType
        fields = [
            'name', 'slug', 'description', 'tags',
        ]


class CircuitForm(TenancyForm, NetBoxModelForm):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        selector=True
    )
    provider_account = DynamicModelChoiceField(
        queryset=ProviderAccount.objects.all(),
        required=False,
        query_params={
            'provider_id': '$provider',
        }
    )
    type = DynamicModelChoiceField(
        queryset=CircuitType.objects.all()
    )
    comments = CommentField()

    fieldsets = (
        ('Circuit', ('provider', 'provider_account', 'cid', 'type', 'status', 'description', 'tags')),
        ('Service Parameters', ('install_date', 'termination_date', 'commit_rate')),
        ('Tenancy', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Circuit
        fields = [
            'cid', 'type', 'provider', 'provider_account', 'status', 'install_date', 'termination_date', 'commit_rate',
            'description', 'tenant_group', 'tenant', 'comments', 'tags',
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
        queryset=Circuit.objects.all(),
        selector=True
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        selector=True
    )
    provider_network = DynamicModelChoiceField(
        queryset=ProviderNetwork.objects.all(),
        required=False,
        selector=True
    )

    class Meta:
        model = CircuitTermination
        fields = [
            'circuit', 'term_side', 'site', 'provider_network', 'mark_connected', 'port_speed', 'upstream_speed',
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
