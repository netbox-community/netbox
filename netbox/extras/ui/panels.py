from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from netbox.ui import actions, panels

__all__ = (
    'CustomFieldsPanel',
    'ImageAttachmentsPanel',
    'TagsPanel',
)


class CustomFieldsPanel(panels.Panel):
    template_name = 'ui/panels/custom_fields.html'
    title = _('Custom Fields')

    def get_context(self, obj):
        return {
            'custom_fields': obj.get_custom_fields_by_group(),
        }


class ImageAttachmentsPanel(panels.ObjectsTablePanel):
    actions = [
        actions.AddObject(
            'extras.imageattachment',
            url_params={
                'object_type': lambda obj: ContentType.objects.get_for_model(obj).pk,
                'object_id': lambda obj: obj.pk,
                'return_url': lambda obj: obj.get_absolute_url(),
            },
            label=_('Attach an image'),
        ),
    ]

    def __init__(self, **kwargs):
        super().__init__('extras.imageattachment', **kwargs)


class TagsPanel(panels.Panel):
    template_name = 'ui/panels/tags.html'
    title = _('Tags')
