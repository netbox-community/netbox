from rest_framework import serializers

from core.models import ContentType
from extras.models import CustomLink
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import ValidatedModelSerializer

__all__ = (
    'CustomLinkSerializer',
)


class CustomLinkSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customlink-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.with_feature('custom_links'),
        many=True
    )

    class Meta:
        model = CustomLink
        fields = [
            'id', 'url', 'display', 'content_types', 'name', 'enabled', 'link_text', 'link_url', 'weight', 'group_name',
            'button_class', 'new_window', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name')
