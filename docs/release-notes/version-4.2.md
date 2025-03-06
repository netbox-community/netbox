# NetBox v4.2

## v4.2-beta1 (2024-12-02)

!!! danger "Not for Production Use"
    This is a beta release of NetBox intended for testing and evaluation. **Do not use this software in production.** Also be aware that no upgrade path is provided to future releases.

### Breaking Changes

* Support for the Django admin UI has been completely removed. (The Django admin UI was disabled by default in NetBox v4.0.)
* NetBox has adopted collation-based natural ordering for many models. This may alter the order in which some objects are listed by default.
* Automatic redirects from pre-v4.1 UI views for virtual disks have been removed.
* The `site` and `provider_network` foreign key fields on `circuits.CircuitTermination` have been replaced by the `termination` generic foreign key.
* The `site` foreign key field on `ipam.Prefix` has been replaced by the `scope` generic foreign key.
* The `site` foreign key field on `virtualization.Cluster` has been replaced by the `scope` generic foreign key.
* The `circuit` foreign key field on `circuits.CircuitGroupAssignment` has been replaced by the `member` generic foreign key.
* Obsolete nested REST API serializers have been removed. These were deprecated in NetBox v4.1 under [#17143](https://github.com/netbox-community/netbox/issues/17143).

### New Features

#### Assign Multiple MAC Addresses per Interface ([#4867](https://github.com/netbox-community/netbox/issues/4867))

MAC addresses are now managed as independent objects, rather than attributes on device and VM interfaces. NetBox now supports the assignment of multiple MAC addresses per interface, and allows a primary MAC address to be designated for each.

#### Quick Add UI Widget ([#5858](https://github.com/netbox-community/netbox/issues/5858))

A new UI widget has been introduced to enable conveniently creating new related objects while creating or editing an object. For instance, it is now possible to create and assign a new device role when creating or editing a device from within the device form.

#### VLAN Translation ([#7336](https://github.com/netbox-community/netbox/issues/7336))

User can now define policies which track the translation of VLAN IDs on IEEE 802.1Q-encapsulated interfaces. Translation policies can be reused across multiple interfaces.

#### Virtual Circuits ([#13086](https://github.com/netbox-community/netbox/issues/13086))

New models have been introduced to support the documentation of virtual circuits as an extension to the physical circuit modeling already supported. This enables users to accurately reflect point-to-point or multipoint virtual circuits atop infrastructure comprising physical circuits and cables.

#### Q-in-Q Encapsulation ([#13428](https://github.com/netbox-community/netbox/issues/13428))

NetBox now supports the designation of customer VLANs (CVLANs) and service VLANs (SVLANs) to support IEEE 802.1ad/Q-in-Q encapsulation. Each interface can now have it mode designated "Q-in-Q" and be assigned an SVLAN.

### Enhancements

* [#6414](https://github.com/netbox-community/netbox/issues/6414) - Prefixes can now be scoped by region, site group, site, or location
* [#7699](https://github.com/netbox-community/netbox/issues/7699) - Virtualization clusters can now be scoped by region, site group, site, or location
* [#9604](https://github.com/netbox-community/netbox/issues/9604) - The scope of a circuit termination now include a region, site group, site, location, or provider network
* [#10711](https://github.com/netbox-community/netbox/issues/10711) - Wireless LANs can now be scoped by region, site group, site, or location
* [#11279](https://github.com/netbox-community/netbox/issues/11279) - Improved the use of natural ordering for various models throughout the application
* [#12596](https://github.com/netbox-community/netbox/issues/12596) - Extended the virtualization clusters REST API endpoint to report on allocated VM resources
* [#16547](https://github.com/netbox-community/netbox/issues/16547) - Add a geographic distance field for circuits
* [#16783](https://github.com/netbox-community/netbox/issues/16783) - Add an operational status field for inventory items
* [#17195](https://github.com/netbox-community/netbox/issues/17195) - Add a color field for power outlets

### Plugins

* [#15093](https://github.com/netbox-community/netbox/issues/15093) - Introduced the `events_pipeline` configuration parameter, which allows plugins to hook into NetBox event processing
* [#16546](https://github.com/netbox-community/netbox/issues/16546) - NetBoxModel now provides a default `get_absolute_url()` method
* [#16971](https://github.com/netbox-community/netbox/issues/16971) - Plugins can now easily register system jobs to perform background tasks
* [#17029](https://github.com/netbox-community/netbox/issues/17029) - Registering a `PluginTemplateExtension` subclass for a single model has been deprecated (replace `model` with `models`)
* [#18023](https://github.com/netbox-community/netbox/issues/18023) - Extend `register_model_view()` to handle list views

### Other Changes

* [#16136](https://github.com/netbox-community/netbox/issues/16136) - Removed support for the Django admin UI
* [#17165](https://github.com/netbox-community/netbox/issues/17165) - All obsolete nested REST API serializers have been removed
* [#17472](https://github.com/netbox-community/netbox/issues/17472) - The legacy staged changes API has been deprecated, and will be removed in Netbox v4.3
* [#17476](https://github.com/netbox-community/netbox/issues/17476) - Upgrade to Django 5.1
* [#17752](https://github.com/netbox-community/netbox/issues/17752) - Bulk object import URL paths have been renamed from `*_import` to `*_bulk_import`
* [#17761](https://github.com/netbox-community/netbox/issues/17761) - Optional choice fields now store empty values as null (rather than empty strings) in the database
* [#18093](https://github.com/netbox-community/netbox/issues/18093) - Redirects for pre-v4.1 virtual disk UI views have been removed

### REST API Changes

* Added the following endpoints:
    * `/api/circuits/virtual-circuits/`
    * `/api/circuits/virtual-circuit-terminations/`
    * `/api/dcim/mac-addresses/`
    * `/api/ipam/vlan-translation-policies/`
    * `/api/ipam/vlan-translation-rules/`
* circuits.Circuit
    * Added the optional `distance` and `distance_unit` fields
* circuits.CircuitGroupAssignment
    * Replaced the `circuit` field with `member_type` and `member_id` to support virtual circuit assignment
* circuits.CircuitTermination
    * Removed the `site` & `provider_network` fields
    * Added the `termination_type` & `termination_id` fields to facilitate termination assignment
    * Added the read-only `termination` field
* dcim.Interface
    * The `mac_address` field is now read-only
    * Added the `primary_mac_address` relation to dcim.MACAddress
    * Added the read-only `mac_addresses` list
    * Added the `qinq_svlan` relation to ipam.VLAN
    * Added the `vlan_translation_policy` relation to ipam.VLANTranslationPolicy
    * Added `mode` choice "Q-in-Q"
* dcim.InventoryItem
    * Added the optional `status` choice field
* dcim.Location
    * Added the read-only `prefix_count` field
* dcim.PowerOutlet
    * Added the optional `color` field
* dcim.Region
    * Added the read-only `prefix_count` field
* dcim.SiteGroup
    * Added the read-only `prefix_count` field
* ipam.Prefix
    * Removed the `site` field
    * Added the `scope_type` & `scope_id` fields to facilitate scope assignment
    * Added the read-only `scope` field
* ipam.VLAN
    * Added the optional `qinq_role` selection field
    * Added the `qinq_svlan` recursive relation
* virtualization.Cluster
    * Removed the `site` field
    * Added the `scope_type` & `scope_id` fields to facilitate scope assignment
    * Added the read-only `scope` field
* virtualization.Cluster
    * Added the read-only fields `allocated_vcpus`, `allocated_memory`, and `allocated_disk`
* virtualization.VMInterface
    * The `mac_address` field is now read-only
    * Added the `primary_mac_address` relation to dcim.MACAddress
    * Added the read-only `mac_addresses` list
    * Added the `qinq_svlan` relation to ipam.VLAN
    * Added the `vlan_translation_policy` relation to ipam.VLANTranslationPolicy
    * Added `mode` choice "Q-in-Q"
* wireless.WirelessLAN
    * Added the `scope_type` & `scope_id` fields to support scope assignment
    * Added the read-only `scope` field
