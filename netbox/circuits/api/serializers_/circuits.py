from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from circuits.choices import CircuitPriorityChoices, CircuitStatusChoices
from circuits.constants import CIRCUIT_TERMINATION_TERMINATION_TYPES
from circuits.models import Circuit, CircuitGroup, CircuitGroupAssignment, CircuitTermination, CircuitType
from dcim.api.serializers_.cables import CabledObjectSerializer
from netbox.api.fields import ChoiceField, ContentTypeField, RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from netbox.choices import DistanceUnitChoices
from tenancy.api.serializers_.tenants import TenantSerializer
from utilities.api import get_serializer_for_model

from .providers import ProviderAccountSerializer, ProviderNetworkSerializer, ProviderSerializer

__all__ = (
    'CircuitSerializer',
    'CircuitGroupAssignmentSerializer',
    'CircuitGroupSerializer',
    'CircuitTerminationSerializer',
    'CircuitTypeSerializer',
)


class CircuitTypeSerializer(NetBoxModelSerializer):

    # Related object counts
    circuit_count = RelatedObjectCountField('circuits')

    class Meta:
        model = CircuitType
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'color', 'description', 'tags', 'custom_fields',
            'created', 'last_updated', 'circuit_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'circuit_count')


class CircuitCircuitTerminationSerializer(WritableNestedSerializer):
    termination_type = ContentTypeField(
        queryset=ContentType.objects.filter(
            model__in=CIRCUIT_TERMINATION_TERMINATION_TYPES
        ),
        allow_null=True,
        required=False,
        default=None
    )
    termination_id = serializers.IntegerField(allow_null=True, required=False, default=None)
    termination = serializers.SerializerMethodField(read_only=True)
    provider_network = ProviderNetworkSerializer(nested=True, allow_null=True)

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'url', 'display_url', 'display', 'termination_type', 'termination_id', 'termination', 'provider_network', 'port_speed', 'upstream_speed',
            'xconnect_id', 'description',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_termination(self, obj):
        if obj.termination_id is None:
            return None
        serializer = get_serializer_for_model(obj.termination)
        context = {'request': self.context['request']}
        return serializer(obj.termination, nested=True, context=context).data


class CircuitGroupSerializer(NetBoxModelSerializer):
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    circuit_count = RelatedObjectCountField('assignments')

    class Meta:
        model = CircuitGroup
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'description', 'tenant',
            'tags', 'custom_fields', 'created', 'last_updated', 'circuit_count'
        ]
        brief_fields = ('id', 'url', 'display', 'name')


class CircuitGroupAssignmentSerializer_(NetBoxModelSerializer):
    """
    Base serializer for group assignments under CircuitSerializer.
    """
    group = CircuitGroupSerializer(nested=True)
    priority = ChoiceField(choices=CircuitPriorityChoices, allow_blank=True, required=False)

    class Meta:
        model = CircuitGroupAssignment
        fields = [
            'id', 'url', 'display_url', 'display', 'group', 'priority', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'group', 'priority')


class CircuitSerializer(NetBoxModelSerializer):
    provider = ProviderSerializer(nested=True)
    provider_account = ProviderAccountSerializer(nested=True, required=False, allow_null=True, default=None)
    status = ChoiceField(choices=CircuitStatusChoices, required=False)
    type = CircuitTypeSerializer(nested=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    termination_a = CircuitCircuitTerminationSerializer(read_only=True, allow_null=True)
    termination_z = CircuitCircuitTerminationSerializer(read_only=True, allow_null=True)
    assignments = CircuitGroupAssignmentSerializer_(nested=True, many=True, required=False)
    distance_unit = ChoiceField(choices=DistanceUnitChoices, allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = Circuit
        fields = [
            'id', 'url', 'display_url', 'display', 'cid', 'provider', 'provider_account', 'type', 'status', 'tenant',
            'install_date', 'termination_date', 'commit_rate', 'description', 'termination_a', 'termination_z',
            'distance', 'distance_unit', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'assignments',
        ]
        brief_fields = ('id', 'url', 'display', 'provider', 'cid', 'description')


class CircuitTerminationSerializer(NetBoxModelSerializer, CabledObjectSerializer):
    circuit = CircuitSerializer(nested=True)
    termination_type = ContentTypeField(
        queryset=ContentType.objects.filter(
            model__in=CIRCUIT_TERMINATION_TERMINATION_TYPES
        ),
        allow_null=True,
        required=False,
        default=None
    )
    termination_id = serializers.IntegerField(allow_null=True, required=False, default=None)
    termination = serializers.SerializerMethodField(read_only=True)
    provider_network = ProviderNetworkSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = CircuitTermination
        fields = [
            'id', 'url', 'display_url', 'display', 'circuit', 'term_side', 'termination_type', 'termination_id', 'termination', 'provider_network', 'port_speed',
            'upstream_speed', 'xconnect_id', 'pp_info', 'description', 'mark_connected', 'cable', 'cable_end',
            'link_peers', 'link_peers_type', 'tags', 'custom_fields', 'created', 'last_updated', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'circuit', 'term_side', 'description', 'cable', '_occupied')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_termination(self, obj):
        if obj.termination_id is None:
            return None
        serializer = get_serializer_for_model(obj.termination)
        context = {'request': self.context['request']}
        return serializer(obj.termination, nested=True, context=context).data


class CircuitGroupAssignmentSerializer(CircuitGroupAssignmentSerializer_):
    circuit = CircuitSerializer(nested=True)

    class Meta:
        model = CircuitGroupAssignment
        fields = [
            'id', 'url', 'display_url', 'display', 'group', 'circuit', 'priority', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'group', 'circuit', 'priority')
