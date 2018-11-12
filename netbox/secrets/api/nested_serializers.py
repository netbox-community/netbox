from rest_framework import serializers

from secrets.models import SecretRole
from utilities.api import WritableNestedSerializer

__all__ = [
    'NestedSecretRoleSerializer'
]


class NestedSecretRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='secrets-api:secretrole-detail')

    class Meta:
        model = SecretRole
        fields = ['id', 'url', 'name', 'slug']
