# Module Types

A module type represents a specific make and model of hardware component which is installable within a device's [module bay](./modulebay.md) and has its own child components. For example, consider a chassis-based switch or router with a number of field-replaceable line cards. Each line card has its own model number and includes a certain set of components such as interfaces. Each module type may have a manufacturer, model number, and part number assigned to it.

Similar to [device types](./devicetype.md), each module type can have any of the following component templates associated with it:

* Interfaces
* Console ports
* Console server ports
* Power ports
* Power Outlets
* Front pass-through ports
* Rear pass-through ports

Note that device bays and module bays may _not_ be added to modules.

## Automatic Component Renaming

When adding component templates to a module type, placeholders can be used to dynamically incorporate the module bay's `position` field into component names. Two placeholders are available:

### `{module}` Placeholder

The `{module}` placeholder references the position of the parent module bay:

* **Single use**: Expands to the immediate parent's position only
* **Multiple uses**: Each `{module}` token is replaced level-by-level (the number of tokens must match the nesting depth)

For example, a module type with interface templates named `Gi{module}/0/[1-48]`, when installed in a module bay with position "3", will create interfaces named `Gi3/0/[1-48]`.

### `{module_path}` Placeholder

The `{module_path}` placeholder expands to the full path from the root device to the current module, with positions joined by `/`. This is useful for modules that can be installed at any nesting depth without modification.

For example, consider an SFP module type with an interface template named `eth{module_path}`:

* Installed directly in slot 2: creates interface `eth2`
* Installed in slot 1's nested bay 1: creates interface `eth1/1`
* Installed in slot 1's nested bay 2's sub-bay 3: creates interface `eth1/2/3`

!!! note
    `{module_path}` can only be used once per template attribute, and cannot be mixed with `{module}` in the same attribute.

### Position Field Resolution

The `{module}` placeholder can also be used in the `position` field of [module bay templates](./modulebaytemplate.md) defined on a module type. This allows nested module bays to build hierarchical position values. For example, a module bay template with `position="{module}/1"`, when its parent module is installed in a bay with position "2", will have its position resolved to "2/1".

Automatic renaming is supported for all modular component types (those listed above).

## Fields

### Manufacturer

The [manufacturer](./manufacturer.md) which produces this type of module.

### Model

The model number assigned to this module type by its manufacturer. Must be unique to the manufacturer.

### Part Number

An alternative part number to uniquely identify the module type.

### Weight

The numeric weight of the module, including a unit designation (e.g. 3 kilograms or 1 pound).

### Airflow

The direction in which air circulates through the device chassis for cooling.

### Profile

The assigned [profile](./moduletypeprofile.md) for the type of module. Profiles can be used to classify module types by function (e.g. power supply, hard disk, etc.), and they support the addition of user-configurable attributes on module types. The assignment of a module type to a profile is optional.

### Attributes

Depending on the module type's assigned [profile](./moduletypeprofile.md) (if any), one or more user-defined attributes may be available to configure.
