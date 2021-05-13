# NetBox v2.12

## v2.12-beta1 (FUTURE)

### Enhancements

* [#3665](https://github.com/netbox-community/netbox/issues/3665) - Enable rendering export templates via REST API
* [#4609](https://github.com/netbox-community/netbox/issues/4609) - Allow marking prefixes as fully utilized
* [#5806](https://github.com/netbox-community/netbox/issues/5806) - Add kilometer and mile as choices for cable length unit
* [#6154](https://github.com/netbox-community/netbox/issues/6154) - Allow decimal values for cable lengths

### Other Changes

* [#5532](https://github.com/netbox-community/netbox/issues/5532) - Drop support for Python 3.6
* [#5994](https://github.com/netbox-community/netbox/issues/5994) - Drop support for `display_field` argument on ObjectVar
* [#6338](https://github.com/netbox-community/netbox/issues/6338) - Decimal fields are no longer coerced to strings in REST API

### REST API Changes

* dcim.Cable
    * `length` is now a decimal value
* dcim.Device
    * Removed the `display_name` attribute (use `display` instead)
* dcim.DeviceType
    * Removed the `display_name` attribute (use `display` instead)
* dcim.Rack
    * Removed the `display_name` attribute (use `display` instead)
* dcim.Site
    * `latitude` and `longitude` are now decimal fields rather than strings
* extras.ContentType
    * Removed the `display_name` attribute (use `display` instead)
* ipam.Prefix
    * Added the `mark_utilized` boolean field
* ipam.VLAN
    * Removed the `display_name` attribute (use `display` instead)
* ipam.VRF
    * Removed the `display_name` attribute (use `display` instead)
* virtualization.VirtualMachine
    * `vcpus` is now a decimal field rather than a string
