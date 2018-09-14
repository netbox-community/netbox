from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from dcim.api.serializers import NestedDeviceSerializer
from dcim.models import Device
from extras.api.customfields import CustomFieldModelSerializer
from secrets.models import Secret, SecretRole
from utilities.api import ValidatedModelSerializer, WritableNestedSerializer


#
# SecretRoles
#

class SecretRoleSerializer(ValidatedModelSerializer):

    class Meta:
        model = SecretRole
        fields = ['id', 'name', 'slug']


class NestedSecretRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='secrets-api:secretrole-detail')

    class Meta:
        model = SecretRole
        fields = ['id', 'url', 'name', 'slug']


#
# Secrets
#

class SecretObjectRelatedField(serializers.RelatedField):
    """
        GenericRelation object can be extended with different Object types
    """
    def to_representation(self, value):
        if isinstance(value, Device):
            object_serial = NestedDeviceSerializer(value, context=self.context)
            dict = object_serial.data.copy()
            dict.update({'class': 'device'})
            return dict

class SecretSerializer(TaggitSerializer, CustomFieldModelSerializer):
    object = SecretObjectRelatedField(queryset=Secret.objects.all(), required=False)
    role = NestedSecretRoleSerializer()
    plaintext = serializers.CharField()
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Secret
        fields = [
            'id', 'object', 'role', 'name', 'plaintext', 'hash', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        validators = []

    def validate(self, data):
        # Encrypt plaintext data using the master key provided from the view context
        if data.get('plaintext'):
            s = Secret(plaintext=data['plaintext'])
            s.encrypt(self.context['master_key'])
            data['ciphertext'] = s.ciphertext
            data['hash'] = s.hash

        # Validate uniqueness of name if one has been provided.
        if data.get('name'):
            validator = UniqueTogetherValidator(queryset=Secret.objects.all(), fields=('object', 'role', 'name'))
            validator.set_context(self)
            validator(data)

        # Enforce model validation
        super(SecretSerializer, self).validate(data)

        return data
