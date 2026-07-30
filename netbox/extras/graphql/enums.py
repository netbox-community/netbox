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
# Built from the live event_rule_actions registry (netbox.event_rules), not EventRuleActionChoices
# -- action_type is plugin-extensible, so its true set of valid values isn't known until all apps'
# (including plugins') AppConfig.ready() have run. This module is only imported once, during
# GraphQL schema assembly, which happens after that point, so this reflects core + every
# currently-installed plugin's actions -- but, like any Strawberry enum, is fixed for the life of
# the process: a plugin installed without a restart, or an action registered only within a test,
# will not appear here. See EventRuleFilter.action_type in filters.py, which uses a plain string
# lookup instead of this enum for exactly that reason.
EventRuleActionEnum = strawberry.enum(enum.Enum('EventRuleActionEnum', {
    enum_key(choice.value): choice.value for choice in get_event_rule_action_choices()
}))
JournalEntryKindEnum = strawberry.enum(JournalEntryKindChoices.as_enum(prefix='kind'))
WebhookHttpMethodEnum = strawberry.enum(WebhookHttpMethodChoices.as_enum())
