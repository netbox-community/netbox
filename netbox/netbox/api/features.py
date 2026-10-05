from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from netbox.api.authentication import TokenSyncPermission

__all__ = (
    'SyncedDataMixin',
)


class SyncedDataMixin:

    def get_permissions(self):
        if self.action == 'sync':
            return [TokenSyncPermission()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def sync(self, request, pk):
        """
        Provide a /sync API endpoint to synchronize an object's data from its associated DataFile (if any).
        """
        # Rebuild from the default manager: initial() has narrowed self.queryset to the add permission,
        # which does not govern this action.
        queryset = self.queryset.model.objects.restrict(request.user, 'sync')
        obj = get_object_or_404(queryset, pk=pk)
        if obj.data_file:
            obj.sync(save=True)
        serializer = self.serializer_class(obj, context={'request': request})

        return Response(serializer.data)
