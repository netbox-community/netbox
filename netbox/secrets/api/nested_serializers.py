from rest_framework import serializers

from netbox.api import WritableNestedSerializer
from secrets.models import Secret, SecretRole

__all__ = [
    'NestedSecretRoleSerializer',
    'NestedSecretSerializer',
]


class NestedSecretSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='secrets-api:secret-detail')

    class Meta:
        model = Secret
        fields = ['id', 'url', 'name']


class NestedSecretRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='secrets-api:secretrole-detail')
    secret_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SecretRole
        fields = ['id', 'url', 'name', 'slug', 'secret_count']
