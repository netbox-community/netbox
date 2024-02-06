import strawberry
import strawberry_django
from strawberry import auto
from core import models, filtersets
from netbox.graphql import filters


__all__ = (
    'DataFileFilter',
    'DataSourceFilter',
)


@strawberry_django.filter(models.DataFile, lookups=True)
class DataFileFilter(filtersets.DataFileFilterSet):
    id: auto


@strawberry_django.filter(models.DataSource, lookups=True)
class DataSourceFilter(filtersets.DataSourceFilterSet):
    id: auto
