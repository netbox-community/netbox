from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from dcim.api.serializers import NestedDeviceSerializer
from secrets.models import Secret, SecretRole
from utilities.api import ValidatedModelSerializer


#
# SecretRoles
#

class SecretRoleSerializer(ValidatedModelSerializer):

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


class WritableSecretSerializer(serializers.ModelSerializer):
    plaintext = serializers.CharField()

    class Meta:
        model = Secret
        fields = ['id', 'device', 'role', 'name', 'plaintext']
        validators = []

    def validate(self, data):

        # Validate uniqueness of name if one has been provided.
        if data.get('name', None):
            validator = UniqueTogetherValidator(queryset=Secret.objects.all(), fields=('device', 'role', 'name'))
            validator.set_context(self)
            validator(data)

        # Enforce model validation
        super(WritableSecretSerializer, self).validate(data)

        return data
