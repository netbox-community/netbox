from rest_framework.routers import APIRootView

from core import filtersets
from core.models import *
from netbox.api.viewsets import NetBoxModelViewSet
from utilities.utils import count_related
from . import serializers


class CoreRootView(APIRootView):
    """
    Core API root view
    """
    def get_view_name(self):
        return 'Core'


#
# Data sources
#

class DataSourceViewSet(NetBoxModelViewSet):
    queryset = DataSource.objects.annotate(
        file_count=count_related(DataFile, 'source')
    )
    serializer_class = serializers.DataSourceSerializer
    filterset_class = filtersets.DataSourceFilterSet


class DataFileViewSet(NetBoxModelViewSet):
    queryset = DataFile.objects.defer('data').prefetch_related('source')
    serializer_class = serializers.DataFileSerializer
    filterset_class = filtersets.DataFileFilterSet
