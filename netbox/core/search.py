from netbox.search import SearchIndex, register_search
from . import models


@register_search
class DataSourceIndex(SearchIndex):
    model = models.DataSource
    fields = (
        ('name', 100),
        ('source_url', 300),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class DataFileIndex(SearchIndex):
    model = models.DataFile
    fields = (
        ('path', 200),
    )
