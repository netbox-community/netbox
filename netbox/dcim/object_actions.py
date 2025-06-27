from django.utils.translation import gettext as _

from netbox.object_actions import ObjectAction

__all__ = (
    'BulkDisconnect',
)


class BulkDisconnect(ObjectAction):
    """
    Disconnect each of a set of objects to which a cable is connected.
    """
    name = 'bulk_disconnect'
    label = _('Disconnect Selected')
    bulk = True
    permissions_required = {'change'}
    template_name = 'buttons/bulk_disconnect.html'
