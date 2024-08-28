from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

from netbox.api.fields import IPNetworkSerializer
from netbox.api.serializers import ValidatedModelSerializer
from users.models import Token
from .users import *

__all__ = (
    'TokenProvisionSerializer',
    'TokenSerializer',
)


class TokenSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:token-detail')
    key = serializers.CharField(
        min_length=40,
        max_length=40,
        allow_blank=True,
        required=False,
        write_only=not settings.ALLOW_TOKEN_RETRIEVAL
    )
    user = UserSerializer(nested=True)
    allowed_ips = serializers.ListField(
        child=IPNetworkSerializer(),
        required=False,
        allow_empty=True,
        default=[]
    )

    class Meta:
        model = Token
        fields = (
            'id', 'url', 'display', 'user', 'created', 'expires', 'last_used', 'key', 'write_enabled', 'description',
            'allowed_ips',
        )
        brief_fields = ('id', 'url', 'display', 'key', 'write_enabled', 'description')

    def to_internal_value(self, data):
        if not getattr(self.instance, 'key', None) and 'key' not in data:
            data['key'] = Token.generate_key()
        return super().to_internal_value(data)

    def validate(self, data):

        # If the Token is being created on behalf of another user, enforce the grant_token permission.
        request = self.context.get('request')
        token_user = data.get('user')
        if token_user and token_user != request.user and not request.user.has_perm('users.grant_token'):
            raise PermissionDenied("This user does not have permission to create tokens for other users.")

        return super().validate(data)


class TokenProvisionSerializer(TokenSerializer):
    user = UserSerializer(
        nested=True,
        read_only=True
    )
    username = serializers.CharField(
        write_only=True
    )
    password = serializers.CharField(
        write_only=True
    )
    last_used = serializers.DateTimeField(
        read_only=True
    )
    key = serializers.CharField(
        read_only=True
    )

    class Meta:
        model = Token
        fields = (
            'id', 'url', 'display', 'user', 'created', 'expires', 'last_used', 'key', 'write_enabled', 'description',
            'allowed_ips', 'username', 'password',
        )

    def validate(self, data):
        # Validate the username and password
        username = data.pop('username')
        password = data.pop('password')
        user = authenticate(request=self.context.get('request'), username=username, password=password)
        if user is None:
            raise AuthenticationFailed("Invalid username/password")

        # Inject the user into the validated data
        data['user'] = user

        return data
