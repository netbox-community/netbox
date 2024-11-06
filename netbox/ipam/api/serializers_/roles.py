from ipam.models import Role
from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer

__all__ = (
    'RoleSerializer',
)


class RoleSerializer(NetBoxModelSerializer):

    # Related object counts
    prefix_count = RelatedObjectCountField('prefixes')
    vlan_count = RelatedObjectCountField('vlans')

    class Meta:
        model = Role
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'weight', 'description', 'tags', 'custom_fields',
            'created', 'last_updated', 'prefix_count', 'vlan_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'prefix_count', 'vlan_count')
