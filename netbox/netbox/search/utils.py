from netbox.registry import registry
from utilities.utils import content_type_identifier

__all__ = (
    'get_indexer',
)


def get_indexer(content_type):
    """
    Return the registered search indexer for the given ContentType.
    """
    ct_identifier = content_type_identifier(content_type)
    return registry['search'].get(ct_identifier)
