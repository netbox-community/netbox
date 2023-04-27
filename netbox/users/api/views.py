from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, User
from django.db.models import Count
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from netbox.api.viewsets import NetBoxModelViewSet
from users import filtersets
from users.models import ObjectPermission, Token, UserConfig
from utilities.querysets import RestrictedQuerySet
from utilities.utils import deepmerge
from . import serializers


class UsersRootView(APIRootView):
    """
    Users API root view
    """
    def get_view_name(self):
        return 'Users'


#
# Users and groups
#

class UserViewSet(NetBoxModelViewSet):
    queryset = RestrictedQuerySet(model=User).prefetch_related('groups').order_by('username')
    serializer_class = serializers.UserSerializer
    filterset_class = filtersets.UserFilterSet


class GroupViewSet(NetBoxModelViewSet):
    queryset = RestrictedQuerySet(model=Group).annotate(user_count=Count('user')).order_by('name')
    serializer_class = serializers.GroupSerializer
    filterset_class = filtersets.GroupFilterSet


#
# REST API tokens
#

class TokenViewSet(NetBoxModelViewSet):
    queryset = RestrictedQuerySet(model=Token).prefetch_related('user')
    serializer_class = serializers.TokenSerializer
    filterset_class = filtersets.TokenFilterSet

    def get_queryset(self):
        """
        Limit the non-superusers to their own Tokens.
        """
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(user=self.request.user)


class TokenProvisionView(APIView):
    """
    Non-authenticated REST API endpoint via which a user may create a Token.
    """
    permission_classes = []

    # @extend_schema(methods=["post"], responses={201: serializers.TokenSerializer})
    def post(self, request):
        serializer = serializers.TokenProvisionSerializer(data=request.data)
        serializer.is_valid()

        # Authenticate the user account based on the provided credentials
        username = serializer.data.get('username')
        password = serializer.data.get('password')
        if not username or not password:
            raise AuthenticationFailed("Username and password must be provided to provision a token.")
        user = authenticate(request=request, username=username, password=password)
        if user is None:
            raise AuthenticationFailed("Invalid username/password")

        # Create a new Token for the User
        token = Token(user=user)
        token.save()
        data = serializers.TokenSerializer(token, context={'request': request}).data
        # Manually append the token key, which is normally write-only
        data['key'] = token.key

        return Response(data, status=HTTP_201_CREATED)

    def get_serializer_class(self):
        return serializers.TokenSerializer


#
# ObjectPermissions
#

class ObjectPermissionViewSet(NetBoxModelViewSet):
    queryset = ObjectPermission.objects.prefetch_related('object_types', 'groups', 'users')
    serializer_class = serializers.ObjectPermissionSerializer
    filterset_class = filtersets.ObjectPermissionFilterSet


#
# User preferences
#

class UserConfigViewSet(ViewSet):
    """
    An API endpoint via which a user can update his or her own UserConfig data (but no one else's).
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserConfig.objects.filter(user=self.request.user)

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def list(self, request):
        """
        Return the UserConfig for the currently authenticated User.
        """
        userconfig = self.get_queryset().first()

        return Response(userconfig.data)

    @extend_schema(methods=["patch"], responses={201: OpenApiTypes.OBJECT})
    def patch(self, request):
        """
        Update the UserConfig for the currently authenticated User.
        """
        # TODO: How can we validate this data?
        userconfig = self.get_queryset().first()
        userconfig.data = deepmerge(userconfig.data, request.data)
        userconfig.save()

        return Response(userconfig.data)
