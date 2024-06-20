import strawberry_django

from extras import filtersets, models
from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

__all__ = (
    'ConfigContextFilter',
    'ConfigTemplateFilter',
    'CustomFieldFilter',
    'CustomFieldChoiceSetFilter',
    'CustomLinkFilter',
    'EventRuleFilter',
    'ExportTemplateFilter',
    'ImageAttachmentFilter',
    'JournalEntryFilter',
    'SavedFilterFilter',
    'TagFilter',
    'WebhookFilter',
)


@strawberry_django.filter(models.ConfigContext, lookups=True)
@autotype_decorator(filtersets.ConfigContextFilterSet)
class ConfigContextFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ConfigTemplate, lookups=True)
@autotype_decorator(filtersets.ConfigTemplateFilterSet)
class ConfigTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.CustomField, lookups=True)
@autotype_decorator(filtersets.CustomFieldFilterSet)
class CustomFieldFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.CustomFieldChoiceSet, lookups=True)
@autotype_decorator(filtersets.CustomFieldChoiceSetFilterSet)
class CustomFieldChoiceSetFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.CustomLink, lookups=True)
@autotype_decorator(filtersets.CustomLinkFilterSet)
class CustomLinkFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ExportTemplate, lookups=True)
@autotype_decorator(filtersets.ExportTemplateFilterSet)
class ExportTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ImageAttachment, lookups=True)
@autotype_decorator(filtersets.ImageAttachmentFilterSet)
class ImageAttachmentFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.JournalEntry, lookups=True)
@autotype_decorator(filtersets.JournalEntryFilterSet)
class JournalEntryFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.SavedFilter, lookups=True)
@autotype_decorator(filtersets.SavedFilterFilterSet)
class SavedFilterFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Tag, lookups=True)
@autotype_decorator(filtersets.TagFilterSet)
class TagFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Webhook, lookups=True)
@autotype_decorator(filtersets.WebhookFilterSet)
class WebhookFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.EventRule, lookups=True)
@autotype_decorator(filtersets.EventRuleFilterSet)
class EventRuleFilter(BaseFilterMixin):
    pass
