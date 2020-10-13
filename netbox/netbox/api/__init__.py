from rest_framework.schemas import coreapi

from .fields import ChoiceField, ContentTypeField, SerializedPKRelatedField, TimeZoneField
from .routers import OrderedDefaultRouter
from .serializers import BulkOperationSerializer, ValidatedModelSerializer, WritableNestedSerializer


__all__ = (
    'BulkOperationSerializer',
    'ChoiceField',
    'ContentTypeField',
    'OrderedDefaultRouter',
    'SerializedPKRelatedField',
    'TimeZoneField',
    'ValidatedModelSerializer',
    'WritableNestedSerializer',
)


def is_custom_action(action):
    return action not in {
        # Default actions
        'retrieve', 'list', 'create', 'update', 'partial_update', 'destroy',
        # Bulk operations
        'bulk_update', 'bulk_partial_update', 'bulk_destroy',
    }


# Monkey-patch DRF to treat bulk_destroy() as a non-custom action (see #3436)
coreapi.is_custom_action = is_custom_action
