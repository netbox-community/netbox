from django.utils.translation import gettext as _

from netbox.object_actions import ObjectAction

__all__ = (
    'BulkSync',
)


class BulkSync(ObjectAction):
    """
    Synchronize multiple objects at once.
    """
    name = 'bulk_sync'
    label = _('Sync Data')
    bulk = True
    permissions_required = {'sync'}
    template_name = 'buttons/bulk_sync.html'
