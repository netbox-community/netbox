from django.contrib.contenttypes.models import ContentType
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from netbox.api import ContentTypeField
from netbox.api.serializers import OrganizationalModelSerializer, PrimaryModelSerializer
from secrets.constants import SECRET_ASSIGNMENT_MODELS
from secrets.models import Secret, SecretRole
from utilities.api import get_serializer_for_model
from .nested_serializers import *


#
# Secrets
#

class SecretRoleSerializer(OrganizationalModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='secrets-api:secretrole-detail')
    secret_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SecretRole
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'custom_fields', 'created', 'last_updated',
            'secret_count',
        ]


class SecretSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='secrets-api:secret-detail')
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(SECRET_ASSIGNMENT_MODELS)
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)
    role = NestedSecretRoleSerializer()
    plaintext = serializers.CharField()

    class Meta:
        model = Secret
        fields = [
            'id', 'url', 'display', 'assigned_object_type', 'assigned_object_id', 'assigned_object', 'role', 'name',
            'plaintext', 'hash', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        validators = []

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_assigned_object(self, obj):
        serializer = get_serializer_for_model(obj.assigned_object, prefix='Nested')
        context = {'request': self.context['request']}
        return serializer(obj.assigned_object, context=context).data

    def validate(self, data):

        # Encrypt plaintext data using the master key provided from the view context
        if data.get('plaintext'):
            s = Secret(plaintext=data['plaintext'])
            s.encrypt(self.context['master_key'])
            data['ciphertext'] = s.ciphertext
            data['hash'] = s.hash

        super().validate(data)

        return data
