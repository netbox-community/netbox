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

When adding component templates to a module type, the string `{module}` can be used to reference the `position` field of the module bay into which an instance of the module type is being installed.

For example, you can create a module type with interface templates named `Gi{module}/0/[1-48]`. When a new module of this type is "installed" to a module bay with a position of "3", NetBox will automatically name these interfaces `Gi3/0/[1-48]`.

Similarly, the string `{vc_position}` can be used in component template names to reference the
`vc_position` field of the device being provisioned, when that device is a member of a Virtual Chassis.

For example, an interface template named `Gi{vc_position}/{module}/0` installed on a Virtual Chassis
member with position `2` and module bay position `3` will be rendered as `Gi2/3/0`.

If the device is not a member of a Virtual Chassis, `{vc_position}` defaults to `0`. A custom
fallback value can be specified using the syntax `{vc_position:X}`, where `X` is the desired default.
For example, `{vc_position:1}` will render as `1` when no Virtual Chassis position is set.

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
