from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import actions, panels

__all__ = (
    'CustomFieldsPanel',
    'ImageAttachmentsPanel',
    'TagsPanel',
)


class CustomFieldsPanel(panels.ObjectPanel):
    """
    Render a panel showing the value of all custom fields defined on the object.
    """
    template_name = 'ui/panels/custom_fields.html'
    title = _('Custom Fields')

    def get_context(self, context):
        obj = context['object']
        return {
            **super().get_context(context),
            'custom_fields': obj.get_custom_fields_by_group(),
        }

    def render(self, context):
        ctx = self.get_context(context)
        # Hide the panel if no custom fields exist
        if not ctx['custom_fields']:
            return ''
        return render_to_string(self.template_name, self.get_context(context))


class ImageAttachmentsPanel(panels.ObjectsTablePanel):
    """
    Render a table listing all images attached to the object.
    """
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


class TagsPanel(panels.ObjectPanel):
    """
    Render a panel showing the tags assigned to the object.
    """
    template_name = 'ui/panels/tags.html'
    title = _('Tags')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'object': context['object'],
        }
