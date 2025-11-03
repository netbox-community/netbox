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

    def get_context(self, context):
        obj = context['object']
        return {
            **super().get_context(context),
            'custom_fields': obj.get_custom_fields_by_group(),
        }


class ImageAttachmentsPanel(panels.ObjectsTablePanel):
    actions = [
        actions.AddObject(
            'extras.imageattachment',
            url_params={
                'object_type': lambda ctx: ContentType.objects.get_for_model(ctx['object']).pk,
                'object_id': lambda ctx: ctx['object'].pk,
                'return_url': lambda ctx: ctx['object'].get_absolute_url(),
            },
            label=_('Attach an image'),
        ),
    ]

    def __init__(self, **kwargs):
        super().__init__('extras.imageattachment', **kwargs)


class TagsPanel(panels.Panel):
    template_name = 'ui/panels/tags.html'
    title = _('Tags')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'object': context['object'],
        }
