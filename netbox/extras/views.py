from django import template
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View
from django_rq.queues import get_connection
from rq import Worker

from netbox.views import generic
from utilities.forms import ConfirmationForm
from utilities.tables import paginate_table
from utilities.utils import copy_safe_request, count_related, shallow_compare_dict
from utilities.views import ContentTypePermissionRequiredMixin
from . import filters, forms, tables
from .choices import JobResultStatusChoices
from .models import ConfigContext, ImageAttachment, JournalEntry, ObjectChange, JobResult, Tag, TaggedItem
from .reports import get_report, get_reports, run_report
from .scripts import get_scripts, run_script


#
# Tags
#

class TagListView(generic.ObjectListView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    filterset = filters.TagFilterSet
    filterset_form = forms.TagFilterForm
    table = tables.TagTable


class TagEditView(generic.ObjectEditView):
    queryset = Tag.objects.all()
    model_form = forms.TagForm


class TagDeleteView(generic.ObjectDeleteView):
    queryset = Tag.objects.all()


class TagBulkImportView(generic.BulkImportView):
    queryset = Tag.objects.all()
    model_form = forms.TagCSVForm
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
    filterset = filters.ConfigContextFilterSet
    filterset_form = forms.ConfigContextFilterForm
    table = tables.ConfigContextTable
    action_buttons = ('add',)


class ConfigContextView(generic.ObjectView):
    queryset = ConfigContext.objects.all()

    def get_extra_context(self, request, instance):
        # Determine user's preferred output format
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            if request.user.is_authenticated:
                request.user.config.set('extras.configcontext.format', format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get('extras.configcontext.format', 'json')
        else:
            format = 'json'

        return {
            'format': format,
        }


class ConfigContextEditView(generic.ObjectEditView):
    queryset = ConfigContext.objects.all()
    model_form = forms.ConfigContextForm
    template_name = 'extras/configcontext_edit.html'


class ConfigContextBulkEditView(generic.BulkEditView):
    queryset = ConfigContext.objects.all()
    filterset = filters.ConfigContextFilterSet
    table = tables.ConfigContextTable
    form = forms.ConfigContextBulkEditForm


class ConfigContextDeleteView(generic.ObjectDeleteView):
    queryset = ConfigContext.objects.all()


class ConfigContextBulkDeleteView(generic.BulkDeleteView):
    queryset = ConfigContext.objects.all()
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
                request.user.config.set('extras.configcontext.format', format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get('extras.configcontext.format', 'json')
        else:
            format = 'json'

        return {
            'rendered_context': instance.get_config_context(),
            'source_contexts': source_contexts,
            'format': format,
            'base_template': self.base_template,
            'active_tab': 'config-context',
        }


#
# Change logging
#

class ObjectChangeListView(generic.ObjectListView):
    queryset = ObjectChange.objects.all()
    filterset = filters.ObjectChangeFilterSet
    filterset_form = forms.ObjectChangeFilterForm
    table = tables.ObjectChangeTable
    template_name = 'extras/objectchange_list.html'
    action_buttons = ('export',)


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

        if instance.prechange_data and instance.postchange_data:
            diff_added = shallow_compare_dict(
                instance.prechange_data or dict(),
                instance.postchange_data or dict(),
                exclude=['last_updated'],
            )
            diff_removed = {
                x: instance.prechange_data.get(x) for x in diff_added
            } if instance.prechange_data else {}
        else:
            diff_added = None
            diff_removed = None

        return {
            'diff_added': diff_added,
            'diff_removed': diff_removed,
            'next_change': next_change,
            'prev_change': prev_change,
            'related_changes_table': related_changes_table,
            'related_changes_count': related_changes.count()
        }


class ObjectChangeLogView(View):
    """
    Present a history of changes made to a particular object.

    base_template: The name of the template to extend. If not provided, "<app>/<model>.html" will be used.
    """
    base_template = None

    def get(self, request, model, **kwargs):

        # Handle QuerySet restriction of parent object if needed
        if hasattr(model.objects, 'restrict'):
            obj = get_object_or_404(model.objects.restrict(request.user, 'view'), **kwargs)
        else:
            obj = get_object_or_404(model, **kwargs)

        # Gather all changes for this object (and its related objects)
        content_type = ContentType.objects.get_for_model(model)
        objectchanges = ObjectChange.objects.restrict(request.user, 'view').prefetch_related(
            'user', 'changed_object_type'
        ).filter(
            Q(changed_object_type=content_type, changed_object_id=obj.pk) |
            Q(related_object_type=content_type, related_object_id=obj.pk)
        )
        objectchanges_table = tables.ObjectChangeTable(
            data=objectchanges,
            orderable=False
        )
        paginate_table(objectchanges_table, request)

        # Default to using "<app>/<model>.html" as the template, if it exists. Otherwise,
        # fall back to using base.html.
        if self.base_template is None:
            self.base_template = f"{model._meta.app_label}/{model._meta.model_name}.html"
            # TODO: This can be removed once an object view has been established for every model.
            try:
                template.loader.get_template(self.base_template)
            except template.TemplateDoesNotExist:
                self.base_template = 'base.html'

        return render(request, 'extras/object_changelog.html', {
            'object': obj,
            'table': objectchanges_table,
            'base_template': self.base_template,
            'active_tab': 'changelog',
        })


#
# Image attachments
#

class ImageAttachmentEditView(generic.ObjectEditView):
    queryset = ImageAttachment.objects.all()
    model_form = forms.ImageAttachmentForm

    def alter_obj(self, imageattachment, request, args, kwargs):
        if not imageattachment.pk:
            # Assign the parent object based on URL kwargs
            model = kwargs.get('model')
            imageattachment.parent = get_object_or_404(model, pk=kwargs['object_id'])
        return imageattachment

    def get_return_url(self, request, imageattachment):
        return imageattachment.parent.get_absolute_url()


class ImageAttachmentDeleteView(generic.ObjectDeleteView):
    queryset = ImageAttachment.objects.all()

    def get_return_url(self, request, imageattachment):
        return imageattachment.parent.get_absolute_url()


#
# Journal entries
#

class JournalEntryListView(generic.ObjectListView):
    queryset = JournalEntry.objects.all()
    filterset = filters.JournalEntryFilterSet
    filterset_form = forms.JournalEntryFilterForm
    table = tables.JournalEntryTable
    action_buttons = ('export',)


class JournalEntryEditView(generic.ObjectEditView):
    queryset = JournalEntry.objects.all()
    model_form = forms.JournalEntryForm

    def alter_obj(self, obj, request, args, kwargs):
        if not obj.pk:
            obj.created_by = request.user
        return obj

    def get_return_url(self, request, instance):
        if not instance.assigned_object:
            return reverse('extras:journalentry_list')
        obj = instance.assigned_object
        viewname = f'{obj._meta.app_label}:{obj._meta.model_name}_journal'
        return reverse(viewname, kwargs={'pk': obj.pk})


class JournalEntryDeleteView(generic.ObjectDeleteView):
    queryset = JournalEntry.objects.all()

    def get_return_url(self, request, instance):
        obj = instance.assigned_object
        viewname = f'{obj._meta.app_label}:{obj._meta.model_name}_journal'
        return reverse(viewname, kwargs={'pk': obj.pk})


class JournalEntryBulkEditView(generic.BulkEditView):
    queryset = JournalEntry.objects.prefetch_related('created_by')
    filterset = filters.JournalEntryFilterSet
    table = tables.JournalEntryTable
    form = forms.JournalEntryBulkEditForm


class JournalEntryBulkDeleteView(generic.BulkDeleteView):
    queryset = JournalEntry.objects.prefetch_related('created_by')
    filterset = filters.JournalEntryFilterSet
    table = tables.JournalEntryTable


class ObjectJournalView(View):
    """
    Show all journal entries for an object.

    base_template: The name of the template to extend. If not provided, "<app>/<model>.html" will be used.
    """
    base_template = None

    def get(self, request, model, **kwargs):

        # Handle QuerySet restriction of parent object if needed
        if hasattr(model.objects, 'restrict'):
            obj = get_object_or_404(model.objects.restrict(request.user, 'view'), **kwargs)
        else:
            obj = get_object_or_404(model, **kwargs)

        # Gather all changes for this object (and its related objects)
        content_type = ContentType.objects.get_for_model(model)
        journalentries = JournalEntry.objects.restrict(request.user, 'view').prefetch_related('created_by').filter(
            assigned_object_type=content_type,
            assigned_object_id=obj.pk
        )
        journalentry_table = tables.ObjectJournalTable(
            data=journalentries,
            orderable=False
        )
        paginate_table(journalentry_table, request)

        if request.user.has_perm('extras.add_journalentry'):
            form = forms.JournalEntryForm(
                initial={
                    'assigned_object_type': ContentType.objects.get_for_model(obj),
                    'assigned_object_id': obj.pk
                }
            )
        else:
            form = None

        # Default to using "<app>/<model>.html" as the template, if it exists. Otherwise,
        # fall back to using base.html.
        if self.base_template is None:
            self.base_template = f"{model._meta.app_label}/{model._meta.model_name}.html"
            # TODO: This can be removed once an object view has been established for every model.
            try:
                template.loader.get_template(self.base_template)
            except template.TemplateDoesNotExist:
                self.base_template = 'base.html'

        return render(request, 'extras/object_journal.html', {
            'object': obj,
            'form': form,
            'table': journalentry_table,
            'base_template': self.base_template,
            'active_tab': 'journal',
        })


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
            ).defer('data')
        }

        ret = []
        for module, report_list in reports:
            module_reports = []
            for report in report_list:
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
            'run_form': ConfirmationForm(),
        })

    def post(self, request, module, name):

        # Permissions check
        if not request.user.has_perm('extras.run_report'):
            return HttpResponseForbidden()

        report = get_report(module, name)
        if report is None:
            raise Http404

        # Allow execution only if RQ worker process is running
        if not Worker.count(get_connection('default')):
            messages.error(request, "Unable to run report: RQ worker process not running.")
            return render(request, 'extras/report.html', {
                'report': report,
            })

        # Run the Report. A new JobResult is created.
        report_content_type = ContentType.objects.get(app_label='extras', model='report')
        job_result = JobResult.enqueue_job(
            run_report,
            report.full_name,
            report_content_type,
            request.user
        )

        return redirect('extras:report_result', job_result_pk=job_result.pk)


