import base64
from Crypto.PublicKey import RSA

from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from extras.api.renderers import FormlessBrowsableAPIRenderer, FreeRADIUSClientsRenderer
from secrets.exceptions import InvalidSessionKey
from secrets.filters import SecretFilter
from secrets.models import Secret, SecretRole, SessionKey, UserKey
from utilities.api import WritableSerializerMixin
from . import serializers


ERR_USERKEY_MISSING = "No UserKey found for the current user."
ERR_USERKEY_INACTIVE = "UserKey has not been activated for decryption."
ERR_PRIVKEY_MISSING = "Private key was not provided."
ERR_PRIVKEY_INVALID = "Invalid private key."


#
# Secret Roles
#

class SecretRoleViewSet(ModelViewSet):
    queryset = SecretRole.objects.all()
    serializer_class = serializers.SecretRoleSerializer
    permission_classes = [IsAuthenticated]


#
# Secrets
#

# TODO: Need to implement custom create() and update() methods to handle secret encryption.
class SecretViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = Secret.objects.select_related(
        'device__primary_ip4', 'device__primary_ip6', 'role',
    ).prefetch_related(
        'role__users', 'role__groups',
    )
    serializer_class = serializers.SecretSerializer
    write_serializer_class = serializers.WritableSecretSerializer
    filter_class = SecretFilter
    # DRF's BrowsableAPIRenderer can't support passing the secret key as a header, so we disable it.
    renderer_classes = [FormlessBrowsableAPIRenderer, JSONRenderer, FreeRADIUSClientsRenderer]
    # Enabled BasicAuthentication for testing (until we have TokenAuthentication implemented)
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def _read_session_key(self, request):

        # Check for a session key provided as a cookie or header
        if 'session_key' in request.COOKIES:
            return base64.b64decode(request.COOKIES['session_key'])
        elif 'HTTP_X_SESSION_KEY' in request.META:
            return base64.b64decode(request.META['HTTP_X_SESSION_KEY'])
        return None

    def retrieve(self, request, *args, **kwargs):

        secret = self.get_object()
        session_key = self._read_session_key(request)

        # Retrieve session key cipher (if any) for the current user
        if session_key is not None:
            try:
                sk = SessionKey.objects.get(user=request.user)
                master_key = sk.get_master_key(session_key)
                secret.decrypt(master_key)
            except SessionKey.DoesNotExist:
                return HttpResponseBadRequest("No active session key for current user.")
            except InvalidSessionKey:
                return HttpResponseBadRequest("Invalid session key.")

        serializer = self.get_serializer(secret)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        # Attempt to retrieve the master key for decryption
        session_key = self._read_session_key(request)
        master_key = None
        if session_key is not None:
            try:
                sk = SessionKey.objects.get(user=request.user)
                master_key = sk.get_master_key(session_key)
            except SessionKey.DoesNotExist:
                return HttpResponseBadRequest("No active session key for current user.")
            except InvalidSessionKey:
                return HttpResponseBadRequest("Invalid session key.")

        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            secrets = []
            if master_key is not None:
                for secret in page:
                    secret.decrypt(master_key)
                    secrets.append(secret)
                serializer = self.get_serializer(secrets, many=True)
            else:
                serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GetSessionKeyViewSet(ViewSet):
    """
    Retrieve a temporary session key to use for encrypting and decrypting secrets via the API. The user's private RSA
    key is POSTed with the name `private_key`. An example:

        curl -v -X POST -H "Authorization: Token <token>" -H "Accept: application/json; indent=4" \\
        --data-urlencode "private_key@<filename>" https://netbox/api/secrets/get-session-key/

    This request will yield a base64-encoded session key to be included in an `X-Session-Key` header in future requests:

        {
            "session_key": "+8t4SI6XikgVmB5+/urhozx9O5qCQANyOk1MNe6taRf="
        }
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):

        # Read private key
        private_key = request.POST.get('private_key', None)
        if private_key is None:
            return HttpResponseBadRequest(ERR_PRIVKEY_MISSING)

        # Validate user key
        try:
            user_key = UserKey.objects.get(user=request.user)
        except UserKey.DoesNotExist:
            return HttpResponseBadRequest(ERR_USERKEY_MISSING)
        if not user_key.is_active():
            return HttpResponseBadRequest(ERR_USERKEY_INACTIVE)

        # Validate private key
        master_key = user_key.get_master_key(private_key)
        if master_key is None:
            return HttpResponseBadRequest(ERR_PRIVKEY_INVALID)

        # Delete the existing SessionKey for this user if one exists
        SessionKey.objects.filter(user=request.user).delete()

        # Create a new SessionKey
        sk = SessionKey(user=request.user)
        sk.save(master_key=master_key)
        encoded_key = base64.b64encode(sk.key)

        # Craft the response
        response = Response({
            'session_key': encoded_key,
        })

        # If token authentication is not in use, assign the session key as a cookie
        if request.auth is None:
            response.set_cookie('session_key', value=encoded_key, path=reverse('secrets-api:secret-list'))

        return response


class GenerateRSAKeyPairViewSet(ViewSet):
    """
    This endpoint can be used to generate a new RSA key pair. The keys are returned in PEM format.

        {
            "public_key": "<public key>",
            "private_key": "<private key>"
        }
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):

        # Determine what size key to generate
        key_size = request.GET.get('key_size', 2048)
        if key_size not in range(2048, 4097, 256):
            key_size = 2048

        # Export RSA private and public keys in PEM format
        key = RSA.generate(key_size)
        private_key = key.exportKey('PEM')
        public_key = key.publickey().exportKey('PEM')

        return Response({
            'private_key': private_key,
            'public_key': public_key,
        })
