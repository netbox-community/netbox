from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.safestring import mark_safe
from django.views.generic import View
from taggit.models import Tag

from utilities.forms import ConfirmationForm
from utilities.views import BulkDeleteView, ObjectDeleteView, ObjectEditView, ObjectListView
from .forms import ImageAttachmentForm, TagForm
from .models import ImageAttachment, ReportResult, UserAction
from .reports import get_report, get_reports
from .tables import TagTable


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
            UserAction.objects.log_create(request.user, report.result, msg)

        return redirect('extras:report', name=report.full_name)
