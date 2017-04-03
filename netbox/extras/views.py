from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404

from utilities.views import ObjectDeleteView, ObjectEditView
from .forms import ImageAttachmentForm
from .models import ImageAttachment


class ImageAttachmentEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'extras.change_imageattachment'
    model = ImageAttachment
    form_class = ImageAttachmentForm

    def alter_obj(self, imageattachment, request, args, kwargs):
        if not imageattachment.pk:
            # Assign the parent object based on URL kwargs
            model = kwargs.get('model')
            imageattachment.obj = get_object_or_404(model, pk=kwargs['object_id'])
        return imageattachment

    def get_return_url(self, imageattachment):
        return imageattachment.obj.get_absolute_url()


class ImageAttachmentDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_imageattachment'
    model = ImageAttachment

    def get_return_url(self, imageattachment):
        return imageattachment.obj.get_absolute_url()
