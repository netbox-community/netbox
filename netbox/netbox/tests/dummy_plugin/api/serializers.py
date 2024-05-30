from rest_framework.serializers import ModelSerializer
from netbox.tests.dummy_plugin.models import DummyModel


class DummyModelSerializer(ModelSerializer):

    class Meta:
        model = DummyModel
        fields = ('id', 'name', 'number')
