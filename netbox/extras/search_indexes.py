import extras.filtersets
import extras.tables
from django.db import models
from extras.models import JournalEntry
from search.models import SearchMixin
from utilities.utils import count_related


class JournalEntryIndex(SearchMixin):
    model = JournalEntry
    queryset = JournalEntry.objects.prefetch_related('assigned_object', 'created_by')
    filterset = extras.filtersets.JournalEntryFilterSet
    table = extras.tables.JournalEntryTable
    url = 'extras:journalentry_list'
    choice_header = 'Journal'


JOURNAL_SEARCH_TYPES = {
    'journalentry': JournalEntryIndex,
}
