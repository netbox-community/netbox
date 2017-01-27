from rest_framework.exceptions import APIException
from rest_framework.serializers import ModelSerializer


WRITE_OPERATIONS = ['create', 'update', 'partial_update', 'delete']


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, please try again later."


class WritableSerializerMixin(object):
    """
    Returns a flat Serializer from the given model suitable for write operations (POST, PUT, PATCH). This is necessary
    to allow write operations on objects which utilize nested serializers.
    """

    def get_serializer_class(self):

        class WritableSerializer(ModelSerializer):

            class Meta:
                model = self.get_queryset().model
                fields = '__all__'

        if self.action in WRITE_OPERATIONS:
            return WritableSerializer

        return self.serializer_class
