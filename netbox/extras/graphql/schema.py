from typing import List
import strawberry
import strawberry_django

from extras import models
from .types import *


@strawberry.type
class ExtrasQuery:
    @strawberry.field
    def config_context(self, id: int) -> ConfigContextType:
        return models.ConfigContext.objects.get(id=id)
    config_context_list: List[ConfigContextType] = strawberry_django.field()

    @strawberry.field
    def config_template(self, id: int) -> ConfigTemplateType:
        return models.ConfigTemplate.objects.get(id=id)
    config_template_list: List[ConfigTemplateType] = strawberry_django.field()

    @strawberry.field
    def custom_field(self, id: int) -> CustomFieldType:
        return models.CustomField.objects.get(id=id)
    custom_field_list: List[CustomFieldType] = strawberry_django.field()

    @strawberry.field
    def custom_field_choice_set(self, id: int) -> CustomFieldChoiceSetType:
        return models.CustomFieldChoiceSet.objects.get(id=id)
    custom_field_choice_set_list: List[CustomFieldChoiceSetType] = strawberry_django.field()

    @strawberry.field
    def custom_link(self, id: int) -> CustomLinkType:
        return models.CustomLink.objects.get(id=id)
    custom_link_list: List[CustomLinkType] = strawberry_django.field()

    @strawberry.field
    def export_template(self, id: int) -> ExportTemplateType:
        return models.ExportTemplate.objects.get(id=id)
    export_template_list: List[ExportTemplateType] = strawberry_django.field()

    @strawberry.field
    def image_attachment(self, id: int) -> ImageAttachmentType:
        return models.ImageAttachment.objects.get(id=id)
    image_attachment_list: List[ImageAttachmentType] = strawberry_django.field()

    @strawberry.field
    def saved_filter(self, id: int) -> SavedFilterType:
        return models.SavedFilter.objects.get(id=id)
    saved_filter_list: List[SavedFilterType] = strawberry_django.field()

    @strawberry.field
    def journal_entry(self, id: int) -> JournalEntryType:
        return models.JournalEntry.objects.get(id=id)
    journal_entry_list: List[JournalEntryType] = strawberry_django.field()

    @strawberry.field
    def tag(self, id: int) -> TagType:
        return models.Tag.objects.get(id=id)
    tag_list: List[TagType] = strawberry_django.field()

    @strawberry.field
    def webhook(self, id: int) -> WebhookType:
        return models.Webhook.objects.get(id=id)
    webhook_list: List[WebhookType] = strawberry_django.field()

    @strawberry.field
    def event_rule(self, id: int) -> EventRuleType:
        return models.EventRule.objects.get(id=id)
    event_rule_list: List[EventRuleType] = strawberry_django.field()
