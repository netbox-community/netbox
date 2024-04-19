from netbox.search import SearchIndex, register_search
from . import models


@register_search
class CustomFieldIndex(SearchIndex):
    model = models.CustomField
    fields = (
        ('name', 100),
        ('label', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('description',)


@register_search
class JournalEntryIndex(SearchIndex):
    model = models.JournalEntry
    fields = (
        ('comments', 5000),
    )
    category = 'Journal'
    display_attrs = ('kind', 'created_by')


@register_search
class WebhookEntryIndex(SearchIndex):
    model = models.Webhook
    fields = (
        ('name', 100),
        ('description', 500),
    )
    display_attrs = ('description',)
