# Module Bay Templates

A template for a module bay that will be created on all instantiations of the parent device type. See the [module bay](./modulebay.md) documentation for more detail.

[Bay types](./modulebaytype.md) assigned to a module bay template are copied to each instantiated module bay, so constraints defined on the device type propagate automatically to all devices of that type.

Bay types are importable and exportable as part of a device type's YAML definition (`module-bays[].module_bay_types`), referenced by name. A bay type belonging to a manufacturer other than the device type's own may be referenced; this mirrors the UI and REST API, which likewise place no manufacturer restriction on the assignment. Since a bay type's uniqueness is scoped to `(manufacturer, name)` rather than name alone, more than one bay type may share a name; import prefers, in order, an exact match on the device type's own manufacturer, then a global (manufacturer-less) bay type. If a name instead matches two or more bay types belonging to *other* manufacturers, with neither the device type's own manufacturer nor a global type available to break the tie, the import is rejected rather than resolved to an arbitrary one.
