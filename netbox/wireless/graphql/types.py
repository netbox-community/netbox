from wireless import filtersets, models
from netbox.graphql.types import ObjectType

__all__ = (
    'WirelessLANType',
    'WirelessLANGroupType',
    'WirelessLinkType',
)


class WirelessLANGroupType(ObjectType):

    class Meta:
        model = models.WirelessLANGroup
        fields = '__all__'
        filterset_class = filtersets.WirelessLANGroupFilterSet


class WirelessLANType(ObjectType):

    class Meta:
        model = models.WirelessLAN
        fields = '__all__'
        filterset_class = filtersets.WirelessLANFilterSet


class WirelessLinkType(ObjectType):

    class Meta:
        model = models.WirelessLink
        fields = '__all__'
        filterset_class = filtersets.WirelessLinkFilterSet
