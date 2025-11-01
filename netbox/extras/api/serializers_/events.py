from core.models import ObjectType
from extras.choices import *
from extras.models import EventRule, Webhook
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import NetBoxModelSerializer
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
    action_type = ChoiceField(choices=EventRuleActionChoices)
    action_object_type = ContentTypeField(
        queryset=ObjectType.objects.with_feature('event_rules'),
    )
    action_object = GFKSerializerField(read_only=True)

    class Meta:
        model = EventRule
        fields = [
            'id', 'url', 'display_url', 'display', 'object_types', 'name', 'enabled', 'event_types', 'conditions',
            'action_type', 'action_object_type', 'action_object_id', 'action_object', 'description', 'custom_fields',
            'owner', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


#
# Webhooks
#

class WebhookSerializer(OwnerMixin, NetBoxModelSerializer):

    class Meta:
        model = Webhook
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'description', 'payload_url', 'http_method',
            'http_content_type', 'additional_headers', 'body_template', 'secret', 'ssl_verification', 'ca_file_path',
            'custom_fields', 'owner', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
