# NetBox v4.1

## v4.1.0 (FUTURE)

### Breaking Changes

* Several filters deprecated in v4.0 have been removed (see [#15410](https://github.com/netbox-community/netbox/issues/15410)).
* The unit size for virtual disk size has been changed from 1 gigabyte to 1 megabyte. Existing values have been updated accordingly.

### New Features

### Enhancements

* [#7537](https://github.com/netbox-community/netbox/issues/7537) - Add a serial number field for virtual machines
* [#8984](https://github.com/netbox-community/netbox/issues/8984) - Enable filtering of custom script output by log level
* [#15156](https://github.com/netbox-community/netbox/issues/15156) - Add `display_url` field to all REST API serializers
* [#16359](https://github.com/netbox-community/netbox/issues/16359) - Enable plugins to embed content in the top navigation bar
* [#16580](https://github.com/netbox-community/netbox/issues/16580) - Enable individual views to enforce `LOGIN_REQUIRED` selectively (remove `AUTH_EXEMPT_PATHS`)

### Plugins

* [#16726](https://github.com/netbox-community/netbox/issues/16726) - Extend `PluginTemplateExtension` to enable registering multiple models

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
