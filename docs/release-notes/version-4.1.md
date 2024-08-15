# NetBox v4.1

## v4.1.0 (FUTURE)

!!! danger "Not for Production Use"
    This is a beta release of NetBox intended for testing and evaluation. **Do not use this software in production.** Also be aware that no upgrade path is provided to future releases.

### Breaking Changes

* Several filters deprecated in v4.0 have been removed (see [#15410](https://github.com/netbox-community/netbox/issues/15410)).
* The unit size for `VirtualMachine.disk` and `VirtualDisk.size` been changed from 1 gigabyte to 1 megabyte. Existing values have been updated accordingly.
* The `min_vid` and `max_vid` fields on the VLAN group model have been replaced with `vid_ranges`, an array of starting and ending integer pairs.
* The five individual event type fields on the EventRule model have been replaced by a single `event_types` array field, indicating each assigned event type by name.
* The UI views & API endpoints associate with change records have been moved from `/extras` to `/core`.
* The `validate()` method on CustomValidator subclasses now **must** accept the request argument (deprecated in v4.0 by #14279).

### New Features

#### Circuit Groups ([#7025](https://github.com/netbox-community/netbox/issues/7025))

Circuits can now be assigned to groups for administrative purposes. Each circuit may be assigned to multiple groups, and each assignment may optionally indicate a priority (primary, secondary, or tertiary).

#### VLAN Group ID Ranges ([#9627](https://github.com/netbox-community/netbox/issues/9627))

The VLAN group model has been enhanced to support multiple VLAN ID (VID) ranges, whereas previously it could track only a single beginning and ending VID. VID ranges are stored as an array of beginning and ending (inclusive) integer pairs.

#### Nested Device Modules ([#10500](https://github.com/netbox-community/netbox/issues/10500))

Module bays can now be nested to effect a hierarchical arrangement of modules within a device. A module installed within a device's module bay may itself have module bays into which child modules may be installed.

#### Rack Types ([#12826](https://github.com/netbox-community/netbox/issues/12826))

A new rack type model has been introduced, which functions similarly to the device type model. Users can now define a common make and model of rack, the attributes of which are automatically populated when creating a new rack of that type. Backward compatibility for racks with individually defined characteristics is fully retained.

#### Plugins Catalog Integration ([#14731](https://github.com/netbox-community/netbox/issues/14731))

The NetBox UI now integrates directly with the canonical [plugins catalog](https://netboxlabs.com/netbox-plugins/) hosted by NetBox Labs. In addition to locally installed plugins, users can explore available plugins and check for newer releases.

#### User Notifications ([#15621](https://github.com/netbox-community/netbox/issues/15621))

NetBox now includes a user notification system. Users can subscribe to individual objects and be alerted to changes live within the web interface. Additionally, event rules can now trigger notifications to specific users and/or groups. Plugins can also employ this notification system for their own purposes.

### Enhancements

* [#7537](https://github.com/netbox-community/netbox/issues/7537) - Add a serial number field for virtual machines
* [#8198](https://github.com/netbox-community/netbox/issues/8198) - Enable uniqueness enforcement for custom field values
* [#8984](https://github.com/netbox-community/netbox/issues/8984) - Enable filtering of custom script output by log level
* [#11969](https://github.com/netbox-community/netbox/issues/11969) - Support for tracking airflow on racks and module types
* [#14656](https://github.com/netbox-community/netbox/issues/14656) - Dynamically render custom field edit form depending on the selected field type
* [#15106](https://github.com/netbox-community/netbox/issues/15106) - Add distance tracking for wireless links
* [#15156](https://github.com/netbox-community/netbox/issues/15156) - Add `display_url` field to all REST API serializers
* [#16574](https://github.com/netbox-community/netbox/issues/16574) - Add `last_synced` time to REST API serializer for data sources
* [#16580](https://github.com/netbox-community/netbox/issues/16580) - Enable individual views to enforce `LOGIN_REQUIRED` selectively (remove `AUTH_EXEMPT_PATHS`)
* [#16782](https://github.com/netbox-community/netbox/issues/16782) - Enable filtering of selection choices for object type custom fields
* [#16907](https://github.com/netbox-community/netbox/issues/16907) - Updated user interface styling
* [#17051](https://github.com/netbox-community/netbox/issues/17051) - Introduced `ISOLATED_DEPLOYMENT` config parameter

### Bug Fixes (From Beta1)

* [#17086](https://github.com/netbox-community/netbox/issues/17086) - Fix exception when viewing a job with no related object
* [#17097](https://github.com/netbox-community/netbox/issues/17097) - Record static object representation when calling `NotificationGroup.notify()`
* [#17098](https://github.com/netbox-community/netbox/issues/17098) - Prevent automatic deletion of related notifications when deleting an object
* [#17159](https://github.com/netbox-community/netbox/issues/17159) - Correct file paths in plugin installation instructions
* [#17163](https://github.com/netbox-community/netbox/issues/17163) - Fix filtering of related services under IP address view
* [#17169](https://github.com/netbox-community/netbox/issues/17169) - Avoid duplicating catalog listings for installed plugins

### Plugins

* [#15692](https://github.com/netbox-community/netbox/issues/15692) - Introduce improved plugin support for background jobs
* [#16359](https://github.com/netbox-community/netbox/issues/16359) - Enable plugins to embed content in the top navigation bar
* [#16726](https://github.com/netbox-community/netbox/issues/16726) - Extend `PluginTemplateExtension` to enable registering multiple models
* [#16776](https://github.com/netbox-community/netbox/issues/16776) - Added an `alerts()` method to `PluginTemplateExtension` for embedding important information about specific objects
* [#16886](https://github.com/netbox-community/netbox/issues/16886) - Introduced a mechanism for plugins to register custom event types (for use with user notifications)

### Other Changes

* [#14692](https://github.com/netbox-community/netbox/issues/14692) - Change atomic unit for virtual disks from 1GB to 1MB
* [#14861](https://github.com/netbox-community/netbox/issues/14861) - The URL path for UI views concerning virtual disks has been standardized to `/virtualization/virtual-disks/`
* [#15410](https://github.com/netbox-community/netbox/issues/15410) - Removed various deprecated filters
* [#15908](https://github.com/netbox-community/netbox/issues/15908) - Indicate product edition in release data
* [#16388](https://github.com/netbox-community/netbox/issues/16388) - Move all change logging resources from `extras` to `core`
* [#16884](https://github.com/netbox-community/netbox/issues/16884) - Remove the ID column from the default table configuration for changelog records
* [#16988](https://github.com/netbox-community/netbox/issues/16988) - Relocated rack items in navigation menu

### REST API Changes

* The `/api/extras/object-changes/` endpoint has moved to `/api/core/object-changes/`
* Added the following endpoints:
    * `/api/circuits/circuit-groups/`
    * `/api/circuits/circuit-group-assignments/`
    * `/api/dcim/rack-types/`
* circuits.Circuit
    * Added the `assignments` field, which lists all group assignments
* core.DataSource
    * Added the read-only `last_synced` field
* dcim.ModuleBay
    * Added the optional `module` foreign key field
* dcim.ModuleBayTemplate
    * Added the optional `module_type` foreign key field
* dcim.ModuleType
    * Added the optional `airflow` choice field
* dcim.Rack
    * Added the optional `rack_type` foreign key field
    * Added the optional `airflow` choice field
* extras.CustomField
    * Added the `related_object_filter` JSON field for object and multi-object custom fields
* extras.EventRule
    * Removed the `type_create`, `type_update`, `type_delete`, `type_job_start`, and `type_job_end` boolean fields
    * Added the `event_types` array field
* ipam.VLANGroup
    * Removed the `min_vid` and `max_vid` fields
    * Added the `vid_ranges` field, and array of starting & ending VLAN IDs
* virtualization.VirtualMachine
    * Added the optional `serial` field
* wireless.WirelessLink
    * Added the optional `distance` and `distance_unit` fields
