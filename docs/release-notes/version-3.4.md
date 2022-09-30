# NetBox v3.4

!!! warning "PostgreSQL 11 Required"
    NetBox v3.4 requires PostgreSQL 11 or later.

### Breaking Changes

* Device and virtual machine names are no longer case-sensitive. Attempting to create e.g. "device1" and "DEVICE1" will raise a validation error.
* The `asn` field has been removed from the provider model. Please replicate any provider ASN assignments to the ASN model introduced in NetBox v3.1 prior to upgrading.
* The `noc_contact`, `admin_contact`, and `portal_url` fields have been removed from the provider model. Please replicate any data remaining in these fields to the contact model introduced in NetBox v3.1 prior to upgrading.

### New Features

#### Top-Level Plugin Navigation Menus ([#9071](https://github.com/netbox-community/netbox/issues/9071))

A new `PluginMenu` class has been introduced, which enables a plugin to inject a top-level menu in NetBox's navigation menu. This menu can have one or more groups of menu items, just like core items. Backward compatibility with the existing `menu_items` has been maintained.

### Enhancements

* [#9249](https://github.com/netbox-community/netbox/issues/9249) - Device and virtual machine names are no longer case-sensitive
* [#9654](https://github.com/netbox-community/netbox/issues/9654) - Add `weight` field to racks, device types, and module types
* [#9892](https://github.com/netbox-community/netbox/issues/9892) - Add optional `name` field for FHRP groups
* [#10348](https://github.com/netbox-community/netbox/issues/10348) - Add decimal custom field type

### Plugins API

* [#9071](https://github.com/netbox-community/netbox/issues/9071) - Introduce `PluginMenu` for top-level plugin navigation menus
* [#9880](https://github.com/netbox-community/netbox/issues/9880) - Introduce `django_apps` plugin configuration parameter
* [#10314](https://github.com/netbox-community/netbox/issues/10314) - Move `clone()` method from NetBoxModel to CloningMixin

### Other Changes

* [#9045](https://github.com/netbox-community/netbox/issues/9045) - Remove legacy ASN field from provider model
* [#9046](https://github.com/netbox-community/netbox/issues/9046) - Remove legacy contact fields from provider model
* [#10358](https://github.com/netbox-community/netbox/issues/10358) - Raise minimum required PostgreSQL version from 10 to 11

### REST API Changes

* circuits.provider
    * Removed the `asn`, `noc_contact`, `admin_contact`, and `portal_url` fields
* dcim.DeviceType
    * Added optional `weight` and `weight_unit` fields
* dcim.ModuleType
    * Added optional `weight` and `weight_unit` fields
* dcim.Rack
    * Added optional `weight` and `weight_unit` fields
* ipam.FHRPGroup
    * Added optional `name` field
