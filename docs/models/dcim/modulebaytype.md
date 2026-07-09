# Module Bay Types

Module bay types are user-defined labels that can be assigned to [module bays](./modulebay.md) and [module types](./moduletype.md) to restrict which modules may be installed into which bays. This is useful for modeling chassis hardware where not every bay accepts every type of line card.

When **both** a module bay and the module type being installed have at least one bay type assigned, NetBox will check for a non-empty intersection. If the two sets share no bay types in common, the installation will be rejected as incompatible.

If either the bay or the module type has **no bay types assigned**, the constraint is not applied and any module type may be installed — this preserves backwards compatibility with existing data.

!!! tip
    Bay types function as an allow-list: assign the same type to a bay and to the module types that fit it, and leave the type unset on bays or module types where no restriction is needed.

## Fields

### Name

A unique human-readable name for the bay type (e.g. `LC Line Card`, `Power Supply`, `Fan Tray`).

### Slug

A URL-friendly identifier derived from the name.

### Manufacturer

An optional [manufacturer](./manufacturer.md) associated with this bay type. Useful when a vendor uses proprietary slot designations.

### Description

A brief description of the bay type.

### Comments

Free-form Markdown-supported notes.