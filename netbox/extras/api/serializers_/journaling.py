from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from extras.choices import *
from extras.models import JournalEntry
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from users.models import User
from utilities.api import get_serializer_for_model

__all__ = (
    'JournalEntrySerializer',
)


class JournalEntrySerializer(NetBoxModelSerializer):
    assigned_object_type = ContentTypeField(
        queryset=ObjectType.objects.all()
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        queryset=User.objects.all(),
        required=False,
        default=serializers.CurrentUserDefault()
    )
    kind = ChoiceField(
        choices=JournalEntryKindChoices,
        required=False
    )

    class Meta:
        model = JournalEntry
        fields = [
            'id', 'url', 'display_url', 'display', 'assigned_object_type', 'assigned_object_id', 'assigned_object',
            'created', 'created_by', 'kind', 'comments', 'tags', 'custom_fields', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'created')

    def validate(self, data):

        # Validate that the parent object exists
        if not self.nested and 'assigned_object_type' in data and 'assigned_object_id' in data:
            try:
                data['assigned_object_type'].get_object_for_this_type(id=data['assigned_object_id'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Invalid assigned_object: {data['assigned_object_type']} ID {data['assigned_object_id']}"
                )

        return super().validate(data)

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_assigned_object(self, instance):
        serializer = get_serializer_for_model(instance.assigned_object_type.model_class())
        context = {'request': self.context['request']}
        return serializer(instance.assigned_object, nested=True, context=context).data
