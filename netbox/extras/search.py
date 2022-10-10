import extras.filtersets
import extras.tables
from extras.models import JournalEntry
from netbox.search import SearchIndex, register_search


@register_search()
class JournalEntryIndex(SearchIndex):
    model = JournalEntry
    fields = (
        ('comments', 1000),
    )
    queryset = JournalEntry.objects.prefetch_related('assigned_object', 'created_by')
    filterset = extras.filtersets.JournalEntryFilterSet
    category = 'Journal'
