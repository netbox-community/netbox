from wireless import filtersets, models
from netbox.graphql.types import ObjectType

__all__ = (
    'SSIDType',
)


class SSIDType(ObjectType):

    class Meta:
        model = models.SSID
        fields = '__all__'
        filterset_class = filtersets.SSIDFilterSet
