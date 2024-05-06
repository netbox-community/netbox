from django.contrib.contenttypes.models import ContentType
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.choices import *
from dcim.constants import *
from dcim.models import Cable, CablePath, CableTermination
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import GenericObjectSerializer, NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from utilities.api import get_serializer_for_model

__all__ = (
    'CablePathSerializer',
    'CableSerializer',
    'CableTerminationSerializer',
    'CabledObjectSerializer',
    'TracedCableSerializer',
)


class CableSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')
    a_terminations = GenericObjectSerializer(many=True, required=False)
    b_terminations = GenericObjectSerializer(many=True, required=False)
    status = ChoiceField(choices=LinkStatusChoices, required=False)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    length_unit = ChoiceField(choices=CableLengthUnitChoices, allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = Cable
        fields = [
            'id', 'url', 'display', 'type', 'a_terminations', 'b_terminations', 'status', 'tenant', 'label', 'color',
            'length', 'length_unit', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'label', 'description')


class TracedCableSerializer(serializers.ModelSerializer):
    """
    Used only while tracing a cable path.
    """
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')

    class Meta:
        model = Cable
        fields = [
            'id', 'url', 'type', 'status', 'label', 'color', 'length', 'length_unit', 'description',
        ]


class CableTerminationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cabletermination-detail')
    termination_type = ContentTypeField(
        queryset=ContentType.objects.filter(CABLE_TERMINATION_MODELS)
    )
    termination = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CableTermination
        fields = [
            'id', 'url', 'display', 'cable', 'cable_end', 'termination_type', 'termination_id', 'termination',
            'created', 'last_updated',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_termination(self, obj):
        serializer = get_serializer_for_model(obj.termination)
        context = {'request': self.context['request']}
        return serializer(obj.termination, nested=True, context=context).data


class CablePathSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CablePath
        fields = ['id', 'path', 'is_active', 'is_complete', 'is_split']

    @extend_schema_field(serializers.ListField)
    def get_path(self, obj):
        ret = []
        for nodes in obj.path_objects:
            serializer = get_serializer_for_model(nodes[0])
            context = {'request': self.context['request']}
            ret.append(serializer(nodes, nested=True, many=True, context=context).data)
        return ret


class CabledObjectSerializer(serializers.ModelSerializer):
    cable = CableSerializer(nested=True, read_only=True, allow_null=True)
    cable_end = serializers.CharField(read_only=True)
    link_peers_type = serializers.SerializerMethodField(read_only=True)
    link_peers = serializers.SerializerMethodField(read_only=True)
    _occupied = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_link_peers_type(self, obj):
        """
        Return the type of the peer link terminations, or None.
        """
        if not obj.cable:
            return None

        if obj.link_peers:
            return f'{obj.link_peers[0]._meta.app_label}.{obj.link_peers[0]._meta.model_name}'

        return None

    @extend_schema_field(serializers.ListField)
    def get_link_peers(self, obj):
        """
        Return the appropriate serializer for the link termination model.
        """
        if not obj.link_peers:
            return []

        # Return serialized peer termination objects
        serializer = get_serializer_for_model(obj.link_peers[0])
        context = {'request': self.context['request']}
        return serializer(obj.link_peers, nested=True, many=True, context=context).data

    @extend_schema_field(serializers.BooleanField)
    def get__occupied(self, obj):
        return obj._occupied
