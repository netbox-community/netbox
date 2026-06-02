# Object Types

An object type identifies a NetBox model by its app label and model name (e.g. `dcim.device`). Object types are used wherever NetBox needs to refer to a model dynamically — most commonly in [custom fields](../extras/customfield.md), [object permissions](../users/objectpermission.md), [export templates](../extras/exporttemplate.md), [event rules](../extras/eventrule.md), and generic relations such as the assignment of an [IP address](../ipam/ipaddress.md) to either a device or VM interface.

Object types extend Django's stock `ContentType` model with two additional attributes that NetBox uses to reason about model capabilities: `public` (whether the model is intended for direct reference) and `features` (the set of NetBox model features the model supports, such as change logging or custom fields).

!!! note "For plugin authors"
    NetBox code should generally use `ObjectType.objects.get_for_model()` rather than Django's `ContentType.objects.get_for_model()`, so that the resulting object exposes NetBox's `public` and `features` attributes. The two managers are otherwise interchangeable.

## Fields

### App Label

The Django application label to which the model belongs (e.g. `dcim`, `ipam`, or a plugin's app label).

### Model

The lowercase model name (e.g. `device`, `prefix`).

### Public

Indicates whether the model is part of NetBox's public data model. Public models are those intended to be referenced from other objects (e.g. via custom fields or generic relations). Internal models — those backing implementation details — are non-public and are excluded from interfaces that expose model selection to end users.

### Features

The list of NetBox model features the underlying model supports (for example: `change_logging`, `custom_fields`, `tags`, `webhooks`). This list is consulted when filtering object types for a particular feature, e.g. when populating the model selector for an event rule.
