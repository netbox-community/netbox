from wireless import filtersets, models
from netbox.graphql.types import ObjectType

__all__ = (
    'WirelessLANType',
)


class WirelessLANType(ObjectType):

    class Meta:
        model = models.WirelessLAN
        fields = '__all__'
        filterset_class = filtersets.WirelessLANFilterSet
