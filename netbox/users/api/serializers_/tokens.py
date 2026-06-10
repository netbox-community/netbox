from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

from netbox.api.fields import IPNetworkSerializer
from netbox.api.serializers import ValidatedModelSerializer
from users.models import Token, User

from .users import *

__all__ = (
    'TokenProvisionSerializer',
    'TokenSerializer',
)


def _user_may_grant_token(requesting_user, token_user):
    """
    Return True if *requesting_user* has permission to create a token for *token_user*,
    respecting ObjectPermission constraints on the users.grant_token permission.

    ``has_perm('users.grant_token', obj=None)`` always short-circuits to True when the
    permission is present in the cache (obj=None bypasses constraint evaluation in
    ObjectPermissionMixin.has_perm).  Since the new token does not yet exist in the
    database we cannot pass an existing Token as obj.  Instead we extract the raw
    constraint list, remap Token-field paths to User-field paths, and evaluate them
    directly against the target User record — the only variable in a new token creation.

    Field remapping rules:
      ``user__<field>`` → ``<field>``  (FK traversal into User)
      ``user``          → ``pk``       (Token.user FK becomes User.pk)

    Constraints referencing other Token fields cannot be evaluated for an unsaved
    token; the function returns False (deny) for those.
    """
    # Mirrors ObjectPermissionMixin.has_perm: superusers implicitly have all permissions.
    if requesting_user.is_active and requesting_user.is_superuser:
        return True

    perm = 'users.grant_token'

    # get_all_permissions() populates _object_perm_cache as a side effect.
    # Guard against missing cache key in case a non-standard backend is in use.
    if perm not in requesting_user.get_all_permissions():
        return False

    constraints = getattr(requesting_user, '_object_perm_cache', {}).get(perm, [])

    # An empty/null constraint means "no restriction" — allow any target.
    if any(not c for c in constraints):
        return True

    # Substitute the $user token so {"user": "$user"} resolves to the requesting user.
    user_token = '$user'
    resolved_user_id = requesting_user.pk

    q = Q()
    for constraint in constraints:
        user_constraint = {}
        for key, raw_val in constraint.items():
            # Resolve $user placeholder; constraint values are JSON primitives so
            # no .pk extraction is needed.
            val = resolved_user_id if raw_val == user_token else raw_val
            if key == 'user':
                user_constraint['pk'] = val
            elif key.startswith('user__'):
                user_constraint[key.removeprefix('user__')] = val
            else:
                # Non-user Token field — cannot evaluate for a new (unsaved) token.
                # Fail closed.
                return False
        q |= Q(**user_constraint)

    return User.objects.filter(q, pk=token_user.pk).exists()


class TokenSerializer(ValidatedModelSerializer):
    token = serializers.CharField(
        required=False,
        default=Token.generate,
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
        # Use _user_may_grant_token() rather than has_perm(obj=None): the latter short-circuits to True
        # when the permission is present in cache without evaluating ObjectPermission constraints.
        request = self.context.get('request')
        token_user = data.get('user')
        if token_user and token_user != request.user and not _user_may_grant_token(request.user, token_user):
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
