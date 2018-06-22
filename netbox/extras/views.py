from __future__ import unicode_literals

from django import template
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.safestring import mark_safe
from django.views.generic import View
from taggit.models import Tag

from utilities.forms import ConfirmationForm
from utilities.views import BulkDeleteView, ObjectDeleteView, ObjectEditView, ObjectListView
from . import filters
from .forms import ObjectChangeFilterForm, ImageAttachmentForm, TagForm
from .models import ImageAttachment, ObjectChange, ReportResult
from .reports import get_report, get_reports
from .tables import ObjectChangeTable, TagTable


#
# Tags
#

class TagListView(ObjectListView):
    queryset = Tag.objects.annotate(items=Count('taggit_taggeditem_items')).order_by('name')
    table = TagTable
    template_name = 'extras/tag_list.html'


class TagEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'taggit.change_tag'
    model = Tag
    model_form = TagForm

    def get_return_url(self, request, obj):
        return reverse('extras:tag', kwargs={'slug': obj.slug})


class TagDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'taggit.delete_tag'
    model = Tag
    default_return_url = 'extras:tag_list'


class TagBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'circuits.delete_circuittype'
    cls = Tag
    queryset = Tag.objects.annotate(items=Count('taggit_taggeditem_items')).order_by('name')
    table = TagTable
    default_return_url = 'extras:tag_list'


#
# Change logging
#

class ObjectChangeListView(ObjectListView):
    queryset = ObjectChange.objects.select_related('user', 'content_type')
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
