# Event Rule Actions

[Event rules](../../models/extras/eventrule.md) dispatch to an *action* when a matching event occurs, such as sending a webhook request or running a script. Plugins can register their own action types to extend the list of actions an event rule can perform, by subclassing NetBox's `EventRuleAction` class.

```python title="event_rules.py"
from django.utils.translation import gettext_lazy as _
from netbox.event_rules import EventRuleAction

from .models import Ticket

class OpenTicketAction(EventRuleAction):
    slug = 'my_plugin.open_ticket'
    label = _('Open ticket')
    description = _('Open a ticket in the external ticketing system')
    object_model = Ticket
    object_required = True

    def enqueue(self, *, event_rule, event_context, action_object, action_data):
        ...
```

To register one or more event rule actions with NetBox, define a list named `event_rule_actions` at the end of this file:

```python title="event_rules.py"
event_rule_actions = [OpenTicketAction]
```

!!! tip
    The path to the list of event rule actions can be modified by setting `event_rule_actions` in the PluginConfig instance.

A dotted namespace prefix (e.g. `my_plugin.open_ticket`) is strongly recommended for `slug` to avoid collisions with other plugins or with action types added to NetBox core in the future.

`slug` must be lowercase, start with a letter, and contain only letters, digits, underscores, and dot-separated segments -- **hyphens and leading underscores are not allowed**, even though they're common in plugin/package names. `register_event_rule_action()` raises `ImproperlyConfigured` immediately for a slug outside this pattern, rather than allowing it to fail later during GraphQL schema assembly.

## Target Objects

If an action operates against a specific object (e.g. a webhook targets a `Webhook` instance, and a script targets a `Script` instance), set `object_model` to the relevant model class. NetBox uses this to render the object-selection field on the event rule form and to validate the selected object's type. `object_required` defaults to `False` (matching `object_model`'s default of `None`); set it to `True` alongside `object_model` if the target object must always be selected. Override `get_object_queryset()` to customize which objects are eligible for selection (e.g. to filter or further restrict the queryset).

## Bulk Import

To support resolving a target object from a CSV value during bulk import of event rules, override `resolve_import_object()`. Raise `django.core.exceptions.ObjectDoesNotExist` (or a subclass) if the supplied value doesn't resolve to an object. If this method is not overridden, event rules using this action type cannot be targeted at an object via bulk import.

## Unregistered Actions

An event rule's `action_type` is stored as a plain string, and is not validated against the set of currently-registered actions at the database level. This means an event rule can reference an action type provided by a plugin that is later uninstalled or disabled, without the row being deleted or corrupted. While its action type is unavailable:

* The event rule is skipped during event processing (it does not raise an error, and does not prevent other event rules from being processed).
* It is displayed with an "unavailable" indicator in the UI. `action_is_available` is exposed as a read-only field via the REST API, and as a filter (`?action_is_available=false`), so affected event rules can be found in bulk.
* It cannot be saved via the UI or REST API -- even to edit an unrelated field -- until its `action_type` is changed to a currently-registered value.

Reinstalling the plugin (and thereby re-registering the action type) automatically restores the event rule to working order, with no need to re-save it.

::: netbox.event_rules.EventRuleAction
