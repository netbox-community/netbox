from typing import List

import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class ExtrasQueryOld:
    config_context: ConfigContextType = strawberry_django.field()
    config_context_list: List[ConfigContextType] = strawberry_django.field()

    config_context_profile: ConfigContextProfileType = strawberry_django.field()
    config_context_profile_list: List[ConfigContextProfileType] = strawberry_django.field()

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

    table_config: TableConfigType = strawberry_django.field()
    table_config_list: List[TableConfigType] = strawberry_django.field()

    journal_entry: JournalEntryType = strawberry_django.field()
    journal_entry_list: List[JournalEntryType] = strawberry_django.field()

    notification: NotificationType = strawberry_django.field()
    notification_list: List[NotificationType] = strawberry_django.field()

    notification_group: NotificationGroupType = strawberry_django.field()
    notification_group_list: List[NotificationGroupType] = strawberry_django.field()

    subscription: SubscriptionType = strawberry_django.field()
    subscription_list: List[SubscriptionType] = strawberry_django.field()

    tag: TagType = strawberry_django.field()
    tag_list: List[TagType] = strawberry_django.field()

    webhook: WebhookType = strawberry_django.field()
    webhook_list: List[WebhookType] = strawberry_django.field()

    event_rule: EventRuleType = strawberry_django.field()
    event_rule_list: List[EventRuleType] = strawberry_django.field()


@strawberry.type(name="Query")
class ExtrasQuery:
    config_context: ConfigContextType = strawberry_django.field()
    config_context_list: OffsetPaginated[ConfigContextType] = strawberry_django.offset_paginated()

    config_context_profile: ConfigContextProfileType = strawberry_django.field()
    config_context_profile_list: OffsetPaginated[ConfigContextProfileType] = strawberry_django.offset_paginated()

    config_template: ConfigTemplateType = strawberry_django.field()
    config_template_list: OffsetPaginated[ConfigTemplateType] = strawberry_django.offset_paginated()

    custom_field: CustomFieldType = strawberry_django.field()
    custom_field_list: OffsetPaginated[CustomFieldType] = strawberry_django.offset_paginated()

    custom_field_choice_set: CustomFieldChoiceSetType = strawberry_django.field()
    custom_field_choice_set_list: OffsetPaginated[CustomFieldChoiceSetType] = strawberry_django.offset_paginated()

    custom_link: CustomLinkType = strawberry_django.field()
    custom_link_list: OffsetPaginated[CustomLinkType] = strawberry_django.offset_paginated()

    export_template: ExportTemplateType = strawberry_django.field()
    export_template_list: OffsetPaginated[ExportTemplateType] = strawberry_django.offset_paginated()

    image_attachment: ImageAttachmentType = strawberry_django.field()
    image_attachment_list: OffsetPaginated[ImageAttachmentType] = strawberry_django.offset_paginated()

    saved_filter: SavedFilterType = strawberry_django.field()
    saved_filter_list: OffsetPaginated[SavedFilterType] = strawberry_django.offset_paginated()

    table_config: TableConfigType = strawberry_django.field()
    table_config_list: OffsetPaginated[TableConfigType] = strawberry_django.offset_paginated()

    journal_entry: JournalEntryType = strawberry_django.field()
    journal_entry_list: OffsetPaginated[JournalEntryType] = strawberry_django.offset_paginated()

    notification: NotificationType = strawberry_django.field()
    notification_list: OffsetPaginated[NotificationType] = strawberry_django.offset_paginated()

    notification_group: NotificationGroupType = strawberry_django.field()
    notification_group_list: OffsetPaginated[NotificationGroupType] = strawberry_django.offset_paginated()

    subscription: SubscriptionType = strawberry_django.field()
    subscription_list: OffsetPaginated[SubscriptionType] = strawberry_django.offset_paginated()

    tag: TagType = strawberry_django.field()
    tag_list: OffsetPaginated[TagType] = strawberry_django.offset_paginated()

    webhook: WebhookType = strawberry_django.field()
    webhook_list: OffsetPaginated[WebhookType] = strawberry_django.offset_paginated()

    event_rule: EventRuleType = strawberry_django.field()
    event_rule_list: OffsetPaginated[EventRuleType] = strawberry_django.offset_paginated()
