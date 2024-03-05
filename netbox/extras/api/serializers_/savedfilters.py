from rest_framework import serializers

from core.models import ContentType
from extras.models import SavedFilter
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import ValidatedModelSerializer

__all__ = (
    'SavedFilterSerializer',
)


class SavedFilterSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:savedfilter-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.all(),
        many=True
    )

    class Meta:
        model = SavedFilter
        fields = [
            'id', 'url', 'display', 'content_types', 'name', 'slug', 'description', 'user', 'weight', 'enabled',
            'shared', 'parameters', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description')
