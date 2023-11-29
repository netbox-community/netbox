from netbox.search import SearchIndex, register_search
from . import models


@register_search
class JournalEntryIndex(SearchIndex):
    model = models.JournalEntry
    fields = (
        ('comments', 5000),
    )
    category = 'Journal'


@register_search
class WebhookEntryIndex(SearchIndex):
    model = models.Webhook
    fields = (
        ('name', 100),
        ('description', 500),
    )
