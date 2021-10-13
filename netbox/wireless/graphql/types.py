from wireless import filtersets, models
from netbox.graphql.types import ObjectType

__all__ = (
    'WirelessLANType',
    'WirelessLinkType',
)


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
