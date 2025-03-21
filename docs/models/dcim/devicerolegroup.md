# Device Role Groups

[Device Roles](./devicerole.md) can be organized by custom groups. For instance, you might create one group called "Rack Infrastructure" and one called "Network Switches." The assignment of a device role to a group is optional.

Device role groups may be nested recursively to achieve a multi-level hierarchy. For example, you might have a group called "Rack Infrastructure" containing subgroups of individual device roles grouped by types.

## Fields

### Parent

The parent device role group (if any).

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)
