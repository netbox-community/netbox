# NetBox v2.12

## v2.12-beta1 (FUTURE)

### Other Changes

* [#5532](https://github.com/netbox-community/netbox/issues/5532) - Drop support for Python 3.6
* [#5994](https://github.com/netbox-community/netbox/issues/5994) - Drop support for `display_field` argument on ObjectVar

### REST API Changes

* dcim.Device
    * Removed the `display_name` attribute (use `display` instead)
* dcim.DeviceType
    * Removed the `display_name` attribute (use `display` instead)
* dcim.Rack
    * Removed the `display_name` attribute (use `display` instead)
* extras.ContentType
    * Removed the `display_name` attribute (use `display` instead)
* ipam.VLAN
    * Removed the `display_name` attribute (use `display` instead)
* ipam.VRF
    * Removed the `display_name` attribute (use `display` instead)
