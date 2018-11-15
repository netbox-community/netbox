from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.views.generic import View
from django_tables2 import RequestConfig
from taggit.models import Tag, TaggedItem

from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator
from utilities.views import BulkDeleteView, BulkEditView, ObjectDeleteView, ObjectEditView, ObjectListView
from . import filters
from .forms import (
    ConfigContextForm, ConfigContextBulkEditForm, ConfigContextFilterForm, ImageAttachmentForm, ObjectChangeFilterForm,
    TagFilterForm, TagForm,
)
from .models import ConfigContext, ImageAttachment, ObjectChange, ReportResult
from .reports import get_report, get_reports
from .tables import ConfigContextTable, ObjectChangeTable, TagTable, TaggedItemTable


#
# Tags
#

class TagListView(ObjectListView):
    queryset = Tag.objects.annotate(
        items=Count('taggit_taggeditem_items')
    ).order_by(
        'name'
    )
    filter = filters.TagFilter
    filter_form = TagFilterForm
    table = TagTable
    template_name = 'extras/tag_list.html'


class TagView(View):

    def get(self, request, slug):

        tag = get_object_or_404(Tag, slug=slug)
        tagged_items = TaggedItem.objects.filter(
            tag=tag
        ).select_related(
            'content_type'
        ).prefetch_related(
            'content_object'
        )

        # Generate a table of all items tagged with this Tag
        items_table = TaggedItemTable(tagged_items)
        paginate = {
            'klass': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(items_table)

        return render(request, 'extras/tag.html', {
            'tag': tag,
            'items_count': tagged_items.count(),
            'items_table': items_table,
        })


class TagEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'taggit.change_tag'
    model = Tag
    model_form = TagForm
    default_return_url = 'extras:tag_list'


class TagDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'taggit.delete_tag'
    model = Tag
    default_return_url = 'extras:tag_list'


class TagBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'circuits.delete_circuittype'
    queryset = Tag.objects.annotate(
        items=Count('taggit_taggeditem_items')
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
    filter = filters.ConfigContextFilter
    filter_form = ConfigContextFilterForm
    table = ConfigContextTable
    template_name = 'extras/configcontext_list.html'


class ConfigContextView(View):

    def get(self, request, pk):

        configcontext = get_object_or_404(ConfigContext, pk=pk)

        return render(request, 'extras/configcontext.html', {
            'configcontext': configcontext,
        })


class ConfigContextCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'extras.add_configcontext'
    model = ConfigContext
    model_form = ConfigContextForm
    default_return_url = 'extras:configcontext_list'
    template_name = 'extras/configcontext_edit.html'


class ConfigContextEditView(ConfigContextCreateView):
    permission_required = 'extras.change_configcontext'


class ConfigContextBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'extras.change_configcontext'
    queryset = ConfigContext.objects.all()
    filter = filters.ConfigContextFilter
    table = ConfigContextTable
    form = ConfigContextBulkEditForm
    default_return_url = 'extras:configcontext_list'


class ConfigContextDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'extras.delete_configcontext'
    model = ConfigContext
    default_return_url = 'extras:configcontext_list'


class ConfigContextBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'extras.delete_cconfigcontext'
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

        return render(request, 'extras/object_configcontext.html', {
            model_name: obj,
            'obj': obj,
            'rendered_context': obj.get_config_context(),
            'source_contexts': source_contexts,
            'base_template': self.base_template,
            'active_tab': 'config-context',
        })


#
# Change logging
#

class ObjectChangeListView(ObjectListView):
    queryset = ObjectChange.objects.select_related('user', 'changed_object_type')
    filter = filters.ObjectChangeFilter
    filter_form = ObjectChangeFilterForm
    table = ObjectChangeTable
    template_name = 'extras/objectchange_list.html'


class ObjectChangeView(View):

    def get(self, request, pk):

        objectchange = get_object_or_404(ObjectChange, pk=pk)

        related_changes = ObjectChange.objects.filter(request_id=objectchange.request_id).exclude(pk=objectchange.pk)
        related_changes_table = ObjectChangeTable(
            data=related_changes[:50],
            orderable=False
        )

        return render(request, 'extras/objectchange.html', {
            'objectchange': objectchange,
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
        objectchanges = ObjectChange.objects.select_related(
            'user', 'changed_object_type'
        ).filter(
            Q(changed_object_type=content_type, changed_object_id=obj.pk) |
            Q(related_object_type=content_type, related_object_id=obj.pk)
        )
        objectchanges_table = ObjectChangeTable(
            data=objectchanges,
            orderable=False
        )

        # Check whether a header template exists for this model
        base_template = '{}/{}.html'.format(model._meta.app_label, model._meta.model_name)
        try:
            template.loader.get_template(base_template)
            object_var = model._meta.model_name
        except template.TemplateDoesNotExist:
            base_template = '_base.html'
            object_var = 'obj'

        return render(request, 'extras/object_changelog.html', {
            object_var: obj,
            'objectchanges_table': objectchanges_table,
            'base_template': base_template,
            'active_tab': 'changelog',
        })


#
# Image attachments
#

class ImageAttachmentEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'extras.change_imageattachment'
    model = ImageAttachment
    model_form = ImageAttachmentForm

    def alter_obj(self, imageattachment, request, args, kwargs):
        if not imageattachment.pk:
            # Assign the parent object based on URL kwargs
            model = kwargs.get('model')
            imageattachment.parent = get_object_or_404(model, pk=kwargs['object_id'])
        return imageattachment

    def get_return_url(self, request, imageattachment):
        return imageattachment.parent.get_absolute_url()


class ImageAttachmentDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'extras.delete_imageattachment'
    model = ImageAttachment

    def get_return_url(self, request, imageattachment):
        return imageattachment.parent.get_absolute_url()


#
# Reports
#

class ReportListView(View):
    """
    Retrieve all of the available reports from disk and the recorded ReportResult (if any) for each.
    """

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


class ReportView(View):
    """
    Display a single Report and its associated ReportResult (if any).
    """

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
