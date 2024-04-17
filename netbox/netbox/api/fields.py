from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from netaddr import IPNetwork
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField, RelatedField

__all__ = (
    'ChoiceField',
    'ContentTypeField',
    'IPNetworkSerializer',
    'SerializedPKRelatedField',
)


class ChoiceField(serializers.Field):
    """
    Represent a ChoiceField as {'value': <DB value>, 'label': <string>}. Accepts a single value on write.

    :param choices: An iterable of choices in the form (value, key).
    :param allow_blank: Allow blank values in addition to the listed choices.
    """
    def __init__(self, choices, allow_blank=False, **kwargs):
        self.choiceset = choices
        self.allow_blank = allow_blank
        self._choices = dict()

        # Unpack grouped choices
        for k, v in choices:
            if type(v) in [list, tuple]:
                for k2, v2 in v:
                    self._choices[k2] = v2
            else:
                self._choices[k] = v

        super().__init__(**kwargs)

    def validate_empty_values(self, data):
        # Convert null to an empty string unless allow_null == True
        if data is None:
            if self.allow_null:
                return True, None
            else:
                data = ''
        return super().validate_empty_values(data)

    def to_representation(self, obj):
        if obj != '':
            # Use an empty string in place of the choice label if it cannot be resolved (i.e. because a previously
            # configured choice has been removed from FIELD_CHOICES).
            return {
                'value': obj,
                'label': self._choices.get(obj, ''),
            }

    def to_internal_value(self, data):
        if data == '':
            if self.allow_blank:
                return data
            raise ValidationError(_("This field may not be blank."))

        # Provide an explicit error message if the request is trying to write a dict or list
        if isinstance(data, (dict, list)):
            raise ValidationError(_('Value must be passed directly (e.g. "foo": 123); do not use a dictionary or list.'))

        # Check for string representations of boolean/integer values
        if hasattr(data, 'lower'):
            if data.lower() == 'true':
                data = True
            elif data.lower() == 'false':
                data = False
            else:
                try:
                    data = int(data)
                except ValueError:
                    pass

        try:
            if data in self._choices:
                return data
        except TypeError:  # Input is an unhashable type
            pass

        raise ValidationError(_("{value} is not a valid choice.").format(value=data))

    @property
    def choices(self):
        return self._choices


@extend_schema_field(OpenApiTypes.STR)
class ContentTypeField(RelatedField):
    """
    Represent a ContentType as '<app_label>.<model>'
    """
    default_error_messages = {
        "does_not_exist": _("Invalid content type: {content_type}"),
        "invalid": _("Invalid value. Specify a content type as '<app_label>.<model_name>'."),
    }

    def to_internal_value(self, data):
        try:
            app_label, model = data.split('.')
            return self.queryset.get(app_label=app_label, model=model)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', content_type=data)
        except (AttributeError, TypeError, ValueError):
            self.fail('invalid')

    def to_representation(self, obj):
        return f"{obj.app_label}.{obj.model}"


class IPNetworkSerializer(serializers.Serializer):
    """
    Representation of an IP network value (e.g. 192.0.2.0/24).
    """
    def to_representation(self, instance):
        return str(instance)

    def to_internal_value(self, value):
        return IPNetwork(value)


class SerializedPKRelatedField(PrimaryKeyRelatedField):
    """
    Extends PrimaryKeyRelatedField to return a serialized object on read. This is useful for representing related
    objects in a ManyToManyField while still allowing a set of primary keys to be written.
    """
    def __init__(self, serializer, **kwargs):
        self.serializer = serializer
        self.pk_field = kwargs.pop('pk_field', None)
        super().__init__(**kwargs)

    def to_representation(self, value):
        return self.serializer(value, context={'request': self.context['request']}).data
