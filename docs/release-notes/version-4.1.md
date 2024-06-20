# NetBox v4.1

## v4.1.0 (FUTURE)

### Breaking Changes

* Several filters deprecated in v4.0 have been removed (see [#15410](https://github.com/netbox-community/netbox/issues/15410)).
* The unit size for virtual disk size has been changed from 1 gigabyte to 1 megabyte. Existing values have been updated accordingly.

### New Features

### Enhancements

* [#7537](https://github.com/netbox-community/netbox/issues/7537) - Add a serial number field for virtual machines
* [#16359](https://github.com/netbox-community/netbox/issues/16359) - Enable plugins to embed content in the top navigation bar

### Other Changes

* [#14692](https://github.com/netbox-community/netbox/issues/14692) - Change atomic unit for virtual disks from 1GB to 1MB
* [#15410](https://github.com/netbox-community/netbox/issues/15410) - Removed various deprecated filters
* [#15908](https://github.com/netbox-community/netbox/issues/15908) - Indicate product edition in release data
* [#16388](https://github.com/netbox-community/netbox/issues/16388) - Move all change logging resources from `extras` to `core`

### REST API Changes

* The `/api/extras/object-changes/` endpoint has moved to `/api/core/object-changes/`
* virtualization.VirtualMachine
    * Added the optional `serial` field
* wireless.WirelessLink
    * Added the optional `distance` and `distance_unit` fields
