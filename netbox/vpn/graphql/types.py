from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from netbox.graphql.types import ObjectType, OrganizationalObjectType, NetBoxObjectType
from vpn import filtersets, models

__all__ = (
    'IPSecProfileType',
    'TunnelTerminationType',
    'TunnelType',
)


class TunnelTerminationType(CustomFieldsMixin, TagsMixin, ObjectType):

    class Meta:
        model = models.TunnelTermination
        fields = '__all__'
        filterset_class = filtersets.TunnelTerminationFilterSet


class TunnelType(NetBoxObjectType):

    class Meta:
        model = models.Tunnel
        fields = '__all__'
        filterset_class = filtersets.TunnelFilterSet


class IPSecProfileType(OrganizationalObjectType):

    class Meta:
        model = models.IPSecProfile
        fields = '__all__'
        filterset_class = filtersets.IPSecProfileFilterSet
