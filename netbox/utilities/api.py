from rest_framework.exceptions import APIException
from rest_framework.serializers import ModelSerializer


WRITE_OPERATIONS = ['create', 'update', 'partial_update', 'delete']


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, please try again later."


class WritableSerializerMixin(object):
    """
    Allow for the use of an alternate, writable serializer class for write operations (e.g. POST, PUT).
    """

    def get_serializer_class(self):
        if self.action in WRITE_OPERATIONS and hasattr(self, 'write_serializer_class'):
            return self.write_serializer_class
        return self.serializer_class
