# Module Bays

Module bays represent a space or slot within a device in which a field-replaceable [module](./module.md) may be installed. A common example is that of a chassis-based switch such as the Cisco Nexus 9000 or Juniper EX9200. Modules, in turn, hold additional components that become available to the parent device.

!!! note
    If you need to model child devices rather than modules, use a [device bay](./devicebay.md) instead.

!!! tip
    Like most device components, module bays are instantiated automatically from [module bay templates](./modulebaytemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this module bay belongs.

### Module

The module to which this bay belongs (optional).

### Name

The module bay's name. Must be unique to the parent device.

### Label

An alternative physical label identifying the module bay.

### Position

The numeric position in which this module bay is situated. For example, this would be the number assigned to a slot within a chassis-based switch.

### Bay Types

Zero or more [module bay types](./modulebaytype.md) assigned to this bay. When at least one bay type is set, only module types that share a common bay type may be installed. Leave empty to allow any module type.

Bay types are importable via CSV, referenced by name. A bay type belonging to a manufacturer other than the module bay's own device may be referenced; this mirrors the UI and REST API, which likewise place no manufacturer restriction on the assignment. Since a bay type's uniqueness is scoped to `(manufacturer, name)` rather than name alone, more than one bay type may share a name; import prefers, in order, an exact match on the device's own manufacturer, then a global (manufacturer-less) bay type. If a name instead matches two or more bay types belonging to *other* manufacturers, with neither the device's own manufacturer nor a global type available to break the tie, the import is rejected rather than resolved to an arbitrary one.

### Enabled

Whether this module bay is enabled. Disabled module bays are not available for installation.

