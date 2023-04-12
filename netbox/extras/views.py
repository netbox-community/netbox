from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View
from django_rq.queues import get_connection
from rq import Worker

from netbox.views import generic
from utilities.htmx import is_htmx
from utilities.templatetags.builtins.filters import render_markdown
from utilities.utils import copy_safe_request, count_related, get_viewname, normalize_querydict, shallow_compare_dict
from utilities.views import ContentTypePermissionRequiredMixin, register_model_view
from . import filtersets, forms, tables
from .choices import JobResultStatusChoices
from .forms.reports import ReportForm
from .models import *
from .reports import get_report, get_reports, run_report
from .scripts import get_scripts, run_script


#
# Custom fields
#

class CustomFieldListView(generic.ObjectListView):
    queryset = CustomField.objects.all()
    filterset = filtersets.CustomFieldFilterSet
    filterset_form = forms.CustomFieldFilterForm
    table = tables.CustomFieldTable


@register_model_view(CustomField)
class CustomFieldView(generic.ObjectView):
    queryset = CustomField.objects.all()


@register_model_view(CustomField, 'edit')
class CustomFieldEditView(generic.ObjectEditView):
    queryset = CustomField.objects.all()
    form = forms.CustomFieldForm


@register_model_view(CustomField, 'delete')
class CustomFieldDeleteView(generic.ObjectDeleteView):
    queryset = CustomField.objects.all()


class CustomFieldBulkImportView(generic.BulkImportView):
    queryset = CustomField.objects.all()
    model_form = forms.CustomFieldImportForm
    table = tables.CustomFieldTable


class CustomFieldBulkEditView(generic.BulkEditView):
    queryset = CustomField.objects.all()
    filterset = filtersets.CustomFieldFilterSet
    table = tables.CustomFieldTable
    form = forms.CustomFieldBulkEditForm


class CustomFieldBulkDeleteView(generic.BulkDeleteView):
    queryset = CustomField.objects.all()
    filterset = filtersets.CustomFieldFilterSet
    table = tables.CustomFieldTable


#
# Custom links
#

class CustomLinkListView(generic.ObjectListView):
    queryset = CustomLink.objects.all()
    filterset = filtersets.CustomLinkFilterSet
    filterset_form = forms.CustomLinkFilterForm
    table = tables.CustomLinkTable


@register_model_view(CustomLink)
class CustomLinkView(generic.ObjectView):
    queryset = CustomLink.objects.all()


@register_model_view(CustomLink, 'edit')
class CustomLinkEditView(generic.ObjectEditView):
    queryset = CustomLink.objects.all()
    form = forms.CustomLinkForm


@register_model_view(CustomLink, 'delete')
class CustomLinkDeleteView(generic.ObjectDeleteView):
    queryset = CustomLink.objects.all()


class CustomLinkBulkImportView(generic.BulkImportView):
    queryset = CustomLink.objects.all()
    model_form = forms.CustomLinkImportForm
    table = tables.CustomLinkTable


class CustomLinkBulkEditView(generic.BulkEditView):
    queryset = CustomLink.objects.all()
    filterset = filtersets.CustomLinkFilterSet
    table = tables.CustomLinkTable
    form = forms.CustomLinkBulkEditForm


class CustomLinkBulkDeleteView(generic.BulkDeleteView):
    queryset = CustomLink.objects.all()
    filterset = filtersets.CustomLinkFilterSet
    table = tables.CustomLinkTable


#
# Export templates
#

class ExportTemplateListView(generic.ObjectListView):
    queryset = ExportTemplate.objects.all()
    filterset = filtersets.ExportTemplateFilterSet
    filterset_form = forms.ExportTemplateFilterForm
    table = tables.ExportTemplateTable


@register_model_view(ExportTemplate)
class ExportTemplateView(generic.ObjectView):
    queryset = ExportTemplate.objects.all()


@register_model_view(ExportTemplate, 'edit')
class ExportTemplateEditView(generic.ObjectEditView):
    queryset = ExportTemplate.objects.all()
    form = forms.ExportTemplateForm


@register_model_view(ExportTemplate, 'delete')
class ExportTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ExportTemplate.objects.all()


