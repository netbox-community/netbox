# Module Bay Templates

A template for a module bay that will be created on all instantiations of the parent device type. See the [module bay](./modulebay.md) documentation for more detail.

[Bay types](./modulebaytype.md) assigned to a module bay template are copied to each instantiated module bay, so constraints defined on the device type propagate automatically to all devices of that type.

Bay types are importable and exportable as part of a device type's YAML definition (`module-bays[].module_bay_types`), referenced by name. A referenced name is resolved against bay types belonging to the device type's own manufacturer or with no manufacturer set (global); a name may match both, since a bay type's uniqueness is scoped to `(manufacturer, name)` rather than name alone, in which case the manufacturer-specific type takes precedence.
