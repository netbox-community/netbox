from django.contrib.auth.models import Group, User
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ViewSet

from netbox.api.views import ModelViewSet
from users import filters
from users.models import ObjectPermission, UserConfig
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

class UserViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=User).prefetch_related('groups').order_by('username')
    serializer_class = serializers.UserSerializer
    filterset_class = filters.UserFilterSet


class GroupViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=Group).annotate(user_count=Count('user')).order_by('name')
    serializer_class = serializers.GroupSerializer
    filterset_class = filters.GroupFilterSet


#
# ObjectPermissions
#

class ObjectPermissionViewSet(ModelViewSet):
    queryset = ObjectPermission.objects.prefetch_related('object_types', 'groups', 'users')
    serializer_class = serializers.ObjectPermissionSerializer
    filterset_class = filters.ObjectPermissionFilterSet


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

    def list(self, request):
        """
        Return the UserConfig for the currently authenticated User.
        """
        userconfig = self.get_queryset().first()

        return Response(userconfig.data)

    def patch(self, request):
        """
        Update the UserConfig for the currently authenticated User.
        """
        # TODO: How can we validate this data?
        userconfig = self.get_queryset().first()
        userconfig.data = deepmerge(userconfig.data, request.data)
        userconfig.save()

        return Response(userconfig.data)
