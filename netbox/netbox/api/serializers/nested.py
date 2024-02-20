from django.core.exceptions import FieldError, MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from extras.models import Tag
from utilities.utils import dict_to_filter_params
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

        if data is None:
            return None

        # Dictionary of related object attributes
        if isinstance(data, dict):
            params = dict_to_filter_params(data)
            queryset = self.Meta.model.objects
            try:
                return queryset.get(**params)
            except ObjectDoesNotExist:
                raise ValidationError(
                    _("Related object not found using the provided attributes: {params}").format(params=params))
            except MultipleObjectsReturned:
                raise ValidationError(
                    _("Multiple objects match the provided attributes: {params}").format(params=params)
                )
            except FieldError as e:
                raise ValidationError(e)

        # Integer PK of related object
        try:
            # Cast as integer in case a PK was mistakenly sent as a string
            pk = int(data)
        except (TypeError, ValueError):
            raise ValidationError(
                _(
                    "Related objects must be referenced by numeric ID or by dictionary of attributes. Received an "
                    "unrecognized value: {value}"
                ).format(value=data)
            )

        # Look up object by PK
        try:
            return self.Meta.model.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise ValidationError(_("Related object not found using the provided numeric ID: {id}").format(id=pk))


# Declared here for use by PrimaryModelSerializer, but should be imported from extras.api.nested_serializers
class NestedTagSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:tag-detail')

    class Meta:
        model = Tag
        fields = ['id', 'url', 'display', 'name', 'slug', 'color']
