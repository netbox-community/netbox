from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django_tables2.data import TableListData

from core.choices import JobStatusChoices
from netbox.object_actions import BulkDelete, BulkExport, DeleteObject
from netbox.ui import layout
from netbox.ui.panels import ContextTablePanel
from netbox.views import generic
from utilities.htmx import htmx_partial
from utilities.paginator import get_paginate_count
from utilities.views import ContentTypePermissionRequiredMixin, GetReturnURLMixin, register_model_view

from . import filtersets, forms, tables
from .catalog import CatalogResults, annotate_entries, get_coverage
from .client import NOT_FOUND, error_of, get_client
from .importers import ImportAborted, get_importer, import_entries
from .jobs import ImportJob, SyncJob, get_active_sync_job, get_last_sync_job
from .models import ImportRecord
from .ui import panels
from .utils import get_web_url, is_enabled


def can_import(user):
    """
    Return True if the user may create any type of object which can be imported from the catalog.
    """
    from .importers import get_importers

    return any(
        user.has_perm(f'{importer.model._meta.app_label}.add_{importer.model._meta.model_name}')
        for importer in get_importers().values()
    )


class NDXView(ContentTypePermissionRequiredMixin, View):
    """
    Base class for views which interact with the NDX catalog.
    """
    def get_required_permission(self):
        return 'ndx.view_importrecord'

    def dispatch(self, request, *args, **kwargs):
        if not is_enabled():
            raise Http404(_("The NDX integration is not enabled."))
        return super().dispatch(request, *args, **kwargs)


#
# Catalog
#

class CatalogView(NDXView):
    """
    Browse and search the NDX catalog.
    """
    def get(self, request):
        client = get_client()
        filter_form = forms.CatalogFilterForm(
            request.GET,
            vendors=client.get_all_vendors(),
        )
        filter_form.is_valid()
        params = filter_form.cleaned_data if filter_form.is_bound else {}

        # Retrieve the requested page of results along with the total count
        per_page = get_paginate_count(request)
        try:
            page = max(int(request.GET.get('page', 1)), 1)
        except ValueError:
            page = 1

        results = CatalogResults(
            client,
            request.user,
            prefetch=((page - 1) * per_page, per_page),
            q=params.get('q') or None,
            vendor=params.get('vendor') or None,
            entry_type=params.get('type') or None,
        )
        # Wrap the results explicitly, as django-tables2 would otherwise evaluate the entire sequence
        table = tables.CatalogEntryTable(TableListData(results))
        table.configure(request)

        if htmx_partial(request):
            return render(request, 'htmx/table.html', {
                'table': table,
            })

        return render(request, 'ndx/catalog_list.html', {
            'table': table,
            'filter_form': filter_form,
            'catalog_error': results.error,
            'can_import': can_import(request.user),
        })


class CatalogEntryView(NDXView):
    """
    Display a single catalog entry.
    """
    def get(self, request, vendor_slug, slug):
        entry = get_client().get_entry(vendor_slug, slug)
        if error := error_of(entry):
            if error.kind == NOT_FOUND:
                raise Http404(_("Catalog entry {id} not found").format(id=f'{vendor_slug}/{slug}'))
            messages.error(request, error.message)
            return redirect('ndx:catalog')
        annotate_entries([entry], request.user)
        importer = get_importer(entry.get('type') or 'device-type')

        dtl = entry.get('dtl') or {}
        components = [
            (key, len(dtl[key])) for key in (
                'interfaces', 'console-ports', 'console-server-ports', 'power-ports', 'power-outlets', 'front-ports',
                'rear-ports', 'module-bays', 'device-bays', 'inventory-items',
            ) if dtl.get(key)
        ]

        return render(request, 'ndx/catalog_entry.html', {
            'entry': entry,
            'dtl': dtl,
            'importer': importer,
            'components': components,
            'interfaces': dtl.get('interfaces') or [],
            'coverage': get_coverage(entry),
            'can_import': importer is not None and can_import(request.user),
            'ndx_web_url': get_web_url(),
        })


class CatalogImportView(GetReturnURLMixin, NDXView):
    """
    Import one or more catalog entries. A single entry is imported immediately; multiple entries are imported by a
    background job.
    """
    def post(self, request):
        if not can_import(request.user):
            raise PermissionDenied(_("You do not have permission to import catalog entries."))

        ndx_ids = request.POST.getlist('pk')
        if not ndx_ids:
            messages.warning(request, _("No catalog entries were selected."))
            return redirect(self.get_return_url(request))

        if len(ndx_ids) > 1:
            job = ImportJob.enqueue_for(request, ndx_ids)
            messages.success(request, _("Queued job #{id} to import {count} catalog entries").format(
                id=job.pk, count=len(ndx_ids)
            ))
            return redirect(job.get_absolute_url())

        try:
            result = import_entries(ndx_ids, request.user)[0]
        except ImportAborted as e:
            messages.error(request, _("Import aborted: {error}").format(error=e))
            return redirect(self.get_return_url(request))

        if not result.success:
            if result.skipped:
                messages.warning(request, result.message)
            else:
                messages.error(request, _("Failed to import {id}: {errors}").format(
                    id=result.ndx_id, errors='; '.join(map(str, result.errors))
                ))
            return redirect(self.get_return_url(request))

        messages.success(request, result.message)
        for msg in [*result.warnings, *result.component_errors, *result.image_errors]:
            messages.warning(request, msg)
        return redirect(result.object.get_absolute_url())


