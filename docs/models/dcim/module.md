# Modules

A module is a field-replaceable hardware component installed within a device which houses its own child components. The most common example is a chassis-based router or switch.

Similar to devices, modules are instantiated from [module types](./moduletype.md), and any components associated with the module type are automatically instantiated on the new model. Each module must be installed within a [module bay](./modulebay.md) on a [device](./device.md), and each module bay may have only one module installed in it.

## Moving Modules

An installed module can be moved to a different module bay after creation. The destination bay must be enabled and unoccupied. Moving a module relocates its entire subtree: the components installed by the module, the module bays belonging to it, and any child modules installed within those bays.

Component names, labels, and module bay positions derived from the module type's templates (for example, names containing `{module}`) are re-resolved for the destination bay. A component is renamed only when its current name matches exactly one of the module type's templates as resolved for the source bay; components whose names do not match any template resolution (including manually renamed components) are preserved as-is. All resulting names are validated against the destination device before the move is applied. A move is rejected when a template-derived name, label, or position would exceed the destination field's maximum length. A move is also rejected when a component's current value matched a template for the source bay but that template cannot be resolved for the destination bay's nesting depth.

Moving a module to a different device is supported only when the moved components carry no active topology or device-scoped configuration. A cross-device move is rejected while any moved component is cabled or marked as connected, has attached inventory items, or any moved interface has IP addresses, FHRP group assignments, tunnel terminations, L2VPN terminations, virtual circuit terminations, wireless links, wireless LAN assignments, VLANs (untagged, tagged, or Q-in-Q service), a VLAN translation policy, VDC assignments, or a VRF. A parent, bridge, LAG, power outlet to power port, or front/rear port mapping relation crossing the moved module's boundary in either direction also blocks the move. MAC addresses move together with their interfaces.

Via the REST API, a module can be moved by patching only `module_bay`; the device is derived from the target bay. Changing a module's type and moving it must be performed as separate operations.

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

## Bay Type Compatibility

If the module bay has [bay types](./modulebaytype.md) assigned and the module's type also has bay types assigned, NetBox verifies that the two sets share at least one type in common. An installation that fails this check will be rejected. The `is_bay_compatible` flag is exposed in the REST API to indicate compatibility status without performing a write.
