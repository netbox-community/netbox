from rest_framework import serializers

from core.models import ObjectType
from extras.choices import *
from extras.models import EventRule, Webhook
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import NetBoxModelSerializer
from netbox.event_rules import get_event_rule_action_choices
from users.api.serializers_.mixins import OwnerMixin

__all__ = (
    'EventRuleSerializer',
    'WebhookSerializer',
)


#
# Event Rules
#

class EventRuleSerializer(OwnerMixin, NetBoxModelSerializer):
    object_types = ContentTypeField(
        queryset=ObjectType.objects.with_feature('event_rules'),
        many=True
    )
    action_type = ChoiceField(choices=[])  # Choices are set by get_fields()
    action_object_type = ContentTypeField(
        queryset=ObjectType.objects.all(),
        required=False,
        allow_null=True,
    )
    action_object = GFKSerializerField(read_only=True)
    action_is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = EventRule
        fields = [
            'id', 'url', 'display_url', 'display', 'object_types', 'name', 'enabled', 'event_types', 'conditions',
            'action_type', 'action_object_type', 'action_object_id', 'action_object', 'action_is_available',
            'description', 'custom_fields', 'owner', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')

    def get_fields(self):
        fields = super().get_fields()

        # Rebuild action_type from the live registry on each instantiation to ensure all registered
        # actions are captured as choices.
        if 'action_type' in fields:
            fields['action_type'] = ChoiceField(choices=get_event_rule_action_choices())

        return fields


#
# Webhooks
#

class WebhookSerializer(OwnerMixin, NetBoxModelSerializer):

    class Meta:
        model = Webhook
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'description', 'payload_url', 'http_method',
            'http_content_type', 'additional_headers', 'body_template', 'secret', 'ssl_verification', 'ca_file_path',
            'timeout', 'custom_fields', 'owner', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
