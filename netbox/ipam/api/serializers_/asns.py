from rest_framework import serializers

from dcim.models import Site
from ipam.models import ASN, RIR, ASNRange
from netbox.api.fields import RelatedObjectCountField, SerializedPKRelatedField
from netbox.api.serializers import OrganizationalModelSerializer, PrimaryModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

__all__ = (
    'ASNRangeSerializer',
    'ASNSerializer',
    'ASNSiteSerializer',
    'AvailableASNSerializer',
    'RIRSerializer',
)


class RIRSerializer(OrganizationalModelSerializer):

    # Related object counts
    aggregate_count = RelatedObjectCountField('aggregates')

    class Meta:
        model = RIR
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'is_private', 'description', 'owner', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated', 'aggregate_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'aggregate_count')


class ASNRangeSerializer(OrganizationalModelSerializer):
    rir = RIRSerializer(nested=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    asn_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ASNRange
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'rir', 'start', 'end', 'tenant', 'description',
            'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'asn_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class ASNSiteSerializer(PrimaryModelSerializer):
    """
    This serializer is meant for inclusion in ASNSerializer and is only used
    to avoid a circular import of SiteSerializer.
    """
    class Meta:
        model = Site
        fields = ('id', 'url', 'display', 'name', 'description', 'slug')
        brief_fields = ('id', 'url', 'display', 'name', 'description', 'slug')


class ASNSerializer(PrimaryModelSerializer):
    rir = RIRSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    sites = SerializedPKRelatedField(
        queryset=Site.objects.all(),
        serializer=ASNSiteSerializer,
        nested=True,
        required=False,
        many=True
    )

    # Related object counts
    site_count = RelatedObjectCountField('sites')
    provider_count = RelatedObjectCountField('providers')

    class Meta:
        model = ASN
        fields = [
            'id', 'url', 'display_url', 'display', 'asn', 'rir', 'tenant', 'description', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'site_count', 'provider_count', 'sites',
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
