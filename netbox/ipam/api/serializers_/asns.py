from rest_framework import serializers

from ipam.models import ASN, ASNRange, RIR
from netbox.api.fields import RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

__all__ = (
    'ASNRangeSerializer',
    'ASNSerializer',
    'AvailableASNSerializer',
    'RIRSerializer',
)


class RIRSerializer(NetBoxModelSerializer):

    # Related object counts
    aggregate_count = RelatedObjectCountField('aggregates')

    class Meta:
        model = RIR
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'is_private', 'description', 'tags',
            'custom_fields', 'created', 'last_updated', 'aggregate_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'aggregate_count')


class ASNRangeSerializer(NetBoxModelSerializer):
    rir = RIRSerializer(nested=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    asn_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ASNRange
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'rir', 'start', 'end', 'tenant', 'description',
            'tags', 'custom_fields', 'created', 'last_updated', 'asn_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class ASNSerializer(NetBoxModelSerializer):
    rir = RIRSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    # Related object counts
    site_count = RelatedObjectCountField('sites')
    provider_count = RelatedObjectCountField('providers')

    class Meta:
        model = ASN
        fields = [
            'id', 'url', 'display_url', 'display', 'asn', 'rir', 'tenant', 'description', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'site_count', 'provider_count',
        ]
        brief_fields = ('id', 'url', 'display', 'asn', 'description')


class AvailableASNSerializer(serializers.Serializer):
    """
    Representation of an ASN which does not exist in the database.
    """
    asn = serializers.IntegerField(read_only=True)
    description = serializers.CharField(required=False)

    def to_representation(self, asn):
        rir = RIRSerializer(self.context['range'].rir, nested=True, context={
            'request': self.context['request']
        }).data
        return {
            'rir': rir,
            'asn': asn,
        }
