from extras.models import Tag

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
    @property
    def resolves_existing_object(self):
        return True


# Declared here for use by PrimaryModelSerializer
class NestedTagSerializer(WritableNestedSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug', 'color']
