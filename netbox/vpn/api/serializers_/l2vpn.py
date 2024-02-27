from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ipam.api.nested_serializers import NestedRouteTargetSerializer
from ipam.models import RouteTarget
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from netbox.constants import NESTED_SERIALIZER_PREFIX
from tenancy.api.serializers_.tenants import TenantSerializer
from utilities.api import get_serializer_for_model
from vpn.choices import *
from vpn.models import L2VPN, L2VPNTermination

__all__ = (
    'L2VPNSerializer',
    'L2VPNTerminationSerializer',
)


class L2VPNSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vpn-api:l2vpn-detail')
    type = ChoiceField(choices=L2VPNTypeChoices, required=False)
    import_targets = SerializedPKRelatedField(
        queryset=RouteTarget.objects.all(),
        serializer=NestedRouteTargetSerializer,
        required=False,
        many=True
    )
    export_targets = SerializedPKRelatedField(
        queryset=RouteTarget.objects.all(),
        serializer=NestedRouteTargetSerializer,
        required=False,
        many=True
    )
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = L2VPN
        fields = [
            'id', 'url', 'display', 'identifier', 'name', 'slug', 'type', 'import_targets', 'export_targets',
            'description', 'comments', 'tenant', 'tags', 'custom_fields', 'created', 'last_updated'
        ]
        brief_fields = ('id', 'url', 'display', 'identifier', 'name', 'slug', 'type', 'description')


class L2VPNTerminationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vpn-api:l2vpntermination-detail')
    l2vpn = L2VPNSerializer(
        nested=True
    )
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = L2VPNTermination
        fields = [
            'id', 'url', 'display', 'l2vpn', 'assigned_object_type', 'assigned_object_id',
            'assigned_object', 'tags', 'custom_fields', 'created', 'last_updated'
        ]
        brief_fields = ('id', 'url', 'display', 'l2vpn')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_assigned_object(self, instance):
        serializer = get_serializer_for_model(instance.assigned_object, prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(instance.assigned_object, context=context).data
