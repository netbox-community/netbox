from core.models import ObjectType
from extras.models import CustomLink
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import ChangeLogMessageSerializer, ValidatedModelSerializer

__all__ = (
    'CustomLinkSerializer',
)


class CustomLinkSerializer(ChangeLogMessageSerializer, ValidatedModelSerializer):
    object_types = ContentTypeField(
        queryset=ObjectType.objects.with_feature('custom_links'),
        many=True
    )

    class Meta:
        model = CustomLink
        fields = [
            'id', 'url', 'display_url', 'display', 'object_types', 'name', 'enabled', 'link_text', 'link_url',
            'weight', 'group_name', 'button_class', 'new_window', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name')
