# Object Permissions

An object permission grants the ability to perform one or more actions (e.g. view, add, change, delete) against a defined set of object types, and may be restricted to a subset of objects matching a configured filter. Permissions are assigned to [users](./user.md) and/or [groups](./group.md); a user's effective permissions are the union of those assigned directly and those inherited via group membership.

See the [permissions documentation](../../administration/permissions.md) for a detailed walkthrough of how permissions are evaluated.

## Fields

### Name

A short, human-readable name for the permission.

### Description

An optional longer description of what the permission grants.

### Enabled

When unset, the permission is effectively disabled: it remains assigned to its users and groups, but is ignored during permission checks. This is useful for temporarily revoking access without altering assignments.

### Object Types

The list of NetBox model types to which this permission applies (e.g. `dcim.device`, `ipam.prefix`).

### Actions

The list of actions granted by the permission. The standard CRUD actions are `view`, `add`, `change`, and `delete`. Models may also register custom actions (e.g. `napalm` on `dcim.device`); custom actions appear here when supported by the selected object types.

### Constraints

An optional [Django ORM-style filter](https://docs.djangoproject.com/en/stable/topics/db/queries/#field-lookups) expressed as JSON. When set, the permission applies only to objects matching the filter. Multiple constraint sets may be supplied as a JSON list; an object matches if it satisfies any of the sets (logical OR).

For example, to grant a permission only over devices in a specific site:

```json
{"site__slug": "ny-dc1"}
```

Or, to apply the permission to devices in either of two sites:

```json
[
    {"site__slug": "ny-dc1"},
    {"site__slug": "sj-dc2"}
]
```

### Users & Groups

The [users](./user.md) and [groups](./group.md) to which this permission is assigned.
