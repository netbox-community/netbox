# Modules

A module is a field-replaceable hardware component installed within a device which houses its own child components. The most common example is a chassis-based router or switch.

Similar to devices, modules are instantiated from [module types](./moduletype.md), and any components associated with the module type are automatically instantiated on the new model. Each module must be installed within a [module bay](./modulebay.md) on a [device](./device.md), and each module bay may have only one module installed in it.

## Fields

### Device

The parent [device](./device.md) into which the module is installed.

### Module Bay

The [module bay](./modulebay.md) into which the module is installed.

### Module Type

The [module type](./moduletype.md) which represents the physical make & model of hardware. By default, module components will be instantiated automatically from the module type when creating a new module.

### Status

The module's operational status.

!!! tip
    Additional statuses may be defined by setting `Module.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Serial Number

The unique physical serial number assigned to this module by its manufacturer.

### Asset Tag

A unique, locally-administered label used to identify hardware resources.

### Replicate Components

Controls whether templates module type components are automatically added when creating a new module.

### Adopt Components

Controls whether pre-existing components assigned to the device with the same names as components that would be created automatically will be assigned to the new module.
