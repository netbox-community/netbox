from circuits.models import ProviderAccount
from netbox.api.serializers import WritableNestedSerializer

__all__ = (
    'NestedProviderAccountSerializer',
)


class NestedProviderAccountSerializer(WritableNestedSerializer):

    class Meta:
        model = ProviderAccount
        fields = ['id', 'url', 'display_url', 'display', 'name', 'account']
