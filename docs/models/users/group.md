# Groups

A group is a collection of [users](./user.md) which share a common set of permissions. Assigning [object permissions](./objectpermission.md) to a group, rather than to individual users, simplifies the administration of permissions for related users (e.g. members of a particular team).

A user inherits the union of all permissions assigned to each group of which they are a member, in addition to any permissions assigned directly to the user.

## Fields

### Name

A unique name for the group.

### Description

A short description of the group's role or membership.

### Object Permissions

The set of [object permissions](./objectpermission.md) granted to all members of this group.
