from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django_rq.queues import get_queue_by_index, get_redis_connection
from django_rq.settings import QUEUES_MAP, QUEUES_LIST
from django_rq.utils import get_jobs, get_statistics, stop_jobs
from rq import requeue_job
from rq.exceptions import NoSuchJobError
from rq.job import Job as RQ_Job, JobStatus as RQJobStatus
from rq.registry import (
    DeferredJobRegistry, FailedJobRegistry, FinishedJobRegistry, ScheduledJobRegistry, StartedJobRegistry,
)
from rq.worker import Worker
from rq.worker_registration import clean_worker_registry

from netbox.config import get_config, PARAMS
from netbox.views import generic
from netbox.views.generic.base import BaseObjectView
from netbox.views.generic.mixins import TableMixin
from utilities.forms import ConfirmationForm
from utilities.utils import count_related
from utilities.views import ContentTypePermissionRequiredMixin, register_model_view
from . import filtersets, forms, tables
from .models import *


#
# Data sources
#

class DataSourceListView(generic.ObjectListView):
    queryset = DataSource.objects.annotate(
        file_count=count_related(DataFile, 'source')
    )
    filterset = filtersets.DataSourceFilterSet
    filterset_form = forms.DataSourceFilterForm
    table = tables.DataSourceTable


@register_model_view(DataSource)
class DataSourceView(generic.ObjectView):
    queryset = DataSource.objects.all()

    def get_extra_context(self, request, instance):
        related_models = (
            (DataFile.objects.restrict(request.user, 'view').filter(source=instance), 'source_id'),
        )

        return {
            'related_models': related_models,
        }


@register_model_view(DataSource, 'sync')
class DataSourceSyncView(BaseObjectView):
    queryset = DataSource.objects.all()

    def get_required_permission(self):
        return 'core.sync_datasource'

    def get(self, request, pk):
        # Redirect GET requests to the object view
        datasource = get_object_or_404(self.queryset, pk=pk)
        return redirect(datasource.get_absolute_url())

    def post(self, request, pk):
        datasource = get_object_or_404(self.queryset, pk=pk)
        job = datasource.enqueue_sync_job(request)

        messages.success(request, f"Queued job #{job.pk} to sync {datasource}")
        return redirect(datasource.get_absolute_url())


@register_model_view(DataSource, 'edit')
class DataSourceEditView(generic.ObjectEditView):
    queryset = DataSource.objects.all()
    form = forms.DataSourceForm


@register_model_view(DataSource, 'delete')
class DataSourceDeleteView(generic.ObjectDeleteView):
    queryset = DataSource.objects.all()


class DataSourceBulkImportView(generic.BulkImportView):
    queryset = DataSource.objects.all()
    model_form = forms.DataSourceImportForm


class DataSourceBulkEditView(generic.BulkEditView):
    queryset = DataSource.objects.annotate(
        count_files=count_related(DataFile, 'source')
    )
    filterset = filtersets.DataSourceFilterSet
    table = tables.DataSourceTable
    form = forms.DataSourceBulkEditForm


class DataSourceBulkDeleteView(generic.BulkDeleteView):
    queryset = DataSource.objects.annotate(
        count_files=count_related(DataFile, 'source')
    )
    filterset = filtersets.DataSourceFilterSet
    table = tables.DataSourceTable


#
# Data files
#

class DataFileListView(generic.ObjectListView):
    queryset = DataFile.objects.defer('data')
    filterset = filtersets.DataFileFilterSet
    filterset_form = forms.DataFileFilterForm
    table = tables.DataFileTable
    actions = {
        'bulk_delete': {'delete'},
    }


@register_model_view(DataFile)
class DataFileView(generic.ObjectView):
    queryset = DataFile.objects.all()


@register_model_view(DataFile, 'delete')
class DataFileDeleteView(generic.ObjectDeleteView):
    queryset = DataFile.objects.all()


class DataFileBulkDeleteView(generic.BulkDeleteView):
    queryset = DataFile.objects.defer('data')
    filterset = filtersets.DataFileFilterSet
    table = tables.DataFileTable


