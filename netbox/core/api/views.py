from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet

from core import filtersets
from core.choices import DataSourceStatusChoices
from core.jobs import SyncDataSourceJob
from core.models import *
from core.utils import get_rq_jobs_from_status
from django_rq.queues import get_queue
from django_rq.utils import get_statistics
from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet, NetBoxReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser
from . import serializers


class CoreRootView(APIRootView):
    """
    Core API root view
    """
    def get_view_name(self):
        return 'Core'


class DataSourceViewSet(NetBoxModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = serializers.DataSourceSerializer
    filterset_class = filtersets.DataSourceFilterSet

    @action(detail=True, methods=['post'])
    def sync(self, request, pk):
        """
        Enqueue a job to synchronize the DataSource.
        """
        datasource = get_object_or_404(DataSource, pk=pk)

        if not request.user.has_perm('core.sync_datasource', obj=datasource):
            raise PermissionDenied(_("This user does not have permission to synchronize this data source."))

        # Enqueue the sync job & update the DataSource's status
        SyncDataSourceJob.enqueue(instance=datasource, user=request.user)
        datasource.status = DataSourceStatusChoices.QUEUED
        DataSource.objects.filter(pk=datasource.pk).update(status=datasource.status)

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


class ObjectChangeViewSet(ReadOnlyModelViewSet):
    """
    Retrieve a list of recent changes.
    """
    metadata_class = ContentTypeMetadata
    queryset = ObjectChange.objects.valid_models()
    serializer_class = serializers.ObjectChangeSerializer
    filterset_class = filtersets.ObjectChangeFilterSet


class BackgroundQueueViewSet(ViewSet):
    serializer_class = serializers.BackgroundQueueSerializer
    permission_classes = [IsAdminUser]

    def get_view_name(self):
        return "BackgroundQueueViewSet"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def list(self, request):
        """
        Return the UserConfig for the currently authenticated User.
        """
        data = get_statistics(run_maintenance_tasks=True)["queues"]
        serializer = serializers.BackgroundQueueSerializer(data, many=True)
        return Response(serializer.data)


class BackgroundTaskViewSet(ViewSet):
    serializer_class = serializers.BackgroundTaskSerializer
    permission_classes = [IsAdminUser]

    def get_view_name(self):
        return "BackgroundTaskViewSet"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def list(self, request, queue_name):
        """
        Return the UserConfig for the currently authenticated User.
        """
        queue = get_queue(queue_name)
        data = queue.get_jobs()
        serializer = serializers.BackgroundTaskSerializer(data, many=True)
        return Response(serializer.data)


class BaseBackgroundTaskViewSet(ViewSet):
    serializer_class = serializers.BackgroundTaskSerializer
    permission_classes = [IsAdminUser]
    registry = None

    def get_view_name(self):
        return "BackgroundTaskViewSet"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def list(self, request, queue_name):
        """
        Return the UserConfig for the currently authenticated User.
        """
        queue = get_queue(queue_name)
        data = get_rq_jobs_from_status(queue, self.registry)
        serializer = serializers.BackgroundTaskSerializer(data, many=True)
        return Response(serializer.data)


class BackgroundTaskDeferredViewSet(BaseBackgroundTaskViewSet):
    registry = "deferred"


class BackgroundTaskFailedViewSet(BaseBackgroundTaskViewSet):
    registry = "failed"


class BackgroundTaskFinishedViewSet(BaseBackgroundTaskViewSet):
    registry = "finished"


class BackgroundTaskStartedViewSet(BaseBackgroundTaskViewSet):
    registry = "started"
