import extras.filtersets
import extras.tables
from extras.models import JournalEntry
from netbox.search import SearchIndex, register_search


@register_search()
class JournalEntryIndex(SearchIndex):
    model = JournalEntry
    queryset = JournalEntry.objects.prefetch_related('assigned_object', 'created_by')
    filterset = extras.filtersets.JournalEntryFilterSet
    table = extras.tables.JournalEntryTable
    url = 'extras:journalentry_list'
    category = 'Journal'
