from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from utilities.permissions import get_permission_for_model

__all__ = (
    'SyncedDataMixin',
)


class SyncedDataMixin:

    @action(detail=True, methods=['post'])
    def sync(self, request, pk):
        """
        Provide a /sync API endpoint to synchronize an object's data from its associated DataFile (if any).
        """
        permission = get_permission_for_model(self.queryset.model, 'sync')
        if not request.user.has_perm(permission):
            raise PermissionDenied(f"Missing permission: {permission}")

        obj = get_object_or_404(self.queryset, pk=pk)
        if obj.data_file:
            obj.sync(save=True)
        serializer = self.serializer_class(obj, context={'request': request})

        return Response(serializer.data)
