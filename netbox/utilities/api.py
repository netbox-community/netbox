from rest_framework.exceptions import APIException
from rest_framework.serializers import Field


WRITE_OPERATIONS = ['create', 'update', 'partial_update', 'delete']


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, please try again later."


class ChoiceFieldSerializer(Field):
    """
    Represent a ChoiceField as a list of (value, label) tuples.
    """

    def __init__(self, choices, **kwargs):
        self._choices = choices
        super(ChoiceFieldSerializer, self).__init__(**kwargs)

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        return getattr(self._choices, data)


class WritableSerializerMixin(object):
    """
    Allow for the use of an alternate, writable serializer class for write operations (e.g. POST, PUT).
    """

    def get_serializer_class(self):
        if self.action in WRITE_OPERATIONS and hasattr(self, 'write_serializer_class'):
            return self.write_serializer_class
        return self.serializer_class
