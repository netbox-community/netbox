from __future__ import unicode_literals
from collections import OrderedDict

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import View

from . import reports
from utilities.views import ObjectDeleteView, ObjectEditView
from .forms import ImageAttachmentForm
from .models import ImageAttachment, ReportResult
from .reports import get_reports


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

        foo = []
        for module, report_list in reports:
            module_reports = []
            for report in report_list:
                module_reports.append({
                    'name': report.name,
                    'description': report.description,
                    'results': results.get(report.full_name, None)
                })
            foo.append((module, module_reports))

        return render(request, 'extras/report_list.html', {
            'reports': foo,
        })
