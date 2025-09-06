from django.utils.translation import gettext as _

from netbox.object_actions import ObjectAction

__all__ = (
    'BulkAddComponents',
)


class BulkAddComponents(ObjectAction):
    """
    Add components to the selected virtual machines.
    """
    label = _('Add Components')
    multi = True
    permissions_required = {'change'}
    template_name = 'virtualization/buttons/bulk_add_components.html'

    @classmethod
    def get_context(cls, context, obj):
        return {
            'formaction': context.get('formaction'),
        }
