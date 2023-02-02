from core import filtersets, models
from netbox.graphql.types import BaseObjectType, NetBoxObjectType

__all__ = (
    'DataFileType',
    'DataSourceType',
)


class DataFileType(BaseObjectType):
    class Meta:
        model = models.DataFile
        exclude = ('data',)
        filterset_class = filtersets.DataFileFilterSet


class DataSourceType(NetBoxObjectType):
    class Meta:
        model = models.DataSource
        fields = '__all__'
        filterset_class = filtersets.DataSourceFilterSet