#
# Jobs
#

class JobListView(generic.ObjectListView):
    queryset = Job.objects.all()
    filterset = filtersets.JobFilterSet
    filterset_form = forms.JobFilterForm
    table = tables.JobTable
    actions = {
        'export': {'view'},
        'bulk_delete': {'delete'},
    }


class JobView(generic.ObjectView):
    queryset = Job.objects.all()


class JobDeleteView(generic.ObjectDeleteView):
    queryset = Job.objects.all()


class JobBulkDeleteView(generic.BulkDeleteView):
    queryset = Job.objects.all()
    filterset = filtersets.JobFilterSet
    table = tables.JobTable


#
# Config Revisions
#

class ConfigView(generic.ObjectView):
    queryset = ConfigRevision.objects.all()

    def get_object(self, **kwargs):
        revision_id = cache.get('config_version')
        try:
            return ConfigRevision.objects.get(pk=revision_id)
        except ConfigRevision.DoesNotExist:
            # Fall back to using the active config data if no record is found
            return ConfigRevision(
                data=get_config().defaults
            )


class ConfigRevisionListView(generic.ObjectListView):
    queryset = ConfigRevision.objects.all()
    filterset = filtersets.ConfigRevisionFilterSet
    filterset_form = forms.ConfigRevisionFilterForm
    table = tables.ConfigRevisionTable


@register_model_view(ConfigRevision)
class ConfigRevisionView(generic.ObjectView):
    queryset = ConfigRevision.objects.all()


class ConfigRevisionEditView(generic.ObjectEditView):
    queryset = ConfigRevision.objects.all()
    form = forms.ConfigRevisionForm


@register_model_view(ConfigRevision, 'delete')
class ConfigRevisionDeleteView(generic.ObjectDeleteView):
    queryset = ConfigRevision.objects.all()


class ConfigRevisionBulkDeleteView(generic.BulkDeleteView):
    queryset = ConfigRevision.objects.all()
    filterset = filtersets.ConfigRevisionFilterSet
    table = tables.ConfigRevisionTable


class ConfigRevisionRestoreView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'core.configrevision_edit'

    def get(self, request, pk):
        candidate_config = get_object_or_404(ConfigRevision, pk=pk)

        # Get the current ConfigRevision
        config_version = get_config().version
        current_config = ConfigRevision.objects.filter(pk=config_version).first()

        params = []
        for param in PARAMS:
            params.append((
                param.name,
                current_config.data.get(param.name, None),
                candidate_config.data.get(param.name, None)
            ))

        return render(request, 'core/configrevision_restore.html', {
            'object': candidate_config,
            'params': params,
        })

    def post(self, request, pk):
        if not request.user.has_perm('core.configrevision_edit'):
            return HttpResponseForbidden()

        candidate_config = get_object_or_404(ConfigRevision, pk=pk)
        candidate_config.activate()
        messages.success(request, f"Restored configuration revision #{pk}")

        return redirect(candidate_config.get_absolute_url())


#
# Background Tasks (RQ)
#

class BaseRQView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_staff


class BackgroundQueueListView(TableMixin, BaseRQView):
    table = tables.BackgroundQueueTable

    def get(self, request):
        data = get_statistics(run_maintenance_tasks=True)["queues"]
        table = self.get_table(data, request, bulk_actions=False)

        return render(request, 'core/rq_queue_list.html', {
            'table': table,
        })


