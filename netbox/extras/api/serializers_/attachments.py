from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ContentType
from extras.models import ImageAttachment
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import ValidatedModelSerializer
from utilities.api import get_serializer_for_model

__all__ = (
    'ImageAttachmentSerializer',
)


class ImageAttachmentSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:imageattachment-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ImageAttachment
        fields = [
            'id', 'url', 'display', 'content_type', 'object_id', 'parent', 'name', 'image', 'image_height',
            'image_width', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'image')

    def validate(self, data):

        # Validate that the parent object exists
        try:
            data['content_type'].get_object_for_this_type(id=data['object_id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Invalid parent object: {} ID {}".format(data['content_type'], data['object_id'])
            )

        # Enforce model validation
        super().validate(data)

        return data

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_parent(self, obj):
        serializer = get_serializer_for_model(obj.parent)
        context = {'request': self.context['request']}
        return serializer(obj.parent, nested=True, context=context).data
