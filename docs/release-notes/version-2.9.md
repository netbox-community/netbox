# NetBox v2.9

## v2.9.2 (FUTURE)

### Bug Fixes

* [#4988](https://github.com/netbox-community/netbox/issues/4988) - Fix ordering of rack reservations with identical creation times
* [#5035](https://github.com/netbox-community/netbox/issues/5035) - Fix exception when modifying an IP address assigned to a VM
* [#5038](https://github.com/netbox-community/netbox/issues/5038) - Fix validation of primary IPs assigned to virtual machines
* [#5040](https://github.com/netbox-community/netbox/issues/5040) - Limit SLAAC status to IPv6 addresses
* [#5041](https://github.com/netbox-community/netbox/issues/5041) - Fix form tabs when assigning an IP to a VM interface
* [#5042](https://github.com/netbox-community/netbox/issues/5042) - Fix display of SLAAC label for IP addresses status
* [#5045](https://github.com/netbox-community/netbox/issues/5045) - Allow assignment of interfaces to non-master VC peer LAG during import

---

## v2.9.1 (2020-08-22)

### Enhancements

* [#4540](https://github.com/netbox-community/netbox/issues/4540) - Add IP address status type for SLAAC
* [#4814](https://github.com/netbox-community/netbox/issues/4814) - Allow nested LAG interfaces
* [#4991](https://github.com/netbox-community/netbox/issues/4991) - Add Python and NetBox versions to error page
* [#5033](https://github.com/netbox-community/netbox/issues/5033) - Support backward compatibility for `REMOTE_AUTH_BACKEND` configuration parameter

---

## v2.9.0 (2020-08-21)

**Note:** Redis 4.0 or later is required for this release.

### New Features

#### Object-Based Permissions ([#554](https://github.com/netbox-community/netbox/issues/554))

NetBox v2.9 replaces Django's built-in permissions framework with one that supports object-based assignment of permissions using arbitrary constraints. When granting a user or group permission to perform a certain action on one or more types of objects, an administrator can optionally specify a set of constraints. The permission will apply only to objects which match the specified constraints. For example, assigning permission to modify devices with the constraint `{"tenant__group__name": "Customers"}` would allow the associated users/groups to perform an action only on devices assigned to a tenant belonging to the "Customers" group.

#### Background Execution of Scripts & Reports ([#2006](https://github.com/netbox-community/netbox/issues/2006))

When running a report or custom script, its execution is now queued for background processing and the user receives an immediate response indicating its status. This prevents long-running scripts from resulting in a timeout error. Once the execution has completed, the page will automatically refresh to display its results. Both scripts and reports now store their output in the new JobResult model. (The ReportResult model has been removed.)

#### Named Virtual Chassis ([#2018](https://github.com/netbox-community/netbox/issues/2018))

The VirtualChassis model now has a mandatory `name` field. Names are assigned to the virtual chassis itself rather than referencing the master VC member. Additionally, the designation of a master is now optional: a virtual chassis may have only non-master members.

#### Changes to Tag Creation ([#3703](https://github.com/netbox-community/netbox/issues/3703))

Tags are no longer created automatically: A tag must be created by a user before it can be applied to any object. Additionally, the REST API representation of assigned tags has been expanded to be consistent with other objects.

#### Dedicated Model for VM Interfaces ([#4721](https://github.com/netbox-community/netbox/issues/4721))

A new model has been introduced to represent virtual machine interfaces. Although this change is largely transparent to the end user, note that the IP address model no longer has a foreign key to the Interface model under the DCIM app. This has been replaced with a generic foreign key named `assigned_object`.

#### REST API Endpoints for Users and Groups ([#4877](https://github.com/netbox-community/netbox/issues/4877))

Two new REST API endpoints have been added to facilitate the retrieval and manipulation of users and groups:

* `/api/users/groups/`
* `/api/users/users/`

### Enhancements

* [#4615](https://github.com/netbox-community/netbox/issues/4615) - Add `label` field for all device components and component templates
* [#4639](https://github.com/netbox-community/netbox/issues/4639) - Improve performance of web UI prefixes list
* [#4742](https://github.com/netbox-community/netbox/issues/4742) - Add tagging for cables, power panels, and rack reservations
* [#4788](https://github.com/netbox-community/netbox/issues/4788) - Add dedicated views for all device components
* [#4792](https://github.com/netbox-community/netbox/issues/4792) - Add bulk rename capability for console and power ports
* [#4793](https://github.com/netbox-community/netbox/issues/4793) - Add `description` field to device component templates
* [#4795](https://github.com/netbox-community/netbox/issues/4795) - Add bulk disconnect capability for console and power ports
* [#4806](https://github.com/netbox-community/netbox/issues/4806) - Add a `url` field to all API serializers
* [#4807](https://github.com/netbox-community/netbox/issues/4807) - Add bulk edit ability for device bay templates
* [#4817](https://github.com/netbox-community/netbox/issues/4817) - Standardize device/VM component `name` field to 64 characters
* [#4837](https://github.com/netbox-community/netbox/issues/4837) - Use dynamic form widget for relationships to MPTT objects (e.g. regions)
* [#4840](https://github.com/netbox-community/netbox/issues/4840) - Enable change logging for config contexts
* [#4885](https://github.com/netbox-community/netbox/issues/4885) - Add MultiChoiceVar for custom scripts
* [#4940](https://github.com/netbox-community/netbox/issues/4940) - Add an `occupied` field to rack unit representations for rack elevation views
* [#4945](https://github.com/netbox-community/netbox/issues/4945) - Add a user-friendly 403 error page
* [#4969](https://github.com/netbox-community/netbox/issues/4969) - Replace secret role user/group assignment with object permissions
* [#4982](https://github.com/netbox-community/netbox/issues/4982) - Extended ObjectVar to allow filtering API query
* [#4994](https://github.com/netbox-community/netbox/issues/4994) - Add `cable` attribute to PowerFeed API serializer
* [#4997](https://github.com/netbox-community/netbox/issues/4997) - The browsable API now lists available endpoints alphabetically
* [#5024](https://github.com/netbox-community/netbox/issues/5024) - List available options for choice fields within CSV import forms

### Configuration Changes

* If using NetBox's built-in remote authentication backend, update `REMOTE_AUTH_BACKEND` to `'netbox.authentication.RemoteUserBackend'`, as the authentication class has moved.
* If using LDAP authentication, set `REMOTE_AUTH_BACKEND` to `'netbox.authentication.LDAPBackend'`. (LDAP configuration parameters in `ldap_config.py` remain unchanged.)
* `REMOTE_AUTH_DEFAULT_PERMISSIONS` now takes a dictionary rather than a list. This is a mapping of permission names to a dictionary of constraining attributes, or `None`. For example, `['dcim.add_site', 'dcim.change_site']` would become `{'dcim.add_site': None, 'dcim.change_site': None}`.

### REST API Changes

* Added new endpoints for users, groups, and permissions under `/api/users/`.
* A `url` field is now included on all object representations, identifying the unique REST API URL for each object.
* The `tags` field of an object now includes a more complete representation of each tag, rather than just its name.
* The assignment of tags to an object is now achieved in the same manner as specifying any other related device. The `tags` field accepts a list of JSON objects each matching a desired tag. (Alternatively, a list of numeric primary keys corresponding to tags may be passed instead.) For example:

```json
"tags": [
  {"name": "First Tag"},
  {"name": "Second Tag"}
]
```

* Legacy numeric values for choice fields are no longer conveyed or accepted.
* circuits.CircuitTermination: Added `cable` field
* dcim.Cable: Added `tags` field
* dcim.ConsolePort: Added `label` field
* dcim.ConsolePortTemplate: Added `description` and `label` fields
* dcim.ConsoleServerPort: Added `label` field
* dcim.ConsoleServerPortTemplate: Added `description` and `label` fields
* dcim.DeviceBay: Added `label` field
* dcim.DeviceBayTemplate: Added `description` and `label` fields
* dcim.FrontPort: Added `label` field
* dcim.FrontPortTemplate: Added `description` and `label` fields
* dcim.Interface: Added `label` field
* dcim.InterfaceTemplate: Added `description` and `label` fields
* dcim.PowerFeed: Added `cable` field
* dcim.PowerPanel: Added `tags` field
* dcim.PowerPort: Added ``label` field
* dcim.PowerPortTemplate: Added `description` and `label` fields
* dcim.PowerOutlet: Added `label` field
* dcim.PowerOutletTemplate: Added `description` and `label` fields
* dcim.Rack: Added an `occupied` field to rack unit representations for rack elevation views
* dcim.RackGroup: Added a `_depth` attribute indicating an object's position in the tree.
* dcim.RackReservation: Added `tags` field
* dcim.RearPort: Added `label` field
* dcim.RearPortTemplate: Added `description` and `label` fields
* dcim.Region: Added a `_depth` attribute indicating an object's position in the tree.
* dcim.VirtualChassis: Added `name` field (required)
* extras.ConfigContext: Added `created` and `last_updated` fields
* extras.JobResult: Added the `/api/extras/job-results/` endpoint
* extras.Report: The `failed` field has been removed. The `completed` (boolean) and `status` (string) fields have been introduced to convey the status of a report's most recent execution. Additionally, the `result` field now conveys the nested representation of a JobResult.
* extras.Script: Added `module` and `result` fields. The `result` field now conveys the nested representation of a JobResult.
* extras.Tag: The count of `tagged_items` is no longer included when viewing the tags list when `brief` is passed.
* ipam.IPAddress: Removed `interface` field; replaced with `assigned_object` generic foreign key. This may represent either a device interface or a virtual machine interface. Assign an object by setting `assigned_object_type` and `assigned_object_id`.
* ipam.VRF: Added `display_name`
* tenancy.TenantGroup: Added a `_depth` attribute indicating an object's position in the tree.
* users.ObjectPermissions: Added the `/api/users/permissions/` endpoint
* virtualization.VMInterface: Removed `type` field (VM interfaces have no type)

### Other Changes

* A new model, `VMInterface` has been introduced to represent interfaces assigned to VirtualMachine instances. Previously, these interfaces utilized the DCIM model `Interface`. Instances will be replicated automatically upon upgrade, however any custom code which references or manipulates virtual machine interfaces will need to be updated accordingly.
* The `secrets.activate_userkey` permission no longer exists. Instead, `secrets.change_userkey` is checked to determine whether a user has the ability to activate a UserKey.
* The `users.delete_token` permission is no longer enforced. All users are permitted to delete their own API tokens.
* Dropped backward compatibility for the `webhooks` Redis queue configuration (use `tasks` instead).
* Dropped backward compatibility for the `/admin/webhook-backend-status` URL (moved to `/admin/background-tasks/`).
* Virtual chassis are now created by navigating to `/dcim/virtual-chassis/add/` rather than via the devices list.
* A name is required when creating a virtual chassis.
