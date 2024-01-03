from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from netbox.config import get_config, PARAMS
from netbox.views import generic
from netbox.views.generic.base import BaseObjectView
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
                data=get_config()
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
