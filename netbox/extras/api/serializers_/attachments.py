from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from core.models import ObjectType
from extras.models import ImageAttachment
from netbox.api.fields import ContentTypeField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import ValidatedModelSerializer

__all__ = (
    'ImageAttachmentSerializer',
)


class ImageAttachmentSerializer(ValidatedModelSerializer):
    object_type = ContentTypeField(
        queryset=ObjectType.objects.all()
    )
    parent = GFKSerializerField(read_only=True)
    image_width = serializers.IntegerField(read_only=True)
    image_height = serializers.IntegerField(read_only=True)

    class Meta:
        model = ImageAttachment
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'parent', 'name', 'image', 'description',
            'image_height', 'image_width', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'image', 'description')

    def validate(self, data):

        # Validate that the parent object exists
        try:
            data['object_type'].get_object_for_this_type(id=data['object_id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Invalid parent object: {} ID {}".format(data['object_type'], data['object_id'])
            )

        # Enforce model validation
        super().validate(data)

        return data
