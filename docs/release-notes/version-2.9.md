# NetBox v2.9

## v2.9.11 (FUTURE)

### Enhancements

* [#5424](https://github.com/netbox-community/netbox/issues/5424) - Allow passing Python code to `nbshell` using `--command`

### Bug Fixes

* [#5383](https://github.com/netbox-community/netbox/issues/5383) - Fix setting user password via REST API
* [#5396](https://github.com/netbox-community/netbox/issues/5396) - Fix uniqueness constraint for virtual machine names
* [#5407](https://github.com/netbox-community/netbox/issues/5407) - Add direct link to secret on secrets list
* [#5408](https://github.com/netbox-community/netbox/issues/5408) - Fix updating secrets without setting new plaintext
* [#5410](https://github.com/netbox-community/netbox/issues/5410) - Restore tags field on cable connection forms
* [#5436](https://github.com/netbox-community/netbox/issues/5436) - Show assigned IP addresses in interfaces list

---

## v2.9.10 (2020-11-24)

### Enhancements

* [#5319](https://github.com/netbox-community/netbox/issues/5319) - Add USB types for power ports and outlets
* [#5337](https://github.com/netbox-community/netbox/issues/5337) - Add "splice" type for pass-through ports

### Bug Fixes

* [#5235](https://github.com/netbox-community/netbox/issues/5235) - Fix exception when editing IP address with a NAT IP assigned to a non-racked device
* [#5309](https://github.com/netbox-community/netbox/issues/5309) - Avoid extraneous database queries when manipulating objects
* [#5345](https://github.com/netbox-community/netbox/issues/5345) - Fix non-deterministic ordering of prefixes and IP addresses
* [#5350](https://github.com/netbox-community/netbox/issues/5350) - Filter available racks by selected group when creating a rack reservation
* [#5355](https://github.com/netbox-community/netbox/issues/5355) - Limit rack groups by selected site when editing a rack
* [#5356](https://github.com/netbox-community/netbox/issues/5356) - Populate manufacturer field when adding a device component template
* [#5360](https://github.com/netbox-community/netbox/issues/5360) - Clear VLAN assignments when setting interface mode to none

---

## v2.9.9 (2020-11-09)

### Enhancements

* [#5304](https://github.com/netbox-community/netbox/issues/5304) - Return server error messages as JSON when handling REST API requests
* [#5310](https://github.com/netbox-community/netbox/issues/5310) - Link to rack groups within rack list table
* [#5327](https://github.com/netbox-community/netbox/issues/5327) - Be more strict when capturing anticipated ImportError exceptions

### Bug Fixes

* [#5271](https://github.com/netbox-community/netbox/issues/5271) - Fix auto-population of region field when editing a device
* [#5314](https://github.com/netbox-community/netbox/issues/5314) - Fix config context rendering when multiple tags are assigned to an object
* [#5316](https://github.com/netbox-community/netbox/issues/5316) - Dry running scripts should not trigger webhooks
* [#5324](https://github.com/netbox-community/netbox/issues/5324) - Add missing template extension tags for plugins for VM interface view
* [#5328](https://github.com/netbox-community/netbox/issues/5328) - Fix CreatedUpdatedFilterTest when running in non-UTC timezone
* [#5331](https://github.com/netbox-community/netbox/issues/5331) - Fix filtering of sites by null region

---

## v2.9.8 (2020-10-30)

### Enhancements

* [#4559](https://github.com/netbox-community/netbox/issues/4559) - Improve device/VM context data rendering performance

### Bug Fixes

* [#3672](https://github.com/netbox-community/netbox/issues/3672) - Fix a caching issue causing incorrect related object counts in API responses
* [#5113](https://github.com/netbox-community/netbox/issues/5113) - Fix incorrect caching of permission object assignments to user groups in the admin panel
* [#5243](https://github.com/netbox-community/netbox/issues/5243) - Redirect user to appropriate tab after modifying device components
* [#5273](https://github.com/netbox-community/netbox/issues/5273) - Fix exception when validating a new permission with no models selected
* [#5282](https://github.com/netbox-community/netbox/issues/5282) - Fix high CPU load when LDAP authentication is enabled
* [#5285](https://github.com/netbox-community/netbox/issues/5285) - Plugins no longer need to define `app_name` for API URLs to be included in the root view

---

## v2.9.7 (2020-10-12)

### Bug Fixes

* [#5231](https://github.com/netbox-community/netbox/issues/5231) - Fix KeyError exception when viewing object with custom link and debugging is disabled

---

## v2.9.6 (2020-10-09)

### Bug Fixes

* [#5229](https://github.com/netbox-community/netbox/issues/5229) - Fix AttributeError exception when LDAP authentication is enabled

---

## v2.9.5 (2020-10-09)

### Enhancements

* [#5202](https://github.com/netbox-community/netbox/issues/5202) - Extend the available context data when rendering custom links

### Bug Fixes

* [#4523](https://github.com/netbox-community/netbox/issues/4523) - Populate site vlan list when bulk editing interfaces under certain circumstances
* [#5174](https://github.com/netbox-community/netbox/issues/5174) - Ensure consistent alignment of rack elevations
* [#5175](https://github.com/netbox-community/netbox/issues/5175) - Fix toggling of rack elevation order
* [#5184](https://github.com/netbox-community/netbox/issues/5184) - Fix missing Power Utilization
* [#5197](https://github.com/netbox-community/netbox/issues/5197) - Limit duplicate IPs shown on IP address view
* [#5199](https://github.com/netbox-community/netbox/issues/5199) - Change default LDAP logging to INFO
* [#5201](https://github.com/netbox-community/netbox/issues/5201) - Fix missing querystring when bulk editing/deleting VLAN Group VLANs when selecting "select all x items matching query"
* [#5206](https://github.com/netbox-community/netbox/issues/5206) - Apply user pagination preferences to all paginated object lists
* [#5211](https://github.com/netbox-community/netbox/issues/5211) - Add missing `has_primary_ip` filter for virtual machines
* [#5217](https://github.com/netbox-community/netbox/issues/5217) - Prevent erroneous removal of prefetched GenericForeignKey data from tables
* [#5218](https://github.com/netbox-community/netbox/issues/5218) - Raise validation error if a power port's `allocated_draw` exceeds its `maximum_draw`
* [#5220](https://github.com/netbox-community/netbox/issues/5220) - Fix API patch request against IP Address endpoint with null assigned_object_type 
* [#5221](https://github.com/netbox-community/netbox/issues/5221) - Fix bulk component creation for virtual machines
* [#5224](https://github.com/netbox-community/netbox/issues/5224) - Don't allow a rear port to have fewer positions than the number of mapped front ports
* [#5226](https://github.com/netbox-community/netbox/issues/5226) - Custom choice fields should be blank initially if no default choice has been designated

---

## v2.9.4 (2020-09-23)

**NOTE:** This release removes support for the `DEFAULT_TIMEOUT` parameter under `REDIS` database configuration. Set `RQ_DEFAULT_TIMEOUT` as a global configuration parameter instead.

**NOTE:** Any permissions referencing the legacy ReportResult model (e.g. `extras.view_reportresult`) should be updated to reference the Report model.

### Enhancements

* [#1755](https://github.com/netbox-community/netbox/issues/1755) - Toggle order in which rack elevations are displayed
* [#5128](https://github.com/netbox-community/netbox/issues/5128) - Increase maximum rear port positions from 64 to 1024
* [#5134](https://github.com/netbox-community/netbox/issues/5134) - Display full hierarchy in breadcrumbs for sites/racks
* [#5149](https://github.com/netbox-community/netbox/issues/5149) - Add rack group field to device edit form
* [#5164](https://github.com/netbox-community/netbox/issues/5164) - Show total rack count per rack group under site view
* [#5171](https://github.com/netbox-community/netbox/issues/5171) - Introduce the `RQ_DEFAULT_TIMEOUT` configuration parameter

### Bug Fixes

* [#5050](https://github.com/netbox-community/netbox/issues/5050) - Fix potential failure on `0016_replicate_interfaces` schema migration from old release
* [#5066](https://github.com/netbox-community/netbox/issues/5066) - Update `view_reportresult` to `view_report` permission
* [#5075](https://github.com/netbox-community/netbox/issues/5075) - Include a VLAN membership view for VM interfaces
* [#5105](https://github.com/netbox-community/netbox/issues/5105) - Validation should fail when reassigning a primary IP from device to VM
* [#5109](https://github.com/netbox-community/netbox/issues/5109) - Fix representation of custom choice field values for webhook data
* [#5108](https://github.com/netbox-community/netbox/issues/5108) - Fix execution of reports via CLI
* [#5111](https://github.com/netbox-community/netbox/issues/5111) - Allow use of tuples when specifying ObjectVar `query_params`
* [#5118](https://github.com/netbox-community/netbox/issues/5118) - Specifying an empty list of tags should clear assigned tags (REST API)
* [#5133](https://github.com/netbox-community/netbox/issues/5133) - Fix disassociation of an IP address from a VM interface
* [#5136](https://github.com/netbox-community/netbox/issues/5136) - Fix exception when bulk editing interface 802.1Q mode
* [#5156](https://github.com/netbox-community/netbox/issues/5156) - Add missing "add" button to rack reservations list
* [#5167](https://github.com/netbox-community/netbox/issues/5167) - Support filtering ObjectChanges by multiple users

---

## v2.9.3 (2020-09-04)

### Enhancements

* [#4977](https://github.com/netbox-community/netbox/issues/4977) - Redirect authenticated users from login view
* [#5048](https://github.com/netbox-community/netbox/issues/5048) - Show the device/VM name when editing a component
* [#5072](https://github.com/netbox-community/netbox/issues/5072) - Add REST API filters for image attachments
* [#5080](https://github.com/netbox-community/netbox/issues/5080) - Add 8P6C, 8P4C, 8P2C port types

### Bug Fixes

* [#5046](https://github.com/netbox-community/netbox/issues/5046) - Disabled plugin menu items are no longer clickable
* [#5063](https://github.com/netbox-community/netbox/issues/5063) - Fix "add device" link in rack elevations for opposite side of half-depth devices
* [#5074](https://github.com/netbox-community/netbox/issues/5074) - Fix inclusion of VC member interfaces when viewing VC master
* [#5078](https://github.com/netbox-community/netbox/issues/5078) - Fix assignment of existing IP addresses to interfaces via web UI
* [#5081](https://github.com/netbox-community/netbox/issues/5081) - Fix exception during webhook processing with custom select field
* [#5085](https://github.com/netbox-community/netbox/issues/5085) - Fix ordering by assignment in IP addresses table
* [#5087](https://github.com/netbox-community/netbox/issues/5087) - Restore label field when editing console server ports, power ports, and power outlets
* [#5089](https://github.com/netbox-community/netbox/issues/5089) - Redirect to device view after editing component
* [#5090](https://github.com/netbox-community/netbox/issues/5090) - Fix status display for console/power/interface connections
* [#5091](https://github.com/netbox-community/netbox/issues/5091) - Avoid KeyError when handling invalid table preferences
* [#5095](https://github.com/netbox-community/netbox/issues/5095) - Show assigned prefixes in VLANs list

---

## v2.9.2 (2020-08-27)

### Enhancements

* [#5055](https://github.com/netbox-community/netbox/issues/5055) - Add tags column to device/VM component list tables
* [#5056](https://github.com/netbox-community/netbox/issues/5056) - Add interface and parent columns to IP address list

### Bug Fixes

* [#4988](https://github.com/netbox-community/netbox/issues/4988) - Fix ordering of rack reservations with identical creation times
* [#5002](https://github.com/netbox-community/netbox/issues/5002) - Correct OpenAPI definition for `available-prefixes` endpoint
* [#5035](https://github.com/netbox-community/netbox/issues/5035) - Fix exception when modifying an IP address assigned to a VM
* [#5038](https://github.com/netbox-community/netbox/issues/5038) - Fix validation of primary IPs assigned to virtual machines
* [#5040](https://github.com/netbox-community/netbox/issues/5040) - Limit SLAAC status to IPv6 addresses
* [#5041](https://github.com/netbox-community/netbox/issues/5041) - Fix form tabs when assigning an IP to a VM interface
* [#5042](https://github.com/netbox-community/netbox/issues/5042) - Fix display of SLAAC label for IP addresses status
* [#5045](https://github.com/netbox-community/netbox/issues/5045) - Allow assignment of interfaces to non-master VC peer LAG during import
* [#5058](https://github.com/netbox-community/netbox/issues/5058) - Correct URL for front rack elevation images when using external storage
* [#5059](https://github.com/netbox-community/netbox/issues/5059) - Fix inclusion of checkboxes for interfaces in virtual machine view
* [#5060](https://github.com/netbox-community/netbox/issues/5060) - Fix validation when bulk-importing child devices
* [#5061](https://github.com/netbox-community/netbox/issues/5061) - Allow adding/removing tags when bulk editing virtual machine interfaces

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
* Backward compatibility for the old `webhooks` Redis queue name has been dropped. Ensure that your `REDIS` configuration parameter specifies both the `tasks` and `caching` databases.

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
