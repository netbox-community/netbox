from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class ExtrasQueryV1:
    config_context: ConfigContextTypeV1 = strawberry_django.field()
    config_context_list: List[ConfigContextTypeV1] = strawberry_django.field()

    config_context_profile: ConfigContextProfileTypeV1 = strawberry_django.field()
    config_context_profile_list: List[ConfigContextProfileTypeV1] = strawberry_django.field()

    config_template: ConfigTemplateTypeV1 = strawberry_django.field()
    config_template_list: List[ConfigTemplateTypeV1] = strawberry_django.field()

    custom_field: CustomFieldTypeV1 = strawberry_django.field()
    custom_field_list: List[CustomFieldTypeV1] = strawberry_django.field()

    custom_field_choice_set: CustomFieldChoiceSetTypeV1 = strawberry_django.field()
    custom_field_choice_set_list: List[CustomFieldChoiceSetTypeV1] = strawberry_django.field()

    custom_link: CustomLinkTypeV1 = strawberry_django.field()
    custom_link_list: List[CustomLinkTypeV1] = strawberry_django.field()

    export_template: ExportTemplateTypeV1 = strawberry_django.field()
    export_template_list: List[ExportTemplateTypeV1] = strawberry_django.field()

    image_attachment: ImageAttachmentTypeV1 = strawberry_django.field()
    image_attachment_list: List[ImageAttachmentTypeV1] = strawberry_django.field()

    saved_filter: SavedFilterTypeV1 = strawberry_django.field()
    saved_filter_list: List[SavedFilterTypeV1] = strawberry_django.field()

    table_config: TableConfigTypeV1 = strawberry_django.field()
    table_config_list: List[TableConfigTypeV1] = strawberry_django.field()

    journal_entry: JournalEntryTypeV1 = strawberry_django.field()
    journal_entry_list: List[JournalEntryTypeV1] = strawberry_django.field()

    notification: NotificationTypeV1 = strawberry_django.field()
    notification_list: List[NotificationTypeV1] = strawberry_django.field()

    notification_group: NotificationGroupTypeV1 = strawberry_django.field()
    notification_group_list: List[NotificationGroupTypeV1] = strawberry_django.field()

    subscription: SubscriptionTypeV1 = strawberry_django.field()
    subscription_list: List[SubscriptionTypeV1] = strawberry_django.field()

    tag: TagTypeV1 = strawberry_django.field()
    tag_list: List[TagTypeV1] = strawberry_django.field()

    webhook: WebhookTypeV1 = strawberry_django.field()
    webhook_list: List[WebhookTypeV1] = strawberry_django.field()

    event_rule: EventRuleTypeV1 = strawberry_django.field()
    event_rule_list: List[EventRuleTypeV1] = strawberry_django.field()
