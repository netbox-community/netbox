from netbox.search import SearchIndex, register_search
from . import models


@register_search
class JournalEntryIndex(SearchIndex):
    model = models.JournalEntry
    fields = (
        ('comments', 5000),
    )
    category = 'Journal'
