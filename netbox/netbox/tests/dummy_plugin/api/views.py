from rest_framework.viewsets import ModelViewSet
from netbox.tests.dummy_plugin.models import DummyModel
from .serializers import DummyModelSerializer


class DummyViewSet(ModelViewSet):
    queryset = DummyModel.objects.all()
    serializer_class = DummyModelSerializer
