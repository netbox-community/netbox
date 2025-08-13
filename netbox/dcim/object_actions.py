from django.utils.translation import gettext as _

from netbox.object_actions import ObjectAction

__all__ = (
    'BulkAddComponents',
    'BulkDisconnect',
)


class BulkAddComponents(ObjectAction):
    """
    Add components to the selected devices.
    """
    label = _('Add Components')
    multi = True
    permissions_required = {'change'}
    template_name = 'dcim/buttons/bulk_add_components.html'

    @classmethod
    def get_context(cls, context, obj):
        return {
            'formaction': context.get('formaction'),
        }


class BulkDisconnect(ObjectAction):
    """
    Disconnect each of a set of objects to which a cable is connected.
    """
    name = 'bulk_disconnect'
    label = _('Disconnect Selected')
    multi = True
    permissions_required = {'change'}
    template_name = 'dcim/buttons/bulk_disconnect.html'
