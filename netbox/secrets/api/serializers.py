from rest_framework import serializers

from dcim.api.nested_serializers import NestedDeviceSerializer
from extras.api.customfields import CustomFieldModelSerializer
from extras.api.serializers import TaggedObjectSerializer
from secrets.models import Secret, SecretRole
from utilities.api import ValidatedModelSerializer
from .nested_serializers import *


#
# Secrets
#

class SecretRoleSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='secrets-api:secretrole-detail')
    secret_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SecretRole
        fields = ['id', 'url', 'name', 'slug', 'description', 'secret_count']


class SecretSerializer(TaggedObjectSerializer, CustomFieldModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='secrets-api:secret-detail')
    device = NestedDeviceSerializer()
    role = NestedSecretRoleSerializer()
    plaintext = serializers.CharField()

    class Meta:
        model = Secret
        fields = [
            'id', 'url', 'device', 'role', 'name', 'plaintext', 'hash', 'tags', 'custom_fields', 'created',
            'last_updated',
        ]
        validators = []

    def validate(self, data):

        # Encrypt plaintext data using the master key provided from the view context
        if data.get('plaintext'):
            s = Secret(plaintext=data['plaintext'])
            s.encrypt(self.context['master_key'])
            data['ciphertext'] = s.ciphertext
            data['hash'] = s.hash

        super().validate(data)

        return data
