import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from dcim.models import Interface
from ipam.models import IPAddress
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from virtualization.models import VMInterface
from .choices import *
from .models import *

__all__ = (
    'IPSecProfileFilterSet',
    'TunnelFilterSet',
    'TunnelTerminationFilterSet',
)


class TunnelFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    status = django_filters.MultipleChoiceFilter(
        choices=TunnelStatusChoices
    )
    encapsulation = django_filters.MultipleChoiceFilter(
        choices=TunnelEncapsulationChoices
    )
    ipsec_profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPSecProfile.objects.all(),
        label=_('IPSec profile (ID)'),
    )
    ipsec_profile = django_filters.ModelMultipleChoiceFilter(
        field_name='ipsec_profile__name',
        queryset=IPSecProfile.objects.all(),
        to_field_name='name',
        label=_('IPSec profile (name)'),
    )

    class Meta:
        model = Tunnel
        fields = ['id', 'name', 'preshared_key', 'tunnel_id']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class TunnelTerminationFilterSet(NetBoxModelFilterSet):
    tunnel_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tunnel',
        queryset=Tunnel.objects.all(),
        label=_('Tunnel (ID)'),
    )
    tunnel = django_filters.ModelMultipleChoiceFilter(
        field_name='tunnel__name',
        queryset=IPSecProfile.objects.all(),
        to_field_name='name',
        label=_('Tunnel (name)'),
    )
    role = django_filters.MultipleChoiceFilter(
        choices=TunnelTerminationRoleChoices
    )
    # interface = django_filters.ModelMultipleChoiceFilter(
    #     field_name='interface__name',
    #     queryset=Interface.objects.all(),
    #     to_field_name='name',
    #     label=_('Interface (name)'),
    # )
    # interface_id = django_filters.ModelMultipleChoiceFilter(
    #     field_name='interface',
    #     queryset=Interface.objects.all(),
    #     label=_('Interface (ID)'),
    # )
    # vminterface = django_filters.ModelMultipleChoiceFilter(
    #     field_name='interface__name',
    #     queryset=VMInterface.objects.all(),
    #     to_field_name='name',
    #     label=_('VM interface (name)'),
    # )
    # vminterface_id = django_filters.ModelMultipleChoiceFilter(
    #     field_name='vminterface',
    #     queryset=VMInterface.objects.all(),
    #     label=_('VM interface (ID)'),
    # )
    outside_ip_id = django_filters.ModelMultipleChoiceFilter(
        field_name='outside_ip',
        queryset=IPAddress.objects.all(),
        label=_('Outside IP (ID)'),
    )

    class Meta:
        model = TunnelTermination
        fields = ['id']


class IPSecProfileFilterSet(NetBoxModelFilterSet):
    protocol = django_filters.MultipleChoiceFilter(
        choices=IPSecProtocolChoices
    )
    ike_version = django_filters.MultipleChoiceFilter(
        choices=IKEVersionChoices
    )
    phase1_encryption = django_filters.MultipleChoiceFilter(
        choices=EncryptionChoices
    )
    phase1_authentication = django_filters.MultipleChoiceFilter(
        choices=AuthenticationChoices
    )
    phase1_group = django_filters.MultipleChoiceFilter(
        choices=DHGroupChoices
    )
    phase2_encryption = django_filters.MultipleChoiceFilter(
        choices=EncryptionChoices
    )
    phase2_authentication = django_filters.MultipleChoiceFilter(
        choices=AuthenticationChoices
    )
    phase2_group = django_filters.MultipleChoiceFilter(
        choices=DHGroupChoices
    )

    class Meta:
        model = IPSecProfile
        fields = ['id', 'name', 'phase1_sa_lifetime', 'phase2_sa_lifetime']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )
