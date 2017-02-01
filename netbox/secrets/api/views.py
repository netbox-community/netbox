import base64
from Crypto.PublicKey import RSA

from django.http import HttpResponseBadRequest

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from extras.api.renderers import FormlessBrowsableAPIRenderer, FreeRADIUSClientsRenderer
from secrets.filters import SecretFilter
from secrets.models import Secret, SecretRole, UserKey
from utilities.api import WritableSerializerMixin

from . import serializers


ERR_USERKEY_MISSING = "No UserKey found for the current user."
ERR_USERKEY_INACTIVE = "UserKey has not been activated for decryption."
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
# TODO: Figure out a better way of transmitting the private key
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

    # The user's private key must be sent as a header (X-Private-Key). To overcome limitations around sending line
    # breaks in a header field, the key must be base64-encoded and stripped of all whitespace. This is a temporary
    # kludge until a more elegant approach can be devised.
    def _get_private_key(self, request):
        private_key_b64 = request.META.get('HTTP_X_PRIVATE_KEY', None)
        if private_key_b64 is None:
            return None
        # TODO: Handle invalid encoding
        return base64.b64decode(private_key_b64)

    def retrieve(self, request, *args, **kwargs):
        private_key = self._get_private_key(request)
        secret = self.get_object()

        # Attempt to unlock the Secret if a private key was provided
        if private_key is not None:

            try:
                user_key = UserKey.objects.get(user=request.user)
            except UserKey.DoesNotExist:
                return HttpResponseBadRequest(ERR_USERKEY_MISSING)
            if not user_key.is_active():
                return HttpResponseBadRequest(ERR_USERKEY_INACTIVE)

            master_key = user_key.get_master_key(private_key)
            if master_key is None:
                return HttpResponseBadRequest(ERR_PRIVKEY_INVALID)

            secret.decrypt(master_key)

        serializer = self.get_serializer(secret)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        private_key = self._get_private_key(request)
        queryset = self.filter_queryset(self.get_queryset())

        # Attempt to unlock the Secrets if a private key was provided
        master_key = None
        if private_key is not None:

            try:
                user_key = UserKey.objects.get(user=request.user)
            except UserKey.DoesNotExist:
                return HttpResponseBadRequest(ERR_USERKEY_MISSING)
            if not user_key.is_active():
                return HttpResponseBadRequest(ERR_USERKEY_INACTIVE)

            master_key = user_key.get_master_key(private_key)
            if master_key is None:
                return HttpResponseBadRequest(ERR_PRIVKEY_INVALID)

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


class RSAKeyGeneratorView(APIView):
    """
    Generate a new RSA key pair for a user. Authenticated because it's a ripe avenue for DoS.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):

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
