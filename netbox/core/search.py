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
    display_attrs = ('type', 'status', 'description')


@register_search
class DataFileIndex(SearchIndex):
    model = models.DataFile
    fields = (
        ('path', 200),
    )
    display_attrs = ('source',)
