import logging

from django.conf import settings
from django.utils import timezone
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.permissions import SAFE_METHODS, BasePermission, DjangoObjectPermissions

from netbox.config import get_config
from users.constants import TOKEN_PREFIX
from users.models import Token
from utilities.request import get_client_ip

V1_KEYWORD = 'Token'
V2_KEYWORD = 'Bearer'


class TokenAuthentication(BaseAuthentication):
    """
    A custom authentication scheme which enforces Token expiration times and source IP restrictions.
    """
    model = Token

    def authenticate(self, request):
        # Authorization header is not present; ignore
        if not (auth := get_authorization_header(request).split()):
            return None
        # Unrecognized header; ignore
        if auth[0].lower() not in (V1_KEYWORD.lower().encode(), V2_KEYWORD.lower().encode()):
            return None
        # Check for extraneous token content
        if len(auth) != 2:
            raise exceptions.AuthenticationFailed(
                'Invalid authorization header: Must be in the form "Bearer <key>.<token>" or "Token <token>"'
            )
        # Extract the key (if v2) & token plaintext from the auth header
        try:
            auth_value = auth[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid authorization header: Token contains invalid characters')

        # Infer token version from presence or absence of prefix
        version = 2 if auth_value.startswith(TOKEN_PREFIX) else 1

        if version == 1:
            key, plaintext = None, auth_value
        else:
            auth_value = auth_value.removeprefix(TOKEN_PREFIX)
            try:
                key, plaintext = auth_value.split('.', 1)
            except ValueError:
                raise exceptions.AuthenticationFailed(
                    "Invalid authorization header: Could not parse key from v2 token. Did you mean to use 'Token' "
                    "instead of 'Bearer'?"
                )

        # Look for a matching token in the database
        try:
            qs = Token.objects.prefetch_related('user')
            if version == 1:
                # Fetch v1 token by querying plaintext value directly
                token = qs.get(version=version, plaintext=plaintext)
            else:
                # Fetch v2 token by key, then validate the plaintext
                token = qs.get(version=version, key=key)
                if not token.validate(plaintext):
                    # Key is valid but plaintext is not. Raise DoesNotExist to guard against key enumeration.
                    raise Token.DoesNotExist()
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed(f"Invalid v{version} token")

        # Enforce source IP restrictions (if any) set on the token
        if token.allowed_ips:
            client_ip = get_client_ip(request)
            if client_ip is None:
                raise exceptions.AuthenticationFailed(
                    'Client IP address could not be determined for validation. Check that the HTTP server is '
                    'correctly configured to pass the required header(s).'
                )
            if not token.validate_client_ip(client_ip):
                raise exceptions.AuthenticationFailed(
                    f"Source IP {client_ip} is not permitted to authenticate using this token."
                )

        # Enforce the Token is enabled
        if not token.enabled:
            raise exceptions.AuthenticationFailed('Token disabled')

        # Enforce the Token's expiration time, if one has been set.
        if token.is_expired:
            raise exceptions.AuthenticationFailed('Token expired')

        # Update last used, but only once per minute at most. This reduces write load on the database
        if not token.last_used or (timezone.now() - token.last_used).total_seconds() > 60:
            # If maintenance mode is enabled, assume the database is read-only, and disable updating the token's
            # last_used time upon authentication.
            if get_config().MAINTENANCE_MODE:
                logger = logging.getLogger('netbox.auth.login')
                logger.debug("Maintenance mode enabled: Disabling update of token's last used timestamp")
            else:
                Token.objects.filter(pk=token.pk).update(last_used=timezone.now())

        user = token.user

        # When LDAP authentication is active try to load user data from LDAP directory
        if 'netbox.authentication.LDAPBackend' in settings.REMOTE_AUTH_BACKEND:
            from netbox.authentication import LDAPBackend
            ldap_backend = LDAPBackend()

            # Load from LDAP if FIND_GROUP_PERMS is active
            # Always query LDAP when user is not active, otherwise it is never activated again
            if ldap_backend.settings.FIND_GROUP_PERMS or not token.user.is_active:
                ldap_user = ldap_backend.populate_user(token.user.username)
                # If the user is found in the LDAP directory use it, if not fallback to the local user
                if ldap_user:
                    user = ldap_user

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User inactive")

        return user, token


class TokenPermissions(DjangoObjectPermissions):
    """
    Custom permissions handler which extends the built-in DjangoModelPermissions to validate a Token's write ability
    for unsafe requests (POST/PUT/PATCH/DELETE).
    """
    # Override the stock perm_map to enforce view permissions
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def __init__(self):

        # LOGIN_REQUIRED determines whether read-only access is provided to anonymous users.
        self.authenticated_users_only = settings.LOGIN_REQUIRED

        super().__init__()

    def _verify_write_permission(self, request):

        # If token authentication is in use, verify that the token allows write operations (for unsafe methods).
        if request.method in SAFE_METHODS or request.auth.write_enabled:
            return True
        return False

    def has_permission(self, request, view):

        # Enforce Token write ability
        if isinstance(request.auth, Token) and not self._verify_write_permission(request):
            return False

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):

        # Enforce Token write ability
        if isinstance(request.auth, Token) and not self._verify_write_permission(request):
            return False

        return super().has_object_permission(request, view, obj)


class TokenWritePermission(BasePermission):
    """
    Verify the token has write_enabled for unsafe methods, without requiring specific model permissions.
    Used for custom actions that accept user data but don't map to standard CRUD operations.
    """

    def has_permission(self, request, view):
        if not isinstance(request.auth, Token):
            raise exceptions.PermissionDenied(
                "TokenWritePermission requires token authentication."
            )
        return bool(request.method in SAFE_METHODS or request.auth.write_enabled)


class IsAuthenticatedOrLoginNotRequired(BasePermission):
    """
    Returns True if the user is authenticated or LOGIN_REQUIRED is False.
    """
    def has_permission(self, request, view):
        if not settings.LOGIN_REQUIRED:
            return True
        return request.user.is_authenticated


class TokenScheme(OpenApiAuthenticationExtension):
    target_class = 'netbox.api.authentication.TokenAuthentication'
    name = 'tokenAuth'
    match_subclasses = True

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': '`Token <token>` (v1) or `Bearer <key>.<token>` (v2)',
        }
