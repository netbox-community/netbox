from typing import List

import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class ExtrasQuery:
    config_context: ConfigContextType = strawberry_django.field()
    config_context_list: List[ConfigContextType] = strawberry_django.field()

    config_template: ConfigTemplateType = strawberry_django.field()
    config_template_list: List[ConfigTemplateType] = strawberry_django.field()

    custom_field: CustomFieldType = strawberry_django.field()
    custom_field_list: List[CustomFieldType] = strawberry_django.field()

    custom_field_choice_set: CustomFieldChoiceSetType = strawberry_django.field()
    custom_field_choice_set_list: List[CustomFieldChoiceSetType] = strawberry_django.field()

    custom_link: CustomLinkType = strawberry_django.field()
    custom_link_list: List[CustomLinkType] = strawberry_django.field()

    export_template: ExportTemplateType = strawberry_django.field()
    export_template_list: List[ExportTemplateType] = strawberry_django.field()

    image_attachment: ImageAttachmentType = strawberry_django.field()
    image_attachment_list: List[ImageAttachmentType] = strawberry_django.field()

    saved_filter: SavedFilterType = strawberry_django.field()
    saved_filter_list: List[SavedFilterType] = strawberry_django.field()

    journal_entry: JournalEntryType = strawberry_django.field()
    journal_entry_list: List[JournalEntryType] = strawberry_django.field()

    tag: TagType = strawberry_django.field()
    tag_list: List[TagType] = strawberry_django.field()

    webhook: WebhookType = strawberry_django.field()
    webhook_list: List[WebhookType] = strawberry_django.field()

    event_rule: EventRuleType = strawberry_django.field()
    event_rule_list: List[EventRuleType] = strawberry_django.field()
