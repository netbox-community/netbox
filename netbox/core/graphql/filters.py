import strawberry
import strawberry_django
from core import filtersets, models

from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

__all__ = (
    'DataFileFilter',
    'DataSourceFilter',
)


@strawberry_django.filter(models.DataFile, lookups=True)
@autotype_decorator(filtersets.DataFileFilterSet)
class DataFileFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.DataSource, lookups=True)
@autotype_decorator(filtersets.DataSourceFilterSet)
class DataSourceFilter(BaseFilterMixin):
    pass
