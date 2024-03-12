import strawberry
import strawberry_django
from core import filtersets, models
from strawberry import auto

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
