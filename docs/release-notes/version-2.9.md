# NetBox v2.8

## v2.9.0 (FUTURE)

### New Features

#### Object-Based Permissions ([#554](https://github.com/netbox-community/netbox/issues/554))

NetBox v2.9 replaces Django's built-in permissions framework with one that supports object-based assignment of permissions using arbitrary constraints. When granting a user or group to perform a certain action on one or more types of objects, an administrator can optionally specify a set of attributes. The permission will apply only to objects which match the specified attributes. For example, assigning permission to modify devices with the attribute filter `{"tenant__group__name": "Customers"}` would grant the permission only for devices assigned to a tenant belonging to the "Customers" group.

### Configuration Changes

* `REMOTE_AUTH_DEFAULT_PERMISSIONS` now takes a dictionary rather than a list. This is a mapping of permission names to a dictionary of constraining attributes, or `None`. For example, `['dcim.add_site', 'dcim.change_site']` would become `{'dcim.add_site': None, 'dcim.change_site': None}`.

### Other Changes

* The `secrets.activate_userkey` permission no longer exists. Instead, `secrets.change_userkey` is checked to determine whether a user has the ability to activate a UserKey.
