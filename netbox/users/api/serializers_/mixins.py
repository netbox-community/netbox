from rest_framework import serializers

from users.api.serializers_.owners import OwnerSerializer

__all__ = (
    'OwnerMixin',
)


class OwnerMixin(serializers.Serializer):
    """
    Adds an `owner` field for models which have a ForeignKey to users.Owner.
    """
    owner = OwnerSerializer(
        nested=True,
        required=False,
        allow_null=True,
    )
