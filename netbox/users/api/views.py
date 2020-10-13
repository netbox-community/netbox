from django.contrib.auth.models import Group, User
from django.db.models import Count
from rest_framework.routers import APIRootView

from netbox.api.views import ModelViewSet
from users import filters
from users.models import ObjectPermission
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
