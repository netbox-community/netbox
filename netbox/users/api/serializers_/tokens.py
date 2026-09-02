from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

from netbox.api.fields import IPNetworkSerializer
from netbox.api.serializers import ValidatedModelSerializer
from users.models import Token
from users.utils import user_may_grant_token

from .users import *

__all__ = (
    'TokenProvisionSerializer',
    'TokenSerializer',
)


class TokenSerializer(ValidatedModelSerializer):
    token = serializers.CharField(
        read_only=True,
    )
    user = UserSerializer(
        nested=True
    )
    allowed_ips = serializers.ListField(
        child=IPNetworkSerializer(),
        required=False,
        allow_empty=True,
        default=[]
    )

    class Meta:
        model = Token
        fields = (
            'id', 'url', 'display_url', 'display', 'version', 'key', 'user', 'description', 'created', 'expires',
            'last_used', 'enabled', 'write_enabled', 'pepper_id', 'allowed_ips', 'token',
        )
        read_only_fields = ('key',)
        brief_fields = ('id', 'url', 'display', 'version', 'key', 'enabled', 'write_enabled', 'description')

    def get_fields(self):
        fields = super().get_fields()

        # Make user field read-only if updating an existing Token.
        if self.instance is not None:
            fields['user'].read_only = True

        return fields

    def validate(self, data):

        # If the Token is being created on behalf of another user, enforce the grant_token permission.
        # Use user_may_grant_token() rather than has_perm(obj=None): the latter short-circuits to True
        # when the permission is present in cache without evaluating ObjectPermission constraints.
        request = self.context.get('request')
        token_user = data.get('user')
        if token_user and token_user != request.user and not user_may_grant_token(request.user, token_user):
            raise PermissionDenied("This user does not have permission to create tokens for other users.")

        return super().validate(data)

    def create(self, validated_data):
        instance = super().create(validated_data)
        # The plaintext token is only available in memory after save(); v2 tokens persist only an
        # HMAC digest, so it can't be recovered later. Stash it on the request so to_representation()
        # can return it even after the viewset re-fetches the instance from the database.
        if request := self.context.get('request'):
            if not hasattr(request, '_token_plaintexts'):
                request._token_plaintexts = {}
            request._token_plaintexts[instance.pk] = instance.token
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get('token') and (request := self.context.get('request')):
            if plaintext := getattr(request, '_token_plaintexts', {}).get(instance.pk):
                data['token'] = plaintext
        return data


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
            'id', 'url', 'display_url', 'display', 'version', 'user', 'key', 'created', 'expires', 'last_used', 'key',
            'enabled', 'write_enabled', 'description', 'allowed_ips', 'username', 'password', 'token',
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
