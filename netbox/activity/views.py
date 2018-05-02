from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.safestring import mark_safe
from django.shortcuts import reverse

from dcim.models import Device
from utilities.forms import ConfirmationForm
from utilities.views import ObjectDeleteView, ObjectEditView
from . import models
from .models import LogItem
from . import forms


def display_activity(request, pk):

    device = get_object_or_404(Device, pk=pk)
    logItems = device.logs.all()
    return render(request, 'activity/displayActivity.html', {
        'device': device,
        'logItems': logItems,
    })

class DeleteComment(PermissionRequiredMixin, ObjectDeleteView):

    permission_required = 'activity.delete_logitem'
    model = LogItem
    template_name = 'activity/deleteComment.html'

    def get_return_url(self, request, obj):
        return reverse('activity:display', kwargs={'pk': obj.for_device.pk})

class AddComment(PermissionRequiredMixin, ObjectEditView):

    permission_required = 'activity.add_logitem'
    model = LogItem
    model_form = forms.CommentForm
    template_name = 'activity/addComment.html'

    def get_return_url(self, request, obj):
        return reverse('activity:display', kwargs={'pk': obj.for_device.pk})

    def get(self, request, *args, **kwargs):

        obj = self.get_object(kwargs)
        obj = self.alter_obj(obj, request, args, kwargs)
        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}
        form = self.model_form(instance=obj, initial=initial_data)

        # Prefilled fields for comments
        created_by = request.user
        for_device = request.build_absolute_uri().replace('http://', '').replace('https://', '').split('/')[2].split('/')[0]

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': self.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
            'created_by': created_by,
            'for_device': for_device,
        })
