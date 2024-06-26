from rest_framework import serializers

from circuits.models import Provider, ProviderAccount, ProviderNetwork
from ipam.api.serializers_.asns import ASNSerializer
from ipam.models import ASN
from netbox.api.fields import RelatedObjectCountField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from ..nested_serializers import *

__all__ = (
    'ProviderAccountSerializer',
    'ProviderNetworkSerializer',
    'ProviderSerializer',
)


class ProviderSerializer(NetBoxModelSerializer):
    accounts = SerializedPKRelatedField(
        queryset=ProviderAccount.objects.all(),
        serializer=NestedProviderAccountSerializer,
        required=False,
        many=True
    )
    asns = SerializedPKRelatedField(
        queryset=ASN.objects.all(),
        serializer=ASNSerializer,
        nested=True,
        required=False,
        many=True
    )

    # Related object counts
    circuit_count = RelatedObjectCountField('circuits')

    class Meta:
        model = Provider
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'accounts', 'description', 'comments',
            'asns', 'tags', 'custom_fields', 'created', 'last_updated', 'circuit_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'circuit_count')


class ProviderAccountSerializer(NetBoxModelSerializer):
    provider = ProviderSerializer(nested=True)
    name = serializers.CharField(allow_blank=True, max_length=100, required=False, default='')

    class Meta:
        model = ProviderAccount
        fields = [
            'id', 'url', 'display_url', 'display', 'provider', 'name', 'account', 'description', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'account', 'description')


class ProviderNetworkSerializer(NetBoxModelSerializer):
    provider = ProviderSerializer(nested=True)

    class Meta:
        model = ProviderNetwork
        fields = [
            'id', 'url', 'display_url', 'display', 'provider', 'name', 'service_id', 'description', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
