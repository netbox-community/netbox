import strawberry

from extras.choices import *

__all__ = (
    'CustomFieldChoiceSetBaseEnum',
    'CustomFieldFilterLogicEnum',
    'CustomFieldTypeEnum',
    'CustomFieldUIEditableEnum',
    'CustomFieldUIVisibleEnum',
    'CustomLinkButtonClassEnum',
    'EventRuleActionEnum',
    'JournalEntryKindEnum',
    'WebhookHttpMethodEnum',
)


CustomFieldChoiceSetBaseEnum = strawberry.enum(CustomFieldChoiceSetBaseChoices.as_enum())
CustomFieldFilterLogicEnum = strawberry.enum(CustomFieldFilterLogicChoices.as_enum())
CustomFieldTypeEnum = strawberry.enum(CustomFieldTypeChoices.as_enum())
CustomFieldUIEditableEnum = strawberry.enum(CustomFieldUIEditableChoices.as_enum())
CustomFieldUIVisibleEnum = strawberry.enum(CustomFieldUIVisibleChoices.as_enum())
CustomLinkButtonClassEnum = strawberry.enum(CustomLinkButtonClassChoices.as_enum())
EventRuleActionEnum = strawberry.enum(EventRuleActionChoices.as_enum())
JournalEntryKindEnum = strawberry.enum(JournalEntryKindChoices.as_enum())
WebhookHttpMethodEnum = strawberry.enum(WebhookHttpMethodChoices.as_enum())
