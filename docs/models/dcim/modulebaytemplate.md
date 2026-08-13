# Module Bay Templates

A template for a module bay that will be created on all instantiations of the parent device type. See the [module bay](./modulebay.md) documentation for more detail.

[Bay types](./modulebaytype.md) assigned to a module bay template are copied to each instantiated module bay, so constraints defined on the device type propagate automatically to all devices of that type.

Bay types are importable and exportable as part of a device type's YAML definition, referenced by name. Since a bay type's uniqueness is scoped to `(manufacturer, name)` rather than name alone, a global bay type and one scoped to the device type's own manufacturer may share a name; import resolves such a name to the manufacturer-specific bay type.
