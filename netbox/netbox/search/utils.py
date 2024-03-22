from netbox.registry import registry
from utilities.object_types import object_type_identifier

__all__ = (
    'get_indexer',
)


def get_indexer(object_type):
    """
    Return the registered search indexer for the given ContentType.
    """
    identifier = object_type_identifier(object_type)
    return registry['search'].get(identifier)
