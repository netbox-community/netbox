from __future__ import unicode_literals

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from utilities.views import ObjectDeleteView, ObjectEditView
from .forms import ImageAttachmentForm
from .models import ImageAttachment, ReportResult
from .reports import get_report, get_reports


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
        })
