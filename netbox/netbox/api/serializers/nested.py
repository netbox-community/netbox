from rest_framework import serializers

from extras.models import Tag
from utilities.api import get_related_object_by_attrs
from .base import BaseModelSerializer

__all__ = (
    'NestedTagSerializer',
    'WritableNestedSerializer',
)


class WritableNestedSerializer(BaseModelSerializer):
    """
    Represents an object related through a ForeignKey field. On write, it accepts a primary key (PK) value or a
    dictionary of attributes which can be used to uniquely identify the related object. This class should be
    subclassed to return a full representation of the related object on read.
    """
    def to_internal_value(self, data):
        queryset = self.Meta.model.objects.all()
        return get_related_object_by_attrs(queryset, data)


# Declared here for use by PrimaryModelSerializer, but should be imported from extras.api.nested_serializers
class NestedTagSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:tag-detail')

    class Meta:
        model = Tag
        fields = ['id', 'url', 'display', 'name', 'slug', 'color']
