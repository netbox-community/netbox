import logging

from django.db.models import Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from netbox.api.viewsets import NetBoxModelViewSet
from users import filtersets
from users.models import Group, ObjectPermission, Owner, OwnerGroup, Token, User, UserConfig
from utilities.data import deepmerge
from utilities.querysets import RestrictedQuerySet

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
    queryset = RestrictedQuerySet(model=User).order_by('username')
    serializer_class = serializers.UserSerializer
    filterset_class = filtersets.UserFilterSet


class GroupViewSet(NetBoxModelViewSet):
    queryset = Group.objects.annotate(user_count=Count('user'))
    serializer_class = serializers.GroupSerializer
    filterset_class = filtersets.GroupFilterSet


#
# REST API tokens
#

class TokenViewSet(NetBoxModelViewSet):
    queryset = Token.objects.all()
    serializer_class = serializers.TokenSerializer
    filterset_class = filtersets.TokenFilterSet

    def create(self, request, *args, **kwargs):
        # This is the same code as NetBoxModelViewSet.create(), but re-copies the plaintext token
        # value(s) onto the re-fetched instance(s). The parent's create() re-fetches from the
        # database after perform_create() to attach prefetched related objects, which discards
        # the in-memory plaintext — for v2 tokens this value cannot be recovered later because
        # the database stores only an HMAC digest.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bulk_create = getattr(serializer, 'many', False)
        self.perform_create(serializer)

        # After creating the instance(s), re-initialize the serializer with a queryset
        # to ensure related objects are prefetched.
        if bulk_create:
            instance_pks = [obj.pk for obj in serializer.instance]
            # Capture the in-memory plaintext token values; v2 tokens cannot be recovered from the database.
            plaintexts = {obj.pk: obj.token for obj in serializer.instance}
            # Order by PK to ensure that the ordering of objects in the response
            # matches the ordering of those in the request.
            qs = list(self.get_queryset().filter(pk__in=instance_pks).order_by('pk'))
            for obj in qs:
                obj._token = plaintexts[obj.pk]
        else:
            # Capture the in-memory plaintext token; v2 tokens cannot be recovered from the database.
            plaintext = serializer.instance.token
            qs = self.get_queryset().get(pk=serializer.instance.pk)
            qs._token = plaintext

        # Re-serialize the instance(s) with prefetched data
        serializer = self.get_serializer(qs, many=bulk_create)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class TokenProvisionView(APIView):
    """
    Non-authenticated REST API endpoint via which a user may create a Token.
    """
    permission_classes = []

    @extend_schema(
        request=serializers.TokenProvisionSerializer,
        responses={
            201: serializers.TokenProvisionSerializer,
            401: OpenApiTypes.OBJECT,
        }
    )
    def post(self, request):
        serializer = serializers.TokenProvisionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def perform_create(self, serializer):
        model = serializer.Meta.model
        logger = logging.getLogger('netbox.api.views.TokenProvisionView')
        logger.info(f"Creating new {model._meta.verbose_name}")
        serializer.save()


#
# ObjectPermissions
#

class ObjectPermissionViewSet(NetBoxModelViewSet):
    queryset = ObjectPermission.objects.all()
    serializer_class = serializers.ObjectPermissionSerializer
    filterset_class = filtersets.ObjectPermissionFilterSet


#
# Owners
#

class OwnerGroupViewSet(NetBoxModelViewSet):
    queryset = OwnerGroup.objects.all()
    serializer_class = serializers.OwnerGroupSerializer
    filterset_class = filtersets.OwnerGroupFilterSet


class OwnerViewSet(NetBoxModelViewSet):
    queryset = Owner.objects.all()
    serializer_class = serializers.OwnerSerializer
    filterset_class = filtersets.OwnerFilterSet


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
