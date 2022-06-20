# NetBox v3.3

## v3.3.0 (FUTURE)

### Breaking Changes

* Device position and rack unit values are now reported as decimals (e.g. `1.0` or `1.5`) to support modeling half-height rack units.
* The `nat_outside` relation on the IP address model now returns a list of zero or more related IP addresses, rather than a single instance (or None).

### New Features

#### Half-Height Rack Units ([#51](https://github.com/netbox-community/netbox/issues/51))

### Enhancements

* [#1202](https://github.com/netbox-community/netbox/issues/1202) - Support overlapping assignment of NAT IP addresses
* [#5303](https://github.com/netbox-community/netbox/issues/5303) - A virtual machine may be assigned to a site and/or cluster
* [#8222](https://github.com/netbox-community/netbox/issues/8222) - Enable the assignment of a VM to a specific host device within a cluster
* [#8471](https://github.com/netbox-community/netbox/issues/8471) - Add `status` field to Cluster
* [#8495](https://github.com/netbox-community/netbox/issues/8495) - Enable custom field grouping
* [#8995](https://github.com/netbox-community/netbox/issues/8995) - Enable arbitrary ordering of REST API results
* [#9166](https://github.com/netbox-community/netbox/issues/9166) - Add UI visibility toggle for custom fields

### Other Changes

* [#9261](https://github.com/netbox-community/netbox/issues/9261) - `NetBoxTable` no longer automatically clears pre-existing calls to `prefetch_related()` on its queryset
* [#9434](https://github.com/netbox-community/netbox/issues/9434) - Enabled `django-rich` test runner for more user-friendly output

### REST API Changes

* dcim.Device
    * The `position` field has been changed from an integer to a decimal
* dcim.DeviceType
    * The `u_height` field has been changed from an integer to a decimal
* dcim.Rack
    * The `elevation` endpoint now includes half-height rack units, and utilizes decimal values for the ID and name of each unit
* extras.CustomField
    * Added `group_name` and `ui_visibility` fields
* ipam.IPAddress
    * The `nat_inside` field no longer requires a unique value
    * The `nat_outside` field has changed from a single IP address instance to a list of multiple IP addresses
* virtualization.Cluster
    * Added required `status` field (default value: `active`)
* virtualization.VirtualMachine
    * Added `device` field
    * The `site` field is now directly writable (rather than being inferred from the assigned cluster)
    * The `cluster` field is now optional. A virtual machine must have a site and/or cluster assigned.
