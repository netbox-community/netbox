from core.models import ObjectType
from extras.models import TableConfig
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import ValidatedModelSerializer

__all__ = (
    'TableConfigSerializer',
)


class TableConfigSerializer(ValidatedModelSerializer):
    object_type = ContentTypeField(
        queryset=ObjectType.objects.all()
    )

    class Meta:
        model = TableConfig
        fields = [
            'id', 'url', 'display_url', 'display', 'object_type', 'table', 'name', 'description', 'user', 'weight',
            'enabled', 'shared', 'columns', 'ordering', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description', 'object_type', 'table')
