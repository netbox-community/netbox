from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import ValidatedModelSerializer
from users.models import Group, Owner, User
from .users import GroupSerializer, UserSerializer

__all__ = (
    'OwnerSerializer',
)


class OwnerSerializer(ValidatedModelSerializer):
    groups = SerializedPKRelatedField(
        queryset=Group.objects.all(),
        serializer=GroupSerializer,
        nested=True,
        required=False,
        many=True
    )
    users = SerializedPKRelatedField(
        queryset=User.objects.all(),
        serializer=UserSerializer,
        nested=True,
        required=False,
        many=True
    )

    class Meta:
        model = Owner
        fields = ('id', 'url', 'display_url', 'display', 'name', 'description', 'groups', 'users')
        brief_fields = ('id', 'url', 'display', 'name', 'description')