class BackgroundTaskListView(TableMixin, BaseRQView):
    table = tables.BackgroundTaskTable

    def get_table_data(self, request, queue, status):
        jobs = []

        # Call get_jobs() to returned queued tasks
        if status == RQJobStatus.QUEUED:
            return queue.get_jobs()

        # For other statuses, determine the registry to list (or raise a 404 for invalid statuses)
        try:
            registry_cls = {
                RQJobStatus.STARTED: StartedJobRegistry,
                RQJobStatus.DEFERRED: DeferredJobRegistry,
                RQJobStatus.FINISHED: FinishedJobRegistry,
                RQJobStatus.FAILED: FailedJobRegistry,
                RQJobStatus.SCHEDULED: ScheduledJobRegistry,
            }[status]
        except KeyError:
            raise Http404
        registry = registry_cls(queue.name, queue.connection)

        job_ids = registry.get_job_ids()
        if status != RQJobStatus.DEFERRED:
            jobs = get_jobs(queue, job_ids, registry)
        else:
            # Deferred jobs require special handling
            for job_id in job_ids:
                try:
                    jobs.append(RQ_Job.fetch(job_id, connection=queue.connection, serializer=queue.serializer))
                except NoSuchJobError:
                    pass

        if jobs and status == RQJobStatus.SCHEDULED:
            for job in jobs:
                job.scheduled_at = registry.get_scheduled_time(job)

        return jobs

    def get(self, request, queue_index, status):
        queue = get_queue_by_index(queue_index)
        data = self.get_table_data(request, queue, status)
        table = self.get_table(data, request, False)

        # If this is an HTMX request, return only the rendered table HTML
        if request.htmx:
            return render(request, 'htmx/table.html', {
                'table': table,
            })

        return render(request, 'core/rq_task_list.html', {
            'table': table,
            'queue': queue,
            'status': status,
        })


class BackgroundTaskView(BaseRQView):

    def get(self, request, job_id):
        # all the RQ queues should use the same connection
        config = QUEUES_LIST[0]
        try:
            job = RQ_Job.fetch(job_id, connection=get_redis_connection(config['connection_config']),)
        except NoSuchJobError:
            raise Http404(_("Job {job_id} not found").format(job_id=job_id))

        queue_index = QUEUES_MAP[job.origin]
        queue = get_queue_by_index(queue_index)

        try:
            exc_info = job._exc_info
        except AttributeError:
            exc_info = None

        return render(request, 'core/rq_task.html', {
            'queue': queue,
            'job': job,
            'queue_index': queue_index,
            'dependency_id': job._dependency_id,
            'exc_info': exc_info,
        })


class BackgroundTaskDeleteView(BaseRQView):

    def get(self, request, job_id):
        if not request.htmx:
            return redirect(reverse('core:background_queue_list'))

        form = ConfirmationForm(initial=request.GET)

        return render(request, 'htmx/delete_form.html', {
            'object_type': 'background task',
            'object': job_id,
            'form': form,
            'form_url': reverse('core:background_task_delete', kwargs={'job_id': job_id})
        })

    def post(self, request, job_id):
        form = ConfirmationForm(request.POST)

        if form.is_valid():
            # all the RQ queues should use the same connection
            config = QUEUES_LIST[0]
            try:
                job = RQ_Job.fetch(job_id, connection=get_redis_connection(config['connection_config']),)
            except NoSuchJobError:
                raise Http404(_("Job {job_id} not found").format(job_id=job_id))

            queue_index = QUEUES_MAP[job.origin]
            queue = get_queue_by_index(queue_index)

            # Remove job id from queue and delete the actual job
            queue.connection.lrem(queue.key, 0, job.id)
            job.delete()
            messages.success(request, f'Deleted job {job_id}')
        else:
            messages.error(request, f'Error deleting job: {form.errors[0]}')

        return redirect(reverse('core:background_queue_list'))


class BackgroundTaskRequeueView(BaseRQView):

    def get(self, request, job_id):
        # all the RQ queues should use the same connection
        config = QUEUES_LIST[0]
        try:
            job = RQ_Job.fetch(job_id, connection=get_redis_connection(config['connection_config']),)
        except NoSuchJobError:
            raise Http404(_("Job {job_id} not found").format(job_id=job_id))

        queue_index = QUEUES_MAP[job.origin]
        queue = get_queue_by_index(queue_index)

        requeue_job(job_id, connection=queue.connection, serializer=queue.serializer)
        messages.success(request, f'You have successfully requeued: {job_id}')
        return redirect(reverse('core:background_task', args=[job_id]))