class ExportTemplateBulkImportView(generic.BulkImportView):
    queryset = ExportTemplate.objects.all()
    model_form = forms.ExportTemplateImportForm
    table = tables.ExportTemplateTable


class ExportTemplateBulkEditView(generic.BulkEditView):
    queryset = ExportTemplate.objects.all()
    filterset = filtersets.ExportTemplateFilterSet
    table = tables.ExportTemplateTable
    form = forms.ExportTemplateBulkEditForm


class ExportTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = ExportTemplate.objects.all()
    filterset = filtersets.ExportTemplateFilterSet
    table = tables.ExportTemplateTable


#
# Saved filters
#

class SavedFilterMixin:

    def get_queryset(self, request):
        """
        Return only shared SavedFilters, or those owned by the current user, unless
        this is a superuser.
        """
        queryset = SavedFilter.objects.all()
        user = request.user
        if user.is_superuser:
            return queryset
        if user.is_anonymous:
            return queryset.filter(shared=True)
        return queryset.filter(
            Q(shared=True) | Q(user=user)
        )


class SavedFilterListView(SavedFilterMixin, generic.ObjectListView):
    filterset = filtersets.SavedFilterFilterSet
    filterset_form = forms.SavedFilterFilterForm
    table = tables.SavedFilterTable


@register_model_view(SavedFilter)
class SavedFilterView(SavedFilterMixin, generic.ObjectView):
    queryset = SavedFilter.objects.all()


@register_model_view(SavedFilter, 'edit')
class SavedFilterEditView(SavedFilterMixin, generic.ObjectEditView):
    queryset = SavedFilter.objects.all()
    form = forms.SavedFilterForm

    def alter_object(self, obj, request, url_args, url_kwargs):
        if not obj.pk:
            obj.user = request.user
        return obj


@register_model_view(SavedFilter, 'delete')
class SavedFilterDeleteView(SavedFilterMixin, generic.ObjectDeleteView):
    queryset = SavedFilter.objects.all()


class SavedFilterBulkImportView(SavedFilterMixin, generic.BulkImportView):
    queryset = SavedFilter.objects.all()
    model_form = forms.SavedFilterImportForm
    table = tables.SavedFilterTable


class SavedFilterBulkEditView(SavedFilterMixin, generic.BulkEditView):
    queryset = SavedFilter.objects.all()
    filterset = filtersets.SavedFilterFilterSet
    table = tables.SavedFilterTable
    form = forms.SavedFilterBulkEditForm


class SavedFilterBulkDeleteView(SavedFilterMixin, generic.BulkDeleteView):
    queryset = SavedFilter.objects.all()
    filterset = filtersets.SavedFilterFilterSet
    table = tables.SavedFilterTable


#
# Webhooks
#

class WebhookListView(generic.ObjectListView):
    queryset = Webhook.objects.all()
    filterset = filtersets.WebhookFilterSet
    filterset_form = forms.WebhookFilterForm
    table = tables.WebhookTable


@register_model_view(Webhook)
class WebhookView(generic.ObjectView):
    queryset = Webhook.objects.all()


@register_model_view(Webhook, 'edit')
class WebhookEditView(generic.ObjectEditView):
    queryset = Webhook.objects.all()
    form = forms.WebhookForm


@register_model_view(Webhook, 'delete')
class WebhookDeleteView(generic.ObjectDeleteView):
    queryset = Webhook.objects.all()


class WebhookBulkImportView(generic.BulkImportView):
    queryset = Webhook.objects.all()
    model_form = forms.WebhookImportForm
    table = tables.WebhookTable


class WebhookBulkEditView(generic.BulkEditView):
    queryset = Webhook.objects.all()
    filterset = filtersets.WebhookFilterSet
    table = tables.WebhookTable
    form = forms.WebhookBulkEditForm


class WebhookBulkDeleteView(generic.BulkDeleteView):
    queryset = Webhook.objects.all()
    filterset = filtersets.WebhookFilterSet
    table = tables.WebhookTable


#
# Tags
#

