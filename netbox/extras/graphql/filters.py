import strawberry
import strawberry_django
from strawberry import auto
from extras import models, filtersets

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
    'ObjectChangeFilter',
    'SavedFilterFilter',
    'TagFilter',
    'WebhookFilter',
)


@strawberry_django.filter(models.ConfigContext, lookups=True)
class ConfigContextFilter(filtersets.ConfigContextFilterSet):
    id: auto
    name: auto
    is_active: auto
    data_synced: auto


@strawberry_django.filter(models.ConfigTemplate, lookups=True)
class ConfigTemplateFilter(filtersets.ConfigTemplateFilterSet):
    id: auto
    name: auto
    description: auto
    data_synced: auto


@strawberry_django.filter(models.CustomField, lookups=True)
class CustomFieldFilter(filtersets.CustomFieldFilterSet):
    id: auto
    content_types: auto
    name: auto
    group_name: auto
    required: auto
    search_weight: auto
    filter_logic: auto
    weight: auto
    is_cloneable: auto
    description: auto


@strawberry_django.filter(models.CustomFieldChoiceSet, lookups=True)
class CustomFieldChoiceSetFilter(filtersets.CustomFieldChoiceSetFilterSet):
    id: auto
    name: auto
    description: auto
    base_choices: auto
    order_alphabetically: auto


@strawberry_django.filter(models.CustomLink, lookups=True)
class CustomLinkFilter(filtersets.CustomLinkFilterSet):
    id: auto
    content_types: auto
    name: auto
    enabled: auto
    link_text: auto
    link_url: auto
    weight: auto
    group_name: auto
    new_window: auto


@strawberry_django.filter(models.ExportTemplate, lookups=True)
class ExportTemplateFilter(filtersets.ExportTemplateFilterSet):
    id: auto
    content_types: auto
    name: auto
    description: auto
    data_synced: auto


@strawberry_django.filter(models.ImageAttachment, lookups=True)
class ImageAttachmentFilter(filtersets.ImageAttachmentFilterSet):
    id: auto
    content_type_id: auto
    object_id: auto
    name: auto


@strawberry_django.filter(models.JournalEntry, lookups=True)
class JournalEntryFilter(filtersets.JournalEntryFilterSet):
    id: auto
    assigned_object_type_id: auto
    assigned_object_id: auto
    created: auto
    kind: auto


@strawberry_django.filter(models.ObjectChange, lookups=True)
class ObjectChangeFilter(filtersets.ObjectChangeFilterSet):
    id: auto
    user: auto
    user_name: auto
    request_id: auto
    action: auto
    changed_object_type_id: auto
    changed_object_id: auto
    object_repr: auto


@strawberry_django.filter(models.SavedFilter, lookups=True)
class SavedFilterFilter(filtersets.SavedFilterFilterSet):
    id: auto
    content_types: auto
    name: auto
    slug: auto
    description: auto
    enabled: auto
    shared: auto
    weight: auto


@strawberry_django.filter(models.Tag, lookups=True)
class TagFilter(filtersets.TagFilterSet):
    id: auto
    name: auto
    slug: auto
    # color: auto
    description: auto
    object_types: auto


@strawberry_django.filter(models.Webhook, lookups=True)
class WebhookFilter(filtersets.WebhookFilterSet):
    id: auto
    name: auto
    payload_url: auto
    http_method: auto
    http_content_type: auto
    secret: auto
    ssl_verification: auto
    ca_file_path: auto


@strawberry_django.filter(models.EventRule, lookups=True)
class EventRuleFilter(filtersets.EventRuleFilterSet):
    id: auto
    name: auto
    enabled: auto
    type_create: auto
    type_update: auto
    type_delete: auto
    type_job_start: auto
    type_job_end: auto