class ReportResultView(ContentTypePermissionRequiredMixin, View):
    """
    Display a JobResult pertaining to the execution of a Report.
    """
    def get_required_permission(self):
        return 'extras.view_report'

    def get(self, request, job_result_pk):
        report_content_type = ContentType.objects.get(app_label='extras', model='report')
        jobresult = get_object_or_404(JobResult.objects.all(), pk=job_result_pk, obj_type=report_content_type)

        # Retrieve the Report and attach the JobResult to it
        module, report_name = jobresult.name.split('.')
        report = get_report(module, report_name)
        report.result = jobresult

        return render(request, 'extras/report_result.html', {
            'report': report,
            'result': jobresult,
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
            ).defer('data')
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
        form = script.as_form(initial=request.GET)

        # Look for a pending JobResult (use the latest one by creation timestamp)
        script_content_type = ContentType.objects.get(app_label='extras', model='script')
        script.result = JobResult.objects.filter(
            obj_type=script_content_type,
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
            commit = form.cleaned_data.pop('_commit')

            script_content_type = ContentType.objects.get(app_label='extras', model='script')
            job_result = JobResult.enqueue_job(
                run_script,
                script.full_name,
                script_content_type,
                request.user,
                data=form.cleaned_data,
                request=copy_safe_request(request),
                commit=commit
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

        return render(request, 'extras/script_result.html', {
            'script': script,
            'result': result,
            'class_name': script.__class__.__name__
        })