class TagListView(generic.ObjectListView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    filterset = filtersets.TagFilterSet
    filterset_form = forms.TagFilterForm
    table = tables.TagTable


@register_model_view(Tag)
class TagView(generic.ObjectView):
    queryset = Tag.objects.all()

    def get_extra_context(self, request, instance):
        tagged_items = TaggedItem.objects.filter(tag=instance)
        taggeditem_table = tables.TaggedItemTable(
            data=tagged_items,
            orderable=False
        )
        taggeditem_table.configure(request)

        object_types = [
            {
                'content_type': ContentType.objects.get(pk=ti['content_type']),
                'item_count': ti['item_count']
            } for ti in tagged_items.values('content_type').annotate(item_count=Count('pk'))
        ]

        return {
            'taggeditem_table': taggeditem_table,
            'tagged_item_count': tagged_items.count(),
            'object_types': object_types,
        }


@register_model_view(Tag, 'edit')
class TagEditView(generic.ObjectEditView):
    queryset = Tag.objects.all()
    form = forms.TagForm


@register_model_view(Tag, 'delete')
class TagDeleteView(generic.ObjectDeleteView):
    queryset = Tag.objects.all()


class TagBulkImportView(generic.BulkImportView):
    queryset = Tag.objects.all()
    model_form = forms.TagImportForm
    table = tables.TagTable


class TagBulkEditView(generic.BulkEditView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    table = tables.TagTable
    form = forms.TagBulkEditForm


class TagBulkDeleteView(generic.BulkDeleteView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    table = tables.TagTable


#
# Config contexts
#

class ConfigContextListView(generic.ObjectListView):
    queryset = ConfigContext.objects.all()
    filterset = filtersets.ConfigContextFilterSet
    filterset_form = forms.ConfigContextFilterForm
    table = tables.ConfigContextTable
    actions = ('add', 'bulk_edit', 'bulk_delete')


@register_model_view(ConfigContext)
class ConfigContextView(generic.ObjectView):
    queryset = ConfigContext.objects.all()

    def get_extra_context(self, request, instance):
        # Gather assigned objects for parsing in the template
        assigned_objects = (
            ('Regions', instance.regions.all),
            ('Site Groups', instance.site_groups.all),
            ('Sites', instance.sites.all),
            ('Locations', instance.locations.all),
            ('Device Types', instance.device_types.all),
            ('Roles', instance.roles.all),
            ('Platforms', instance.platforms.all),
            ('Cluster Types', instance.cluster_types.all),
            ('Cluster Groups', instance.cluster_groups.all),
            ('Clusters', instance.clusters.all),
            ('Tenant Groups', instance.tenant_groups.all),
            ('Tenants', instance.tenants.all),
            ('Tags', instance.tags.all),
        )

        # Determine user's preferred output format
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            if request.user.is_authenticated:
                request.user.config.set('data_format', format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get('data_format', 'json')
        else:
            format = 'json'

        return {
            'assigned_objects': assigned_objects,
            'format': format,
        }


@register_model_view(ConfigContext, 'edit')
class ConfigContextEditView(generic.ObjectEditView):
    queryset = ConfigContext.objects.all()
    form = forms.ConfigContextForm


class ConfigContextBulkEditView(generic.BulkEditView):
    queryset = ConfigContext.objects.all()
    filterset = filtersets.ConfigContextFilterSet
    table = tables.ConfigContextTable
    form = forms.ConfigContextBulkEditForm


@register_model_view(ConfigContext, 'delete')
class ConfigContextDeleteView(generic.ObjectDeleteView):
    queryset = ConfigContext.objects.all()


class ConfigContextBulkDeleteView(generic.BulkDeleteView):
    queryset = ConfigContext.objects.all()
    filterset = filtersets.ConfigContextFilterSet
    table = tables.ConfigContextTable


class ObjectConfigContextView(generic.ObjectView):
    base_template = None
    template_name = 'extras/object_configcontext.html'

    def get_extra_context(self, request, instance):
        source_contexts = ConfigContext.objects.restrict(request.user, 'view').get_for_object(instance)

        # Determine user's preferred output format
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            if request.user.is_authenticated:
                request.user.config.set('data_format', format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get('data_format', 'json')
        else:
            format = 'json'

        return {
            'rendered_context': instance.get_config_context(),
            'source_contexts': source_contexts,
            'format': format,
            'base_template': self.base_template,
        }


#
# Change logging
#

class ObjectChangeListView(generic.ObjectListView):
    queryset = ObjectChange.objects.all()
    filterset = filtersets.ObjectChangeFilterSet
    filterset_form = forms.ObjectChangeFilterForm
    table = tables.ObjectChangeTable
    template_name = 'extras/objectchange_list.html'
    actions = ('export',)


@register_model_view(ObjectChange)
class ObjectChangeView(generic.ObjectView):
    queryset = ObjectChange.objects.all()

    def get_extra_context(self, request, instance):
        related_changes = ObjectChange.objects.restrict(request.user, 'view').filter(
            request_id=instance.request_id
        ).exclude(
            pk=instance.pk
        )
        related_changes_table = tables.ObjectChangeTable(
            data=related_changes[:50],
            orderable=False
        )

        objectchanges = ObjectChange.objects.restrict(request.user, 'view').filter(
            changed_object_type=instance.changed_object_type,
            changed_object_id=instance.changed_object_id,
        )

        next_change = objectchanges.filter(time__gt=instance.time).order_by('time').first()
        prev_change = objectchanges.filter(time__lt=instance.time).order_by('-time').first()

        if not instance.prechange_data and instance.action in ['update', 'delete'] and prev_change:
            non_atomic_change = True
            prechange_data = prev_change.postchange_data
        else:
            non_atomic_change = False
            prechange_data = instance.prechange_data

        if prechange_data and instance.postchange_data:
            diff_added = shallow_compare_dict(
                prechange_data or dict(),
                instance.postchange_data or dict(),
                exclude=['last_updated'],
            )
            diff_removed = {
                x: prechange_data.get(x) for x in diff_added
            } if prechange_data else {}
        else:
            diff_added = None
            diff_removed = None

        return {
            'diff_added': diff_added,
            'diff_removed': diff_removed,
            'next_change': next_change,
            'prev_change': prev_change,
            'related_changes_table': related_changes_table,
            'related_changes_count': related_changes.count(),
            'non_atomic_change': non_atomic_change
        }


#
# Image attachments
#

@register_model_view(ImageAttachment, 'edit')
class ImageAttachmentEditView(generic.ObjectEditView):
    queryset = ImageAttachment.objects.all()
    form = forms.ImageAttachmentForm
    template_name = 'extras/imageattachment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the parent object based on URL kwargs
            content_type = get_object_or_404(ContentType, pk=request.GET.get('content_type'))
            instance.parent = get_object_or_404(content_type.model_class(), pk=request.GET.get('object_id'))
        return instance

    def get_return_url(self, request, obj=None):
        return obj.parent.get_absolute_url() if obj else super().get_return_url(request)

    def get_extra_addanother_params(self, request):
        return {
            'content_type': request.GET.get('content_type'),
            'object_id': request.GET.get('object_id'),
        }


@register_model_view(ImageAttachment, 'delete')
class ImageAttachmentDeleteView(generic.ObjectDeleteView):
    queryset = ImageAttachment.objects.all()

    def get_return_url(self, request, obj=None):
        return obj.parent.get_absolute_url() if obj else super().get_return_url(request)


#
# Journal entries
#

class JournalEntryListView(generic.ObjectListView):
    queryset = JournalEntry.objects.all()
    filterset = filtersets.JournalEntryFilterSet
    filterset_form = forms.JournalEntryFilterForm
    table = tables.JournalEntryTable
    actions = ('export', 'bulk_edit', 'bulk_delete')


@register_model_view(JournalEntry)
class JournalEntryView(generic.ObjectView):
    queryset = JournalEntry.objects.all()


@register_model_view(JournalEntry, 'edit')
class JournalEntryEditView(generic.ObjectEditView):
    queryset = JournalEntry.objects.all()
    form = forms.JournalEntryForm

    def alter_object(self, obj, request, args, kwargs):
        if not obj.pk:
            obj.created_by = request.user
        return obj

    def get_return_url(self, request, instance):
        if not instance.assigned_object:
            return reverse('extras:journalentry_list')
        obj = instance.assigned_object
        viewname = get_viewname(obj, 'journal')
        return reverse(viewname, kwargs={'pk': obj.pk})


@register_model_view(JournalEntry, 'delete')
class JournalEntryDeleteView(generic.ObjectDeleteView):
    queryset = JournalEntry.objects.all()

    def get_return_url(self, request, instance):
        obj = instance.assigned_object
        viewname = get_viewname(obj, 'journal')
        return reverse(viewname, kwargs={'pk': obj.pk})


class JournalEntryBulkEditView(generic.BulkEditView):
    queryset = JournalEntry.objects.all()
    filterset = filtersets.JournalEntryFilterSet
    table = tables.JournalEntryTable
    form = forms.JournalEntryBulkEditForm


class JournalEntryBulkDeleteView(generic.BulkDeleteView):
    queryset = JournalEntry.objects.all()
    filterset = filtersets.JournalEntryFilterSet
    table = tables.JournalEntryTable


#
# Reports
#

class ReportListView(ContentTypePermissionRequiredMixin, View):
    """
    Retrieve all of the available reports from disk and the recorded JobResult (if any) for each.
    """
    def get_required_permission(self):
        return 'extras.view_report'

    def get(self, request):

        reports = get_reports()
        report_content_type = ContentType.objects.get(app_label='extras', model='report')
        results = {
            r.name: r
            for r in JobResult.objects.filter(
                obj_type=report_content_type,
                status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
            ).order_by('name', '-created').distinct('name').defer('data')
        }

        ret = []

        for module, report_list in reports.items():
            module_reports = []
            for report in report_list.values():
                report.result = results.get(report.full_name, None)
                module_reports.append(report)
            ret.append((module, module_reports))

        return render(request, 'extras/report_list.html', {
            'reports': ret,
        })


class ReportView(ContentTypePermissionRequiredMixin, View):
    """
    Display a single Report and its associated JobResult (if any).
    """
    def get_required_permission(self):
        return 'extras.view_report'

    def get(self, request, module, name):

        report = get_report(module, name)
        if report is None:
            raise Http404

        report_content_type = ContentType.objects.get(app_label='extras', model='report')
        report.result = JobResult.objects.filter(
            obj_type=report_content_type,
            name=report.full_name,
            status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
        ).first()

        return render(request, 'extras/report.html', {
            'report': report,
            'form': ReportForm(),
        })

    def post(self, request, module, name):

        # Permissions check
        if not request.user.has_perm('extras.run_report'):
            return HttpResponseForbidden()

        report = get_report(module, name)
        if report is None:
            raise Http404

        form = ReportForm(request.POST)

        if form.is_valid():

            # Allow execution only if RQ worker process is running
            if not Worker.count(get_connection('default')):
                messages.error(request, "Unable to run report: RQ worker process not running.")
                return render(request, 'extras/report.html', {
                    'report': report,
                })

            # Run the Report. A new JobResult is created.
            job_result = JobResult.enqueue_job(
                run_report,
                name=report.full_name,
                obj_type=ContentType.objects.get_for_model(Report),
                user=request.user,
                schedule_at=form.cleaned_data.get('schedule_at'),
                interval=form.cleaned_data.get('interval'),
                job_timeout=report.job_timeout
            )

            return redirect('extras:report_result', job_result_pk=job_result.pk)

        return render(request, 'extras/report.html', {
            'report': report,
            'form': form,
        })


class ReportResultView(ContentTypePermissionRequiredMixin, View):
    """
    Display a JobResult pertaining to the execution of a Report.
    """
    def get_required_permission(self):
        return 'extras.view_report'

    def get(self, request, job_result_pk):
        report_content_type = ContentType.objects.get(app_label='extras', model='report')
        result = get_object_or_404(JobResult.objects.all(), pk=job_result_pk, obj_type=report_content_type)

        # Retrieve the Report and attach the JobResult to it
        module, report_name = result.name.split('.', maxsplit=1)
        report = get_report(module, report_name)
        report.result = result

        # If this is an HTMX request, return only the result HTML
        if is_htmx(request):
            response = render(request, 'extras/htmx/report_result.html', {
                'report': report,
                'result': result,
            })
            if result.completed or not result.started:
                response.status_code = 286
            return response

        return render(request, 'extras/report_result.html', {
            'report': report,
            'result': result,
        })


#
# Scripts
#

class GetScriptMixin:
    def _get_script(self, name, module=None):
        if module is None:
            module, name = name.split('.', 1)
        scripts = get_scripts()
        try:
            return scripts[module][name]()
        except KeyError:
            raise Http404


class ScriptListView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'extras.view_script'

    def get(self, request):

        scripts = get_scripts(use_names=True)
        script_content_type = ContentType.objects.get(app_label='extras', model='script')
        results = {
            r.name: r
            for r in JobResult.objects.filter(
                obj_type=script_content_type,
                status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
            ).order_by('name', '-created').distinct('name').defer('data')
        }

        for _scripts in scripts.values():
            for script in _scripts.values():
                script.result = results.get(script.full_name)

        return render(request, 'extras/script_list.html', {
            'scripts': scripts,
        })


class ScriptView(ContentTypePermissionRequiredMixin, GetScriptMixin, View):

    def get_required_permission(self):
        return 'extras.view_script'

    def get(self, request, module, name):
        script = self._get_script(name, module)
        form = script.as_form(initial=normalize_querydict(request.GET))

        # Look for a pending JobResult (use the latest one by creation timestamp)
        script.result = JobResult.objects.filter(
            obj_type=ContentType.objects.get_for_model(Script),
            name=script.full_name,
        ).exclude(
            status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
        ).first()

        return render(request, 'extras/script.html', {
            'module': module,
            'script': script,
            'form': form,
        })

    def post(self, request, module, name):

        # Permissions check
        if not request.user.has_perm('extras.run_script'):
            return HttpResponseForbidden()

        script = self._get_script(name, module)
        form = script.as_form(request.POST, request.FILES)

        # Allow execution only if RQ worker process is running
        if not Worker.count(get_connection('default')):
            messages.error(request, "Unable to run script: RQ worker process not running.")

        elif form.is_valid():
            job_result = JobResult.enqueue_job(
                run_script,
                name=script.full_name,
                obj_type=ContentType.objects.get_for_model(Script),
                user=request.user,
                schedule_at=form.cleaned_data.pop('_schedule_at'),
                interval=form.cleaned_data.pop('_interval'),
                data=form.cleaned_data,
                request=copy_safe_request(request),
                job_timeout=script.job_timeout,
                commit=form.cleaned_data.pop('_commit')
            )

            return redirect('extras:script_result', job_result_pk=job_result.pk)

        return render(request, 'extras/script.html', {
            'module': module,
            'script': script,
            'form': form,
        })


class ScriptResultView(ContentTypePermissionRequiredMixin, GetScriptMixin, View):

    def get_required_permission(self):
        return 'extras.view_script'

    def get(self, request, job_result_pk):
        result = get_object_or_404(JobResult.objects.all(), pk=job_result_pk)
        script_content_type = ContentType.objects.get(app_label='extras', model='script')
        if result.obj_type != script_content_type:
            raise Http404

        script = self._get_script(result.name)

        # If this is an HTMX request, return only the result HTML
        if is_htmx(request):
            response = render(request, 'extras/htmx/script_result.html', {
                'script': script,
                'result': result,
            })
            if result.completed or not result.started:
                response.status_code = 286
            return response

        return render(request, 'extras/script_result.html', {
            'script': script,
            'result': result,
            'class_name': script.__class__.__name__
        })


#
# Job results
#

class JobResultListView(generic.ObjectListView):
    queryset = JobResult.objects.all()
    filterset = filtersets.JobResultFilterSet
    filterset_form = forms.JobResultFilterForm
    table = tables.JobResultTable
    actions = ('export', 'delete', 'bulk_delete', )


class JobResultDeleteView(generic.ObjectDeleteView):
    queryset = JobResult.objects.all()


class JobResultBulkDeleteView(generic.BulkDeleteView):
    queryset = JobResult.objects.all()
    filterset = filtersets.JobResultFilterSet
    table = tables.JobResultTable


#
# Markdown
#

class RenderMarkdownView(View):

    def post(self, request):
        form = forms.RenderMarkdownForm(request.POST)
        if not form.is_valid():
            HttpResponseBadRequest()
        rendered = render_markdown(form.cleaned_data['text'])

        return HttpResponse(rendered)
