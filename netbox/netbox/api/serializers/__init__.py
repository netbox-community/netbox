from rest_framework import serializers

from .base import *
from .features import *
from .nested import *


#
# Base model serializers
#

class NetBoxModelSerializer(TaggableObjectSerializer, CustomFieldModelSerializer, ValidatedModelSerializer):
    """
    Adds support for custom fields and tags.
    """
    pass


class NestedGroupModelSerializer(NetBoxModelSerializer):
    """
    Extends PrimaryModelSerializer to include MPTT support.
    """
    _depth = serializers.IntegerField(source='level', read_only=True)


class BulkOperationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
