from rest_framework import serializers

from .features import ChangeLogMessageSerializer

__all__ = (
    'BulkOperationSerializer',
)


class BulkOperationSerializer(ChangeLogMessageSerializer):
    id = serializers.IntegerField()
