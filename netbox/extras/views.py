from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.generic import View
from django_tables2 import RequestConfig

from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator
from utilities.utils import shallow_compare_dict
from utilities.views import BulkDeleteView, BulkEditView, ObjectDeleteView, ObjectEditView, ObjectListView
from . import filters, forms
from .models import ConfigContext, ImageAttachment, ObjectChange, ReportResult, Tag, TaggedItem
from .reports import get_report, get_reports
from .scripts import get_scripts, run_script
from .tables import ConfigContextTable, ObjectChangeTable, TagTable, TaggedItemTable


#
# Tags
#

class TagListView(ObjectListView):
    queryset = Tag.objects.annotate(
        items=Count('extras_taggeditem_items', distinct=True)
    ).order_by(
        'name'
    )
    filterset = filters.TagFilterSet
    filterset_form = forms.TagFilterForm
    table = TagTable
    action_buttons = ()


class TagView(PermissionRequiredMixin, View):
    permission_required = 'extras.view_tag'

    def get(self, request, slug):

        tag = get_object_or_404(Tag, slug=slug)
        tagged_items = TaggedItem.objects.filter(
            tag=tag
        ).prefetch_related(
            'content_type', 'content_object'
        )

        # Generate a table of all items tagged with this Tag
        items_table = TaggedItemTable(tagged_items)
        paginate = {
            'paginator_class': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(items_table)

        return render(request, 'extras/tag.html', {
            'tag': tag,
            'items_count': tagged_items.count(),
            'items_table': items_table,
        })


class TagEditView(ObjectEditView):
    queryset = Tag.objects.all()
    model_form = forms.TagForm
    default_return_url = 'extras:tag_list'
    template_name = 'extras/tag_edit.html'


class TagDeleteView(ObjectDeleteView):
    queryset = Tag.objects.all()
    default_return_url = 'extras:tag_list'


class TagBulkEditView(BulkEditView):
    queryset = Tag.objects.annotate(
        items=Count('extras_taggeditem_items', distinct=True)
    ).order_by(
        'name'
    )
    table = TagTable
    form = forms.TagBulkEditForm
    default_return_url = 'extras:tag_list'


class TagBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'extras.delete_tag'
    queryset = Tag.objects.annotate(
        items=Count('extras_taggeditem_items')
    ).order_by(
        'name'
    )
    table = TagTable
    default_return_url = 'extras:tag_list'


#
# Config contexts
#

class ConfigContextListView(ObjectListView):
    queryset = ConfigContext.objects.all()
    filterset = filters.ConfigContextFilterSet
    filterset_form = forms.ConfigContextFilterForm
    table = ConfigContextTable
    action_buttons = ('add',)


class ConfigContextView(PermissionRequiredMixin, View):
    permission_required = 'extras.view_configcontext'

    def get(self, request, pk):
        configcontext = get_object_or_404(ConfigContext, pk=pk)

        # Determine user's preferred output format
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            request.user.config.set('extras.configcontext.format', format, commit=True)
        else:
            format = request.user.config.get('extras.configcontext.format', 'json')

        return render(request, 'extras/configcontext.html', {
            'configcontext': configcontext,
            'format': format,
        })


class ConfigContextEditView(ObjectEditView):
    queryset = ConfigContext.objects.all()
    model_form = forms.ConfigContextForm
    default_return_url = 'extras:configcontext_list'
    template_name = 'extras/configcontext_edit.html'


class ConfigContextBulkEditView(BulkEditView):
    queryset = ConfigContext.objects.all()
    filterset = filters.ConfigContextFilterSet
    table = ConfigContextTable
    form = forms.ConfigContextBulkEditForm
    default_return_url = 'extras:configcontext_list'


class ConfigContextDeleteView(ObjectDeleteView):
    queryset = ConfigContext.objects.all()
    default_return_url = 'extras:configcontext_list'


class ConfigContextBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'extras.delete_configcontext'
    queryset = ConfigContext.objects.all()
    table = ConfigContextTable
    default_return_url = 'extras:configcontext_list'


class ObjectConfigContextView(View):
    object_class = None
    base_template = None

    def get(self, request, pk):

        obj = get_object_or_404(self.object_class, pk=pk)
        source_contexts = ConfigContext.objects.get_for_object(obj)
        model_name = self.object_class._meta.model_name

        # Determine user's preferred output format
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            request.user.config.set('extras.configcontext.format', format, commit=True)
        else:
            format = request.user.config.get('extras.configcontext.format', 'json')

        return render(request, 'extras/object_configcontext.html', {
            model_name: obj,
            'obj': obj,
            'rendered_context': obj.get_config_context(),
            'source_contexts': source_contexts,
            'format': format,
            'base_template': self.base_template,
            'active_tab': 'config-context',
        })


#
# Change logging
#

class ObjectChangeListView(ObjectListView):
    queryset = ObjectChange.objects.prefetch_related('user', 'changed_object_type')
    filterset = filters.ObjectChangeFilterSet
    filterset_form = forms.ObjectChangeFilterForm
    table = ObjectChangeTable
    template_name = 'extras/objectchange_list.html'
    action_buttons = ('export',)


class ObjectChangeView(PermissionRequiredMixin, View):
    permission_required = 'extras.view_objectchange'

    def get(self, request, pk):

        objectchange = get_object_or_404(ObjectChange, pk=pk)

        related_changes = ObjectChange.objects.filter(request_id=objectchange.request_id).exclude(pk=objectchange.pk)
        related_changes_table = ObjectChangeTable(
            data=related_changes[:50],
            orderable=False
        )

        objectchanges = ObjectChange.objects.filter(
            changed_object_type=objectchange.changed_object_type,
            changed_object_id=objectchange.changed_object_id,
        )

        next_change = objectchanges.filter(time__gt=objectchange.time).order_by('time').first()
        prev_change = objectchanges.filter(time__lt=objectchange.time).order_by('-time').first()

        if prev_change:
            diff_added = shallow_compare_dict(
                prev_change.object_data,
                objectchange.object_data,
                exclude=['last_updated'],
            )
            diff_removed = {x: prev_change.object_data.get(x) for x in diff_added}
        else:
            # No previous change; this is the initial change that added the object
            diff_added = diff_removed = objectchange.object_data

        return render(request, 'extras/objectchange.html', {
            'objectchange': objectchange,
            'diff_added': diff_added,
            'diff_removed': diff_removed,
            'next_change': next_change,
            'prev_change': prev_change,
            'related_changes_table': related_changes_table,
            'related_changes_count': related_changes.count()
        })


class ObjectChangeLogView(View):
    """
    Present a history of changes made to a particular object.
    """

    def get(self, request, model, **kwargs):

        # Get object my model and kwargs (e.g. slug='foo')
        obj = get_object_or_404(model, **kwargs)

        # Gather all changes for this object (and its related objects)
        content_type = ContentType.objects.get_for_model(model)
        objectchanges = ObjectChange.objects.prefetch_related(
            'user', 'changed_object_type'
        ).filter(
            Q(changed_object_type=content_type, changed_object_id=obj.pk) |
            Q(related_object_type=content_type, related_object_id=obj.pk)
        )
        objectchanges_table = ObjectChangeTable(
            data=objectchanges,
            orderable=False
        )

        # Apply the request context
        paginate = {
            'paginator_class': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(objectchanges_table)

        # Check whether a header template exists for this model
        base_template = '{}/{}.html'.format(model._meta.app_label, model._meta.model_name)
        try:
            template.loader.get_template(base_template)
            object_var = model._meta.model_name
        except template.TemplateDoesNotExist:
            base_template = 'base.html'
            object_var = 'obj'

        return render(request, 'extras/object_changelog.html', {
            object_var: obj,
            'table': objectchanges_table,
            'base_template': base_template,
            'active_tab': 'changelog',
        })


#
# Image attachments
#

class ImageAttachmentEditView(ObjectEditView):
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


class ImageAttachmentDeleteView(ObjectDeleteView):
    queryset = ImageAttachment.objects.all()

    def get_return_url(self, request, imageattachment):
        return imageattachment.parent.get_absolute_url()


#
# Reports
#

class ReportListView(PermissionRequiredMixin, View):
    """
    Retrieve all of the available reports from disk and the recorded ReportResult (if any) for each.
    """
    permission_required = 'extras.view_reportresult'

    def get(self, request):

        reports = get_reports()
        results = {r.report: r for r in ReportResult.objects.all()}

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


class ReportView(PermissionRequiredMixin, View):
    """
    Display a single Report and its associated ReportResult (if any).
    """
    permission_required = 'extras.view_reportresult'

    def get(self, request, name):

        # Retrieve the Report by "<module>.<report>"
        module_name, report_name = name.split('.')
        report = get_report(module_name, report_name)
        if report is None:
            raise Http404

        # Attach the ReportResult (if any)
        report.result = ReportResult.objects.filter(report=report.full_name).first()

        return render(request, 'extras/report.html', {
            'report': report,
            'run_form': ConfirmationForm(),
        })


class ReportRunView(PermissionRequiredMixin, View):
    """
    Run a Report and record a new ReportResult.
    """
    permission_required = 'extras.add_reportresult'

    def post(self, request, name):

        # Retrieve the Report by "<module>.<report>"
        module_name, report_name = name.split('.')
        report = get_report(module_name, report_name)
        if report is None:
            raise Http404

        form = ConfirmationForm(request.POST)
        if form.is_valid():

            # Run the Report. A new ReportResult is created.
            report.run()
            result = 'failed' if report.failed else 'passed'
            msg = "Ran report {} ({})".format(report.full_name, result)
            messages.success(request, mark_safe(msg))

        return redirect('extras:report', name=report.full_name)


#
# Scripts
#

class ScriptListView(PermissionRequiredMixin, View):
    permission_required = 'extras.view_script'

    def get(self, request):

        return render(request, 'extras/script_list.html', {
            'scripts': get_scripts(use_names=True),
        })


class ScriptView(PermissionRequiredMixin, View):
    permission_required = 'extras.view_script'

    def _get_script(self, module, name):
        scripts = get_scripts()
        try:
            return scripts[module][name]()
        except KeyError:
            raise Http404

    def get(self, request, module, name):

        script = self._get_script(module, name)
        form = script.as_form(initial=request.GET)

        return render(request, 'extras/script.html', {
            'module': module,
            'script': script,
            'form': form,
        })

    def post(self, request, module, name):

        # Permissions check
        if not request.user.has_perm('extras.run_script'):
            return HttpResponseForbidden()

        script = self._get_script(module, name)
        form = script.as_form(request.POST, request.FILES)
        output = None
        execution_time = None

        if form.is_valid():
            commit = form.cleaned_data.pop('_commit')
            output, execution_time = run_script(script, form.cleaned_data, request, commit)

        return render(request, 'extras/script.html', {
            'module': module,
            'script': script,
            'form': form,
            'output': output,
            'execution_time': execution_time,
        })
