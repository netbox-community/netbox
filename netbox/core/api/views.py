from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ReadOnlyModelViewSet

from core import filtersets
from core.choices import DataSourceStatusChoices
from core.jobs import SyncDataSourceJob
from core.models import *
from core.utils import delete_rq_job, enqueue_rq_job, get_rq_jobs, requeue_rq_job, stop_rq_job
from django_rq.queues import get_redis_connection
from django_rq.utils import get_statistics
from django_rq.settings import QUEUES_LIST
from netbox.api.metadata import ContentTypeMetadata
from netbox.api.pagination import LimitOffsetListPagination
from netbox.api.viewsets import NetBoxModelViewSet, NetBoxReadOnlyModelViewSet
from rest_framework import viewsets
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


class BaseRQListView(viewsets.ViewSet):
    """
    Retrieve a list of RQ Queues.
    """
    permission_classes = [IsAdminUser]
    serializer_class = None

    def get_data(self):
        raise NotImplementedError()

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def list(self, request):
        data = self.get_data()
        paginator = LimitOffsetListPagination()
        data = paginator.paginate_list(data, request)

        serializer = self.serializer_class(data, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class QueueViewSet(BaseRQListView):
    """
    Retrieve a list of RQ Queues.
    Note: Queue names are not URL safe so not returning a detail view.
    """
    serializer_class = serializers.BackgroundQueueSerializer
    lookup_field = 'name'

    def get_view_name(self):
        return "Background Queues"

    def get_data(self):
        return get_statistics(run_maintenance_tasks=True)["queues"]


class WorkerViewSet(BaseRQListView):
    """
    Retrieve a list of RQ Workers.
    """
    serializer_class = serializers.BackgroundWorkerSerializer
    lookup_field = 'name'

    def get_view_name(self):
        return "Background Workers"

    def get_data(self):
        config = QUEUES_LIST[0]
        return Worker.all(get_redis_connection(config['connection_config']))

    def retrieve(self, request, name):
        # all the RQ queues should use the same connection
        config = QUEUES_LIST[0]
        workers = Worker.all(get_redis_connection(config['connection_config']))
        worker = next((item for item in workers if item.name == name), None)
        if not worker:
            raise Http404

        serializer = serializers.BackgroundWorkerSerializer(worker, context={'request': request})
        return Response(serializer.data)


class TaskViewSet(BaseRQListView):
    """
    Retrieve the details of the specified RQ Task.
    """
    serializer_class = serializers.BackgroundTaskSerializer

    def get_view_name(self):
        return "Background Tasks"

    def get_data(self):
        return get_rq_jobs()

    def get_task_from_id(self, task_id):
        config = QUEUES_LIST[0]
        task = RQ_Job.fetch(task_id, connection=get_redis_connection(config['connection_config']))
        if not task:
            raise Http404

        return task

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def retrieve(self, request, pk):
        task = self.get_task_from_id(pk)
        serializer = serializers.BackgroundTaskSerializer(task, context={'request': request})
        return Response(serializer.data)

    @action(methods=["POST"], detail=True)
    def delete(self, request, pk):
        delete_rq_job(pk)
        return HttpResponse(status=200)

    @action(methods=["POST"], detail=True)
    def requeue(self, request, pk):
        requeue_rq_job(pk)
        return HttpResponse(status=200)

    @action(methods=["POST"], detail=True)
    def enqueue(self, request, pk):
        enqueue_rq_job(pk)
        return HttpResponse(status=200)

    @action(methods=["POST"], detail=True)
    def stop(self, request, pk):
        stopped_jobs = stop_rq_job(pk)
        if len(stopped_jobs) == 1:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=204)
