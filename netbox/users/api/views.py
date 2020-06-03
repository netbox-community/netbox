from utilities.api import ModelViewSet
from . import serializers

from users.models import ObjectPermission


#
# ObjectPermissions
#

class ObjectPermissionViewSet(ModelViewSet):
    queryset = ObjectPermission.objects.prefetch_related('object_types', 'groups', 'users')
    serializer_class = serializers.ObjectPermissionSerializer
    # filterset_class = filters.ObjectPermissionFilterSet
