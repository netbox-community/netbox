from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from core import filtersets
from core.choices import DataSourceStatusChoices
from core.jobs import SyncDataSourceJob
from core.models import *
from core.utils import delete_rq_job, enqueue_rq_job, get_rq_jobs_from_status, requeue_rq_job, stop_rq_job
from django_rq.queues import get_queue, get_redis_connection
from django_rq.utils import get_statistics
from django_rq.settings import QUEUES_LIST
from netbox.api.metadata import ContentTypeMetadata
from netbox.api.viewsets import NetBoxModelViewSet, NetBoxReadOnlyModelViewSet
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser
from rq.job import Job as RQ_Job
from rq.worker import Worker
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


class LimitOffsetListPagination(LimitOffsetPagination):
    """
    DRF LimitOffset Paginator but for list instead of queryset
    """
    count = 0
    offset = 0

    def paginate_list(self, data, request, view=None):
        self.request = request
        self.limit = self.get_limit(request)
        self.count = len(data)
        self.offset = self.get_offset(request)

        if self.limit is None:
            self.limit = self.count

        if self.count == 0 or self.offset > self.count:
            return []

        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        return data[self.offset:self.offset + self.limit]


class BaseRQListView(viewsets.ViewSet):
    """
    Retrieve a list of RQ Queues.
    """
    permission_classes = [IsAdminUser]
    serializer_class = None

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def list(self, request):
        data = self.get_data()
        paginator = LimitOffsetListPagination()
        data = paginator.paginate_list(data, request)

        serializer = self.serializer_class(data, many=True)
        return paginator.get_paginated_response(serializer.data)


class QueueViewSet(BaseRQListView):
    """
    Retrieve a list of RQ Queues.
    """
    serializer_class = serializers.BackgroundQueueSerializer

    def get_view_name(self):
        return "Background Queues"

    def get_data(self):
        return get_statistics(run_maintenance_tasks=True)["queues"]


class WorkerViewSet(BaseRQListView):
    """
    Retrieve a list of RQ Workers.
    """
    serializer_class = serializers.BackgroundWorkerSerializer

    def get_view_name(self):
        return "Background Workers"

    def get_data(self):
        config = QUEUES_LIST[0]
        return Worker.all(get_redis_connection(config['connection_config']))

    def retrieve(self, request, pk=None):
        # all the RQ queues should use the same connection
        if not pk:
            raise Http404

        config = QUEUES_LIST[0]
        workers = Worker.all(get_redis_connection(config['connection_config']))
        worker = next((item for item in workers if item.name == pk), None)
        if not worker:
            raise Http404

        serializer = serializers.BackgroundWorkerSerializer(worker)
        return Response(serializer.data)


class TaskListView(APIView):
    """
    Retrieve a list of RQ Tasks in the specified Queue.
    """
    permission_classes = [IsAdminUser]

    def get_view_name(self):
        return "Background Tasks"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request, queue_name, format=None):
        try:
            queue = get_queue(queue_name)
        except KeyError:
            raise Http404

        data = queue.get_jobs()
        serializer = serializers.BackgroundTaskSerializer(data, many=True)
        return Response(serializer.data)


class BaseTaskView(APIView):
    permission_classes = [IsAdminUser]

    def get_view_name(self):
        return "Background Task"

    def get_task_from_id(self, task_id):
        config = QUEUES_LIST[0]
        task = RQ_Job.fetch(task_id, connection=get_redis_connection(config['connection_config']))
        if not task:
            raise Http404

        return task


class TaskDetailView(BaseTaskView):
    """
    Retrieve the details of the specified RQ Task.
    """
    permission_classes = [IsAdminUser]

    def get_view_name(self):
        return "Background Task"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request, task_id, format=None):
        task = self.get_task_from_id(task_id)
        serializer = serializers.BackgroundTaskSerializer(task)
        return Response(serializer.data)


class TaskDeleteView(APIView):
    """
    Deletes the specified RQ Task.
    """
    permission_classes = [IsAdminUser]

    def get_view_name(self):
        return "Background Task"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def post(self, request, task_id, format=None):
        delete_rq_job(task_id)
        return HttpResponse(status=200)


class TaskRequeueView(APIView):
    """
    Requeues the specified RQ Task.
    """
    permission_classes = [IsAdminUser]

    def get_view_name(self):
        return "Background Task"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def post(self, request, task_id, format=None):
        requeue_rq_job(task_id)
        return HttpResponse(status=200)


class TaskEnqueueView(APIView):
    """
    Enqueues the specified RQ Task.
    """
    permission_classes = [IsAdminUser]

    def get_view_name(self):
        return "Background Task"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def post(self, request, task_id, format=None):
        enqueue_rq_job(task_id)
        return HttpResponse(status=200)


class TaskStopView(APIView):
    """
    Stops the specified RQ Task.
    """
    permission_classes = [IsAdminUser]

    def get_view_name(self):
        return "Background Task"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def post(self, request, task_id, format=None):
        stopped_jobs = stop_rq_job(task_id)
        if len(stopped_jobs) == 1:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=204)


class BaseTaskListView(APIView):
    permission_classes = [IsAdminUser]
    registry = None

    def get_view_name(self):
        return "Background Tasks"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request, queue_name, format=None):
        try:
            queue = get_queue(queue_name)
        except KeyError:
            raise Http404

        data = get_rq_jobs_from_status(queue, self.registry)
        serializer = serializers.BackgroundTaskSerializer(data, many=True)
        return Response(serializer.data)


class DeferredTaskListView(BaseTaskListView):
    """
    Retrieve a list of Deferred RQ Tasks in the specified Queue.
    """
    registry = "deferred"

    def get_view_name(self):
        return "Deferred Tasks"


class FailedTaskListView(BaseTaskListView):
    """
    Retrieve a list of Failed RQ Tasks in the specified Queue.
    """
    registry = "failed"

    def get_view_name(self):
        return "Failed Tasks"


class FinishedTaskListView(BaseTaskListView):
    """
    Retrieve a list of Finished RQ Tasks in the specified Queue.
    """
    registry = "finished"

    def get_view_name(self):
        return "Finished Tasks"


class StartedTaskListView(BaseTaskListView):
    """
    Retrieve a list of Started RQ Tasks in the specified Queue.
    """
    registry = "started"

    def get_view_name(self):
        return "Started Tasks"


class QueuedTaskListView(BaseTaskListView):
    """
    Retrieve a list of Queued RQ Tasks in the specified Queue.
    """
    registry = "queued"

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request, queue_name, format=None):
        try:
            queue = get_queue(queue_name)
        except KeyError:
            raise Http404

        data = queue.get_jobs()
        serializer = serializers.BackgroundTaskSerializer(data, many=True)
        return Response(serializer.data)
