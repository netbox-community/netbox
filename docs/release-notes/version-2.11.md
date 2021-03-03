# NetBox v2.11

## v2.11-beta1 (FUTURE)

**WARNING:** This is a beta release and is not suitable for production use. It is intended for development and evaluation purposes only. No upgrade path to the final v2.11 release will be provided from this beta, and users should assume that all data entered into the application will be lost.

### New Features

#### Mark as Connected Without a Cable ([#3648](https://github.com/netbox-community/netbox/issues/3648))

Cable termination objects (circuit terminations, power feeds, and most device components) can now be marked as "connected" without actually attaching a cable. This helps simplify the process of modeling an infrastructure boundary where you don't necessarily know or care what is connected to the far end of a cable, but still need to designate the near end termination.

In addition to the new `mark_connected` boolean field, the REST API representation of these objects now also includes a read-only boolean field named `_occupied`. This conveniently returns true if either a cable is attached or `mark_connected` is true.

#### Allow Assigning Devices to Locations ([#4971](https://github.com/netbox-community/netbox/issues/4971))

Devices can now be assigned to locations (formerly known as rack groups) within a site without needing to be assigned to a particular rack. This is handy for assigning devices to rooms or floors within a building where racks are not used. The `location` foreign key field has been added to the Device model to support this.

### Enhancements

* [#5370](https://github.com/netbox-community/netbox/issues/5370) - Extend custom field support to organizational models
* [#5375](https://github.com/netbox-community/netbox/issues/5375) - Add `speed` attribute to console port models
* [#5401](https://github.com/netbox-community/netbox/issues/5401) - Extend custom field support to device component models
* [#5451](https://github.com/netbox-community/netbox/issues/5451) - Add support for multiple-selection custom fields
* [#5894](https://github.com/netbox-community/netbox/issues/5894) - Use primary keys when filtering object lists by related objects in the UI
* [#5895](https://github.com/netbox-community/netbox/issues/5895) - Rename RackGroup to Location
* [#5901](https://github.com/netbox-community/netbox/issues/5901) - Add `created` and `last_updated` fields to device component models

### Other Changes

* [#1638](https://github.com/netbox-community/netbox/issues/1638) - Migrate all primary keys to 64-bit integers
* [#5873](https://github.com/netbox-community/netbox/issues/5873) - Use numeric IDs in all object URLs

### REST API Changes

* All primary keys are now 64-bit integers
* All device components
  * Added support for custom fields
  * Added `created` and `last_updated` fields to track object creation and modification
* All device component templates
  * Added `created` and `last_updated` fields to track object creation and modification
* All organizational models
  * Added support for custom fields
* All cable termination models (cabled device components, power feeds, and circuit terminations)
  * Added `mark_connected` boolean field to force connection status
  * Added `_occupied` read-only boolean field as common attribute for determining whether an object is occupied
* Renamed RackGroup to Location
  * The `/dcim/rack-groups/` endpoint is now `/dcim/locations/`
* dcim.Device
  * Added the `location` field
* dcim.PowerPanel
  * Renamed `rack_group` field to `location`
* dcim.Rack
  * Renamed `group` field to `location`
* extras.CustomField
  * Added new custom field type: `multi-select`
