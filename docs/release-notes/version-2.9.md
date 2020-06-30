# NetBox v2.9

## v2.9.0 (FUTURE)

### New Features

#### Object-Based Permissions ([#554](https://github.com/netbox-community/netbox/issues/554))

NetBox v2.9 replaces Django's built-in permissions framework with one that supports object-based assignment of permissions using arbitrary constraints. When granting a user or group to perform a certain action on one or more types of objects, an administrator can optionally specify a set of constraints. The permission will apply only to objects which match the specified constraints. For example, assigning permission to modify devices with the constraint `{"tenant__group__name": "Customers"}` would grant the permission only for devices assigned to a tenant belonging to the "Customers" group.

### Enhancements

* [#2018](https://github.com/netbox-community/netbox/issues/2018) - Add `name` field to virtual chassis model
* [#3703](https://github.com/netbox-community/netbox/issues/3703) - Tags must be created administratively before being assigned to an object
* [#4615](https://github.com/netbox-community/netbox/issues/4615) - Add `label` field for all device components
* [#4742](https://github.com/netbox-community/netbox/issues/4742) - Add tagging for cables, power panels, and rack reservations
* [#4788](https://github.com/netbox-community/netbox/issues/4788) - Add dedicated views for all device components
* [#4792](https://github.com/netbox-community/netbox/issues/4792) - Add bulk rename capability for console and power ports
* [#4793](https://github.com/netbox-community/netbox/issues/4793) - Add `description` field to device component templates
* [#4795](https://github.com/netbox-community/netbox/issues/4795) - Add bulk disconnect capability for console and power ports

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
* A `label` field has been added to all device components and component templates.
* The IP address model now uses a generic foreign key to refer to the assigned interface. The `interface` field on the serializer has been replaced with `assigned_object_type` and `assigned_object_id` for write operations. If one exists, the assigned interface is available as `assigned_object`.
* The serialized representation of a virtual machine interface now includes only relevant fields: `type`, `lag`, `mgmt_only`, `connected_endpoint_type`, `connected_endpoint`, and `cable` are no longer included.
* dcim.VirtualChassis: Added a mandatory `name` field
* An optional `description` field has been added to all device component templates

### Other Changes

* A new model, `VMInterface` has been introduced to represent interfaces assigned to VirtualMachine instances. Previously, these interfaces utilized the DCIM model `Interface`. Instances will be replicated automatically upon upgrade, however any custom code which references or manipulates virtual machine interfaces will need to be updated accordingly.
* The `secrets.activate_userkey` permission no longer exists. Instead, `secrets.change_userkey` is checked to determine whether a user has the ability to activate a UserKey.
* The `users.delete_token` permission is no longer enforced. All users are permitted to delete their own API tokens.
* Dropped backward compatibility for the `webhooks` Redis queue configuration (use `tasks` instead).
* Dropped backward compatibility for the `/admin/webhook-backend-status` URL (moved to `/admin/background-tasks/`).
* Virtual chassis are now created by navigating to `/dcim/virtual-chassis/add` rather than via the devices list.
* A name is required when creating a virtual chassis.
