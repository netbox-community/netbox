from netbox.search import SearchIndex, register_search

from . import models


@register_search
class ImportRecordIndex(SearchIndex):
    model = models.ImportRecord
    fields = (
        ('ndx_id', 100),
        ('vendor_slug', 500),
    )
    display_attrs = ('entry_type', 'source')
