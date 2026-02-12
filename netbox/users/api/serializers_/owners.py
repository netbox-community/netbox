from netbox.api.fields import RelatedObjectCountField, SerializedPKRelatedField
from netbox.api.serializers import ValidatedModelSerializer
from users.models import Group, Owner, OwnerGroup, User

from .users import GroupSerializer, UserSerializer

__all__ = (
    'OwnerGroupSerializer',
    'OwnerSerializer',
)


class OwnerGroupSerializer(ValidatedModelSerializer):
    # Related object counts
    member_count = RelatedObjectCountField('members')

    class Meta:
        model = OwnerGroup
        fields = ('id', 'url', 'display_url', 'display', 'name', 'description', 'member_count')
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class OwnerSerializer(ValidatedModelSerializer):
    group = OwnerGroupSerializer(
        nested=True,
        allow_null=True,
    )
    user_groups = SerializedPKRelatedField(
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
        fields = ('id', 'url', 'display_url', 'display', 'name', 'group', 'description', 'user_groups', 'users')
        brief_fields = ('id', 'url', 'display', 'name', 'description')
