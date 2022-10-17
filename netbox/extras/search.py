from netbox.search import SearchIndex, register_search
from . import filtersets, models


@register_search()
class JournalEntryIndex(SearchIndex):
    model = models.JournalEntry
    fields = (
        ('comments', 5000),
    )
    queryset = models.JournalEntry.objects.prefetch_related('assigned_object', 'created_by')
    filterset = filtersets.JournalEntryFilterSet
    category = 'Journal'
