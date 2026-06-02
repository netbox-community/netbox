# Users

A user represents an individual account in NetBox. Users authenticate to access the application, and may be granted permissions either directly or through their assigned [groups](./group.md). Each user can hold one or more API [tokens](./token.md) for use with the REST and GraphQL APIs.

NetBox extends Django's stock user model to support multiple API tokens per user, configurable [object permissions](./objectpermission.md), and integration with [remote authentication backends](../../administration/authentication/overview.md).

## Fields

### Username

A unique identifier used to log in. May contain letters, digits, and the characters `@ . + - _`. Username comparison is case-insensitive: a new user cannot be created whose username differs from an existing one only in letter case.

### First Name

The user's given name. Optional.

### Last Name

The user's family name. Optional.

### Email Address

The user's email address. Used by NetBox to send notifications (e.g. error reports) when configured to do so.

### Active

When unset, the user is treated as inactive and may not log in. Disabling a user is generally preferable to deletion, as it preserves the user's history in change records and other related objects.

### Staff Status

Designates whether the user can log into the (legacy) Django admin site. Most NetBox functionality is exposed via the standard UI; staff status is rarely needed.

### Superuser Status

Designates that the user is granted all permissions implicitly, bypassing all permission checks. Use sparingly.

### Date Joined

The date and time at which the user account was created.

### Groups

The set of [groups](./group.md) to which the user belongs. A user inherits all permissions assigned to each of their groups.

### Object Permissions

The set of [object permissions](./objectpermission.md) assigned directly to the user, in addition to those granted via group membership.
