from rest_framework import serializers

from ipam.models import Role
from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer

__all__ = (
    'RoleSerializer',
)


class RoleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:role-detail')

    # Related object counts
    prefix_count = RelatedObjectCountField('prefixes')
    vlan_count = RelatedObjectCountField('vlans')

    class Meta:
        model = Role
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'weight', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'prefix_count', 'vlan_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'prefix_count', 'vlan_count')
