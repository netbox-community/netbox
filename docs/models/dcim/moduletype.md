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

!!! info "The `airflow` field was introduced in NetBox v4.1."

The direction in which air circulates through the device chassis for cooling.
