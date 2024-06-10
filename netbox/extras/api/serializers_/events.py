from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from extras.choices import *
from extras.models import EventRule, Webhook
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from utilities.api import get_serializer_for_model
from .scripts import ScriptSerializer

__all__ = (
    'EventRuleSerializer',
    'WebhookSerializer',
)


#
# Event Rules
#

class EventRuleSerializer(NetBoxModelSerializer):
    object_types = ContentTypeField(
        queryset=ObjectType.objects.with_feature('event_rules'),
        many=True
    )
    action_type = ChoiceField(choices=EventRuleActionChoices)
    action_object_type = ContentTypeField(
        queryset=ObjectType.objects.with_feature('event_rules'),
    )
    action_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EventRule
        fields = [
            'id', 'url', 'display_url', 'display', 'object_types', 'name', 'type_create', 'type_update', 'type_delete',
            'type_job_start', 'type_job_end', 'enabled', 'conditions', 'action_type', 'action_object_type',
            'action_object_id', 'action_object', 'description', 'custom_fields', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_action_object(self, instance):
        context = {'request': self.context['request']}
        # We need to manually instantiate the serializer for scripts
        if instance.action_type == EventRuleActionChoices.SCRIPT:
            script = instance.action_object
            return ScriptSerializer(script, nested=True, context=context).data
        else:
            serializer = get_serializer_for_model(instance.action_object_type.model_class())
            return serializer(instance.action_object, nested=True, context=context).data


#
# Webhooks
#

class WebhookSerializer(NetBoxModelSerializer):

    class Meta:
        model = Webhook
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'description', 'payload_url', 'http_method',
            'http_content_type', 'additional_headers', 'body_template', 'secret', 'ssl_verification', 'ca_file_path',
            'custom_fields', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
