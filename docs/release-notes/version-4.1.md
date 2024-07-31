# NetBox v4.1

## v4.1.0 (FUTURE)

### Breaking Changes

* Several filters deprecated in v4.0 have been removed (see [#15410](https://github.com/netbox-community/netbox/issues/15410)).
* The unit size for virtual disk size has been changed from 1 gigabyte to 1 megabyte. Existing values have been updated accordingly.
* The `min_vid` and `max_vid` fields on the VLAN group model have been replaced with `vid_ranges`, an array of starting and ending integer pairs.
* The five individual event type fields on the EventRule model have been replaced by a single `event_types` array field, indicating each assigned event type by name.
* The `validate()` method on CustomValidator subclasses now **must** accept the request argument (deprecated in v4.0 by #14279).

### New Features

#### Circuit Groups ([#7025](https://github.com/netbox-community/netbox/issues/7025))

Circuits can now be assigned to groups for administrative purposes. Each circuit may be assigned to multiple groups, and each assignment may optionally indicate a priority (primary, secondary, or tertiary).

#### VLAN Group ID Ranges ([#9627](https://github.com/netbox-community/netbox/issues/9627))

The VLAN group model has been enhanced to support multiple VLAN ID (VID) ranges, whereas previously it could track only a single beginning and ending VID. VID ranges are stored as an array of beginning and ending (inclusive) integers.

#### Rack Types ([#12826](https://github.com/netbox-community/netbox/issues/12826))

A new rack type model has been introduced, which functions similar to the device type model. Users can now define a common make and model of rack, the attributes of which are automatically populated when creating a new rack of that type.

#### Plugins Catalog Integration ([#14731](https://github.com/netbox-community/netbox/issues/14731))

The NetBox UI now integrates directly with the canonical plugins catalog hosted by NetBox Labs. In addition to locally installed plugins, users can explore available plugins and check for newer releases.

#### User Notifications ([#15621](https://github.com/netbox-community/netbox/issues/15621))

NetBox now includes a user notification system. Users can subscribe to individual objects and be alerted to changes live within the web interface. Additionally, event rules can now trigger notifications to specific users and/or groups. Plugins can also employ this notification system for their own purposes.

### Enhancements

* [#7537](https://github.com/netbox-community/netbox/issues/7537) - Add a serial number field for virtual machines
* [#8984](https://github.com/netbox-community/netbox/issues/8984) - Enable filtering of custom script output by log level
* [#11969](https://github.com/netbox-community/netbox/issues/11969) - Support for tracking airflow on racks and module types
* [#15156](https://github.com/netbox-community/netbox/issues/15156) - Add `display_url` field to all REST API serializers
* [#16359](https://github.com/netbox-community/netbox/issues/16359) - Enable plugins to embed content in the top navigation bar
* [#16580](https://github.com/netbox-community/netbox/issues/16580) - Enable individual views to enforce `LOGIN_REQUIRED` selectively (remove `AUTH_EXEMPT_PATHS`)
* [#16776](https://github.com/netbox-community/netbox/issues/16776) - Added an `alerts()` method to `PluginTemplateExtension` for embedding important information about specific objects 
* [#16782](https://github.com/netbox-community/netbox/issues/16782) - Enable filtering of selection choices for object type custom fields
* [#16866](https://github.com/netbox-community/netbox/issues/16866) - Introduced a mechanism for plugins to register custom event types (for use with user notifications)

### Plugins

* [#16726](https://github.com/netbox-community/netbox/issues/16726) - Extend `PluginTemplateExtension` to enable registering multiple models

### Other Changes

* [#14692](https://github.com/netbox-community/netbox/issues/14692) - Change atomic unit for virtual disks from 1GB to 1MB
* [#14861](https://github.com/netbox-community/netbox/issues/14861) - The URL path for UI views concerning virtual disks has been standardized to `/virtualization/virtual-disks/`
* [#15410](https://github.com/netbox-community/netbox/issues/15410) - Removed various deprecated filters
* [#15908](https://github.com/netbox-community/netbox/issues/15908) - Indicate product edition in release data
* [#16388](https://github.com/netbox-community/netbox/issues/16388) - Move all change logging resources from `extras` to `core`
* [#16884](https://github.com/netbox-community/netbox/issues/16884) - Remove the ID column from the default table configuration for changelog records

### REST API Changes

* The `/api/extras/object-changes/` endpoint has moved to `/api/core/object-changes/`
* Added the following endpoints:
    * `/api/circuits/circuit-groups/`
    * `/api/circuits/circuit-group-assignments/`
    * `/api/dcim/rack-types/`
* circuits.Circuit
    * Added the `assignments` field, which lists all group assignments
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