#
# Sync status
#

class SyncStatusView(NDXView):
    """
    Display the status of catalog synchronization.
    """
    def get(self, request):
        client = get_client()
        auth = client.verify_auth(use_cache=True)
        records = ImportRecord.objects.restrict(request.user, 'view')
        jobs = SyncJob.get_jobs()
        job = get_last_sync_job()
        job_data = job.data if job and isinstance(job.data, dict) else {}

        return render(request, 'ndx/sync_status.html', {
            'api_url': client.api_url,
            'auth_error': error_of(auth),
            'tier': auth.get('tier') or job_data.get('tier'),
            'job': job,
            'catalog_count': job_data.get('catalog_count'),
            'flagged_count': job_data.get('flagged'),
            'sync_error': job.error or job_data.get('error') if job else None,
            'running_job': get_active_sync_job(),
            'next_job': jobs.filter(status=JobStatusChoices.STATUS_SCHEDULED).order_by('scheduled').first(),
            'imported_count': records.count(),
            'updates_available': records.filter(update_available=True).count(),
            'can_import': can_import(request.user),
        })


class SyncView(NDXView):
    """
    Queue a catalog sync job.
    """
    def get_required_permission(self):
        return 'ndx.sync_importrecord'

    def post(self, request):
        if job := get_active_sync_job():
            messages.info(request, _("A catalog sync is already in progress (job #{id})").format(id=job.pk))
        else:
            job = SyncJob.enqueue(user=request.user)
            messages.success(request, _("Queued job #{id} to sync with the NDX catalog").format(id=job.pk))
        return redirect('ndx:sync_status')


class ApplyUpdatesView(NDXView):
    """
    Re-import all imported entries for which the catalog has an update available.
    """
    def post(self, request):
        if not can_import(request.user):
            raise PermissionDenied(_("You do not have permission to import catalog entries."))

        ndx_ids = list(
            ImportRecord.objects.restrict(request.user, 'view').filter(update_available=True)
            .values_list('ndx_id', flat=True)
        )
        if not ndx_ids:
            messages.info(request, _("No updates are available."))
            return redirect('ndx:sync_status')

        job = ImportJob.enqueue_for(request, ndx_ids)
        messages.success(request, _("Queued job #{id} to update {count} imported entries").format(
            id=job.pk, count=len(ndx_ids)
        ))
        return redirect(job.get_absolute_url())


#
# Import records
#

@register_model_view(ImportRecord, 'list', path='', detail=False)
class ImportRecordListView(generic.ObjectListView):
    queryset = ImportRecord.objects.all()
    filterset = filtersets.ImportRecordFilterSet
    filterset_form = forms.ImportRecordFilterForm
    table = tables.ImportRecordTable
    actions = (BulkExport, BulkDelete)


@register_model_view(ImportRecord)
class ImportRecordView(generic.ObjectView):
    queryset = ImportRecord.objects.select_related('enrichment')
    actions = (DeleteObject,)
    layout = layout.Layout(
        layout.Row(
            layout.Column(
                panels.ImportRecordAttributesPanel(),
                panels.EnrichmentLifecyclePanel(),
                panels.EnrichmentPlatformPanel(),
            ),
            layout.Column(
                panels.EnrichmentPowerThermalPanel(),
                panels.EnrichmentEnvironmentalPanel(),
            ),
        ),
        layout.Row(
            layout.Column(
                ContextTablePanel('provenance_table', title=_('Provenance')),
                panels.EnrichmentExtensionsPanel(),
            ),
        ),
    )

    def get_extra_context(self, request, instance):
        enrichment = getattr(instance, 'enrichment', None)
        provenance_table = None
        if enrichment is not None and enrichment.provenance.exists():
            provenance_table = tables.ProvenanceTable(enrichment.provenance.all(), orderable=False)
            provenance_table.configure(request)
        return {
            'provenance_table': provenance_table,
            'catalog_url': reverse('ndx:catalog_entry', kwargs={
                'vendor_slug': instance.vendor_slug, 'slug': instance.slug
            }) if is_enabled() else None,
            'ndx_web_url': get_web_url(),
            'can_import': is_enabled() and can_import(request.user),
        }


@register_model_view(ImportRecord, 'delete')
class ImportRecordDeleteView(generic.ObjectDeleteView):
    queryset = ImportRecord.objects.all()


@register_model_view(ImportRecord, 'bulk_delete', path='delete', detail=False)
class ImportRecordBulkDeleteView(generic.BulkDeleteView):
    queryset = ImportRecord.objects.all()
    filterset = filtersets.ImportRecordFilterSet
    table = tables.ImportRecordTable
