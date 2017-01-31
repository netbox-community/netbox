from rest_framework import serializers

from dcim.api.serializers import NestedDeviceSerializer
from secrets.models import Secret, SecretRole


#
# SecretRoles
#

class SecretRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = SecretRole
        fields = ['id', 'name', 'slug']


class NestedSecretRoleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='secrets-api:secretrole-detail')

    class Meta:
        model = SecretRole
        fields = ['id', 'url', 'name', 'slug']


#
# Secrets
#

class SecretSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    role = NestedSecretRoleSerializer()

    class Meta:
        model = Secret
        fields = ['id', 'device', 'role', 'name', 'plaintext', 'hash', 'created', 'last_updated']