class BackgroundTaskEnqueueView(BaseRQView):

    def get(self, request, job_id):
        # all the RQ queues should use the same connection
        config = QUEUES_LIST[0]
        try:
            job = RQ_Job.fetch(job_id, connection=get_redis_connection(config['connection_config']),)
        except NoSuchJobError:
            raise Http404(_("Job {job_id} not found").format(job_id=job_id))

        queue_index = QUEUES_MAP[job.origin]
        queue = get_queue_by_index(queue_index)

        try:
            # _enqueue_job is new in RQ 1.14, this is used to enqueue
            # job regardless of its dependencies
            queue._enqueue_job(job)
        except AttributeError:
            queue.enqueue_job(job)

        # Remove job from correct registry if needed
        if job.get_status() == RQJobStatus.DEFERRED:
            registry = DeferredJobRegistry(queue.name, queue.connection)
            registry.remove(job)
        elif job.get_status() == RQJobStatus.FINISHED:
            registry = FinishedJobRegistry(queue.name, queue.connection)
            registry.remove(job)
        elif job.get_status() == RQJobStatus.SCHEDULED:
            registry = ScheduledJobRegistry(queue.name, queue.connection)
            registry.remove(job)

        messages.success(request, f'You have successfully enqueued: {job_id}')
        return redirect(reverse('core:background_task', args=[job_id]))


class BackgroundTaskStopView(BaseRQView):

    def get(self, request, job_id):
        # all the RQ queues should use the same connection
        config = QUEUES_LIST[0]
        try:
            job = RQ_Job.fetch(job_id, connection=get_redis_connection(config['connection_config']),)
        except NoSuchJobError:
            raise Http404(_("Job {job_id} not found").format(job_id=job_id))

        queue_index = QUEUES_MAP[job.origin]
        queue = get_queue_by_index(queue_index)

        stopped, _ = stop_jobs(queue, job_id)
        if len(stopped) == 1:
            messages.success(request, f'You have successfully stopped {job_id}')
        else:
            messages.error(request, f'Failed to stop {job_id}')

        return redirect(reverse('core:background_task', args=[job_id]))


class WorkerListView(TableMixin, BaseRQView):
    table = tables.WorkerTable

    def get_table_data(self, request, queue):
        clean_worker_registry(queue)
        all_workers = Worker.all(queue.connection)
        workers = [worker for worker in all_workers if queue.name in worker.queue_names()]
        return workers

    def get(self, request, queue_index):
        queue = get_queue_by_index(queue_index)
        data = self.get_table_data(request, queue)

        table = self.get_table(data, request, False)

        # If this is an HTMX request, return only the rendered table HTML
        if request.htmx:
            if request.htmx.target != 'object_list':
                table.embedded = True
                # Hide selection checkboxes
                if 'pk' in table.base_columns:
                    table.columns.hide('pk')
            return render(request, 'htmx/table.html', {
                'table': table,
                'queue': queue,
            })

        return render(request, 'core/rq_worker_list.html', {
            'table': table,
            'queue': queue,
        })


class WorkerView(BaseRQView):

    def get(self, request, key):
        # all the RQ queues should use the same connection
        config = QUEUES_LIST[0]
        worker = Worker.find_by_key('rq:worker:' + key, connection=get_redis_connection(config['connection_config']))
        # Convert microseconds to milliseconds
        worker.total_working_time = worker.total_working_time / 1000

        return render(request, 'core/rq_worker.html', {
            'worker': worker,
            'job': worker.get_current_job(),
            'total_working_time': worker.total_working_time * 1000,
        })


#
# Plugins
#

class PluginListView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        plugins = [
            # Look up app config by package name
            apps.get_app_config(plugin.rsplit('.', 1)[-1]) for plugin in settings.PLUGINS
        ]
        table = tables.PluginTable(plugins, user=request.user)
        table.configure(request)

        return render(request, 'core/plugin_list.html', {
            'plugins': plugins,
            'active_tab': 'api-tokens',
            'table': table,
        })
