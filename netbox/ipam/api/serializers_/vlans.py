from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.api.serializers_.sites import SiteSerializer
from ipam.choices import *
from ipam.constants import VLANGROUP_SCOPE_TYPES
from ipam.models import VLAN, VLANGroup, VLANTranslationPolicy, VLANTranslationRule
from netbox.api.fields import ChoiceField, ContentTypeField, IntegerRangeSerializer, RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from utilities.api import get_serializer_for_model
from vpn.api.serializers_.l2vpn import L2VPNTerminationSerializer
from .nested import NestedVLANSerializer
from .roles import RoleSerializer

__all__ = (
    'AvailableVLANSerializer',
    'CreateAvailableVLANSerializer',
    'VLANGroupSerializer',
    'VLANSerializer',
    'VLANTranslationPolicySerializer',
    'VLANTranslationRuleSerializer',
)


class VLANGroupSerializer(NetBoxModelSerializer):
    scope_type = ContentTypeField(
        queryset=ContentType.objects.filter(
            model__in=VLANGROUP_SCOPE_TYPES
        ),
        allow_null=True,
        required=False,
        default=None
    )
    scope_id = serializers.IntegerField(allow_null=True, required=False, default=None)
    scope = serializers.SerializerMethodField(read_only=True)
    vid_ranges = IntegerRangeSerializer(many=True, required=False)
    utilization = serializers.CharField(read_only=True)

    # Related object counts
    vlan_count = RelatedObjectCountField('vlans')

    class Meta:
        model = VLANGroup
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'scope_type', 'scope_id', 'scope', 'vid_ranges',
            'description', 'tags', 'custom_fields', 'created', 'last_updated', 'vlan_count', 'utilization'
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'vlan_count')
        validators = []

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_scope(self, obj):
        if obj.scope_id is None:
            return None
        serializer = get_serializer_for_model(obj.scope)
        context = {'request': self.context['request']}
        return serializer(obj.scope, nested=True, context=context).data


class VLANSerializer(NetBoxModelSerializer):
    site = SiteSerializer(nested=True, required=False, allow_null=True)
    group = VLANGroupSerializer(nested=True, required=False, allow_null=True, default=None)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    status = ChoiceField(choices=VLANStatusChoices, required=False)
    role = RoleSerializer(nested=True, required=False, allow_null=True)
    qinq_role = ChoiceField(choices=VLANQinQRoleChoices, required=False)
    qinq_svlan = NestedVLANSerializer(required=False, allow_null=True, default=None)
    l2vpn_termination = L2VPNTerminationSerializer(nested=True, read_only=True, allow_null=True)

    # Related object counts
    prefix_count = RelatedObjectCountField('prefixes')

    class Meta:
        model = VLAN
        fields = [
            'id', 'url', 'display_url', 'display', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role',
            'description', 'qinq_role', 'qinq_svlan', 'comments', 'l2vpn_termination', 'tags', 'custom_fields',
            'created', 'last_updated', 'prefix_count',
        ]
        brief_fields = ('id', 'url', 'display', 'vid', 'name', 'description')


class AvailableVLANSerializer(serializers.Serializer):
    """
    Representation of a VLAN which does not exist in the database.
    """
    vid = serializers.IntegerField(read_only=True)
    group = VLANGroupSerializer(nested=True, read_only=True, allow_null=True)

    def to_representation(self, instance):
        return {
            'vid': instance,
            'group': VLANGroupSerializer(
                self.context['group'],
                nested=True,
                context={'request': self.context['request']}
            ).data,
        }


class CreateAvailableVLANSerializer(NetBoxModelSerializer):
    site = SiteSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    status = ChoiceField(choices=VLANStatusChoices, required=False)
    role = RoleSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = VLAN
        fields = [
            'name', 'site', 'tenant', 'status', 'role', 'description', 'tags', 'custom_fields',
        ]

    def validate(self, data):
        # Bypass model validation since we don't have a VID yet
        return data


class VLANTranslationRuleSerializer(NetBoxModelSerializer):

    class Meta:
        model = VLANTranslationRule
        fields = ['id', 'url', 'display', 'policy', 'local_vid', 'remote_vid', 'description']


class VLANTranslationPolicySerializer(NetBoxModelSerializer):
    rules = VLANTranslationRuleSerializer(many=True, read_only=True)

    class Meta:
        model = VLANTranslationPolicy
        fields = ['id', 'url', 'display', 'name', 'description', 'display', 'rules']
        brief_fields = ('id', 'url', 'display', 'name', 'description')
