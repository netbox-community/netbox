import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class ExtrasQuery:
    config_context: ConfigContextType = strawberry_django.field()
    config_context_list: list[ConfigContextType] = strawberry_django.field()

    config_context_profile: ConfigContextProfileType = strawberry_django.field()
    config_context_profile_list: list[ConfigContextProfileType] = strawberry_django.field()

    config_template: ConfigTemplateType = strawberry_django.field()
    config_template_list: list[ConfigTemplateType] = strawberry_django.field()

    custom_field: CustomFieldType = strawberry_django.field()
    custom_field_list: list[CustomFieldType] = strawberry_django.field()

    custom_field_choice_set: CustomFieldChoiceSetType = strawberry_django.field()
    custom_field_choice_set_list: list[CustomFieldChoiceSetType] = strawberry_django.field()

    custom_link: CustomLinkType = strawberry_django.field()
    custom_link_list: list[CustomLinkType] = strawberry_django.field()

    export_template: ExportTemplateType = strawberry_django.field()
    export_template_list: list[ExportTemplateType] = strawberry_django.field()

    image_attachment: ImageAttachmentType = strawberry_django.field()
    image_attachment_list: list[ImageAttachmentType] = strawberry_django.field()

    saved_filter: SavedFilterType = strawberry_django.field()
    saved_filter_list: list[SavedFilterType] = strawberry_django.field()

    table_config: TableConfigType = strawberry_django.field()
    table_config_list: list[TableConfigType] = strawberry_django.field()

    journal_entry: JournalEntryType = strawberry_django.field()
    journal_entry_list: list[JournalEntryType] = strawberry_django.field()

    notification: NotificationType = strawberry_django.field()
    notification_list: list[NotificationType] = strawberry_django.field()

    notification_group: NotificationGroupType = strawberry_django.field()
    notification_group_list: list[NotificationGroupType] = strawberry_django.field()

    subscription: SubscriptionType = strawberry_django.field()
    subscription_list: list[SubscriptionType] = strawberry_django.field()

    tag: TagType = strawberry_django.field()
    tag_list: list[TagType] = strawberry_django.field()

    webhook: WebhookType = strawberry_django.field()
    webhook_list: list[WebhookType] = strawberry_django.field()

    event_rule: EventRuleType = strawberry_django.field()
    event_rule_list: list[EventRuleType] = strawberry_django.field()
