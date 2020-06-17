# NetBox v2.8

## v2.9.0 (FUTURE)

### New Features

#### Object-Based Permissions ([#554](https://github.com/netbox-community/netbox/issues/554))

NetBox v2.9 replaces Django's built-in permissions framework with one that supports object-based assignment of permissions using arbitrary constraints. When granting a user or group to perform a certain action on one or more types of objects, an administrator can optionally specify a set of constraints. The permission will apply only to objects which match the specified constraints. For example, assigning permission to modify devices with the constraint `{"tenant__group__name": "Customers"}` would grant the permission only for devices assigned to a tenant belonging to the "Customers" group.

### Enhancements

* [#3703](https://github.com/netbox-community/netbox/issues/3703) - Tags must be created administratively before being assigned to an object
* [#4615](https://github.com/netbox-community/netbox/issues/4615) - Add `label` field for all device components
* [#4742](https://github.com/netbox-community/netbox/issues/4742) - Add tagging for cables, power panels, and rack reservations

### Configuration Changes

* If in use, LDAP authentication must be enabled by setting `REMOTE_AUTH_BACKEND` to `'netbox.authentication.LDAPBackend'`. (LDAP configuration parameters in `ldap_config.py` remain unchanged.)
* `REMOTE_AUTH_DEFAULT_PERMISSIONS` now takes a dictionary rather than a list. This is a mapping of permission names to a dictionary of constraining attributes, or `None`. For example, `['dcim.add_site', 'dcim.change_site']` would become `{'dcim.add_site': None, 'dcim.change_site': None}`.

### REST API Changes

* The count of `tagged_items` is no longer included when viewing the tags list when `brief` is passed.
* The assignment of tags to an object is now achieved in the same manner as specifying any other related device. The `tags` field accepts a list of JSON objects each matching a desired tag. (Alternatively, a list of numeric primary keys corresponding to tags may be passed instead.) For example:

```json
"tags": [
  {"name": "First Tag"},
  {"name": "Second Tag"}
]
```

* The `tags` field of an object now includes a more complete representation of each tag, rather than just its name.

### Other Changes

* The `secrets.activate_userkey` permission no longer exists. Instead, `secrets.change_userkey` is checked to determine whether a user has the ability to activate a UserKey.
* The `users.delete_token` permission is no longer enforced. All users are permitted to delete their own API tokens.
* Dropped backward compatibility for the `webhooks` Redis queue configuration (use `tasks` instead).
* Dropped backward compatibility for the `/admin/webhook-backend-status` URL (moved to `/admin/background-tasks/`).
