# Module Bay Templates

A template for a module bay that will be created on all instantiations of the parent device type. See the [module bay](./modulebay.md) documentation for more detail.

[Bay types](./modulebaytype.md) assigned to a module bay template are copied to each instantiated module bay, so constraints defined on the device type propagate automatically to all devices of that type.

Bay types are importable as part of a device type's or module type's YAML definition (`module-bays[].module_bay_types`), referenced by name. They are included when a device type is exported; a module type's exported definition omits its module bays entirely, so bay types are not carried through it. A referenced name is resolved against bay types belonging to the parent type's own manufacturer or with no manufacturer set (global); a name may match both, since a bay type's uniqueness is scoped to `(manufacturer, name)` rather than name alone, in which case the manufacturer-specific type takes precedence. A name matching only some other manufacturer's bay type is rejected rather than resolved to it.
