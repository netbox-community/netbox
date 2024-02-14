from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ReadOnlyModelViewSet

from core import filtersets
from core.models import *
from netbox.api.viewsets import NetBoxModelViewSet, NetBoxReadOnlyModelViewSet
from utilities.utils import count_related
from . import serializers


class CoreRootView(APIRootView):
    """
    Core API root view
    """
    def get_view_name(self):
        return 'Core'


class DataSourceViewSet(NetBoxModelViewSet):
    queryset = DataSource.objects.annotate(
        file_count=count_related(DataFile, 'source')
    )
    serializer_class = serializers.DataSourceSerializer
    filterset_class = filtersets.DataSourceFilterSet

    @action(detail=True, methods=['post'])
    def sync(self, request, pk):
        """
        Enqueue a job to synchronize the DataSource.
        """
        if not request.user.has_perm('core.sync_datasource'):
            raise PermissionDenied("Syncing data sources requires the core.sync_datasource permission.")

        datasource = get_object_or_404(DataSource, pk=pk)
        datasource.enqueue_sync_job(request)
        serializer = serializers.DataSourceSerializer(datasource, context={'request': request})

        return Response(serializer.data)


class DataFileViewSet(NetBoxReadOnlyModelViewSet):
    queryset = DataFile.objects.defer('data')
    serializer_class = serializers.DataFileSerializer
    filterset_class = filtersets.DataFileFilterSet


class JobViewSet(ReadOnlyModelViewSet):
    """
    Retrieve a list of job results
    """
    queryset = Job.objects.all()
    serializer_class = serializers.JobSerializer
    filterset_class = filtersets.JobFilterSet
