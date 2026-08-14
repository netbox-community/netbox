# Event Rule Actions

!!! info "This feature was introduced in NetBox v4.7."

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

`slug` must begin with a lowercase letter, and may contain only letters, digits, underscores, and dot-separated segments thereafter. **Hyphens are not allowed**, even though they're common in plugin/package names -- use an underscore instead, e.g. `my_plugin.open_ticket` as in the example above. `register_event_rule_action()` raises `ImproperlyConfigured` immediately for a slug outside this pattern, rather than allowing it to fail later during GraphQL schema assembly.

`slug`/`label` are only required at registration time, not at class definition, so an intermediate base class shared by several concrete actions may leave them unset.

!!! warning "Actions must be stateless"
    Registration instantiates the class once, and that single instance serves every event rule, request, and background worker thread for the lifetime of the process. Do not stash per-event data on `self` in `enqueue()` or `validate()` -- concurrent dispatches would race over it. Everything an action needs is passed in as an argument.

## Target Objects

If an action operates against a specific object (e.g. a webhook targets a `Webhook` instance, and a script targets a `Script` instance), set `object_model` to the relevant model class. NetBox uses this to render the object-selection field on the event rule form and to validate the selected object's type. `object_required` defaults to `False` (matching `object_model`'s default of `None`); set it to `True` alongside `object_model` if the target object must always be selected. (Setting `object_required` *without* an `object_model` raises `ImproperlyConfigured` at registration, as it could never be satisfied.) Override `get_object_queryset()` to customize which objects are eligible for selection (e.g. to filter or further restrict the queryset).

The object-selection field is labeled with `object_model`'s verbose name; set `object_label` to override it.

If an action leaves `object_model` as `None`, event rules using it must not specify a target object: supplying one is rejected as a validation error rather than being silently stored.

## Bulk Import

To support resolving a target object from a CSV value during bulk import of event rules, override `resolve_import_object()`. Raise `django.core.exceptions.ObjectDoesNotExist` (or a subclass) if the supplied value doesn't resolve to an object. If this method is not overridden, event rules using this action type cannot be targeted at an object via bulk import.

## Unregistered Actions

An event rule's `action_type` is stored as a plain string, and is not validated against the set of currently-registered actions at the database level. This means an event rule can reference an action type provided by a plugin that is later uninstalled or disabled, without the row being deleted or corrupted. While its action type is unavailable:

* The event rule is skipped during event processing (it does not raise an error, and does not prevent other event rules from being processed).
* It is displayed with an "unavailable" indicator in the UI. `action_is_available` is exposed as a read-only field via the REST API, and as a filter (`?action_is_available=false`), so affected event rules can be found in bulk.
* It cannot be saved via the UI or REST API -- even to edit an unrelated field -- until its `action_type` is changed to a currently-registered value.

Reinstalling the plugin (and thereby re-registering the action type) automatically restores the event rule to working order, with no need to re-save it.

::: netbox.event_rules.EventRuleAction
