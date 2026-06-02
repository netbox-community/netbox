from utilities.forms import BulkRenameForm

from .mixins import ChangelogMessageMixin

__all__ = (
    'NetBoxModelBulkRenameForm',
)


class NetBoxModelBulkRenameForm(ChangelogMessageMixin, BulkRenameForm):
    """
    Extends BulkRenameForm with a changelog message field for NetBox models that support change logging.
    """
    pass
