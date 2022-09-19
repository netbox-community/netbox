import dcim.filtersets
import dcim.tables
from django.db import models
from extras.models import JournalEntry
from search.models import SearchMixin


class JournalEntryIndex(SearchMixin):
    def __init__(self):
        self.model = JournalEntry
        self.queryset = JournalEntry.objects.prefetch_related('assigned_object', 'created_by')
        self.filterset = extras.filtersets.JournalEntryFilterSet
        self.table = extras.tables.JournalEntryTable
        self.url = 'extras:journalentry_list'


JOURNAL_SEARCH_TYPES = {
    'journalentry': JournalEntryIndex(),
}
