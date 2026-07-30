import enum

import strawberry

from extras.choices import *
from netbox.event_rules import get_event_rule_action_choices
from utilities.string import enum_key

__all__ = (
    'CustomFieldChoiceColorEnum',
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


CustomFieldChoiceColorEnum = strawberry.enum(CustomFieldChoiceColorChoices.as_enum())
CustomFieldChoiceSetBaseEnum = strawberry.enum(CustomFieldChoiceSetBaseChoices.as_enum())
CustomFieldFilterLogicEnum = strawberry.enum(CustomFieldFilterLogicChoices.as_enum(prefix='filter'))
CustomFieldTypeEnum = strawberry.enum(CustomFieldTypeChoices.as_enum(prefix='type'))
CustomFieldUIEditableEnum = strawberry.enum(CustomFieldUIEditableChoices.as_enum())
CustomFieldUIVisibleEnum = strawberry.enum(CustomFieldUIVisibleChoices.as_enum())
CustomLinkButtonClassEnum = strawberry.enum(CustomLinkButtonClassChoices.as_enum())
# Built from the live event_rule_actions registry, not EventRuleActionChoices -- action_type is
# plugin-extensible, and this module isn't imported until schema assembly, after plugins load.
# Still fixed for the process's lifetime like any Strawberry enum, so a plugin installed without a
# restart won't appear here.
EventRuleActionEnum = strawberry.enum(enum.Enum('EventRuleActionEnum', {
    enum_key(choice.value): choice.value for choice in get_event_rule_action_choices()
}))
JournalEntryKindEnum = strawberry.enum(JournalEntryKindChoices.as_enum(prefix='kind'))
WebhookHttpMethodEnum = strawberry.enum(WebhookHttpMethodChoices.as_enum())
