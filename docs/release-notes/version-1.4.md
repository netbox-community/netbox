# v1.4.2 (2016-08-06)

## Improvements

* [#167](https://github.com/netbox-community/netbox/issues/167) - Added new interface form factors
* [#253](https://github.com/netbox-community/netbox/issues/253) - Added new interface form factors
* [#434](https://github.com/netbox-community/netbox/issues/434) - Restored admin UI access to user action history (however bulk deletion is disabled)
* [#435](https://github.com/netbox-community/netbox/issues/435) - Added an "add prefix" button to the VLAN view

## Bug Fixes

* [#425](https://github.com/netbox-community/netbox/issues/425) - Ignore leading and trailing periods when generating a slug
* [#427](https://github.com/netbox-community/netbox/issues/427) - Prevent error when duplicate IPs are present in a prefix's IP list
* [#429](https://github.com/netbox-community/netbox/issues/429) - Correct redirection of user when adding a secret to a device

---

# v1.4.1 (2016-08-03)

## Improvements

* [#289](https://github.com/netbox-community/netbox/issues/289) - Annotate available ranges in prefix IP list
* [#412](https://github.com/netbox-community/netbox/issues/412) - Tenant group assignment is no longer mandatory
* [#422](https://github.com/netbox-community/netbox/issues/422) - CSV import now supports double-quoting values which contain commas

## Bug Fixes

* [#395](https://github.com/netbox-community/netbox/issues/395) - Show child prefixes from all VRFs if the parent belongs to the global table
* [#406](https://github.com/netbox-community/netbox/issues/406) - Fixed circuit list rendring when filtering on port speed or commit rate
* [#409](https://github.com/netbox-community/netbox/issues/409) - Filter IPs and prefixes by tenant slug rather than by its PK
* [#411](https://github.com/netbox-community/netbox/issues/411) - Corrected title of secret roles view
* [#419](https://github.com/netbox-community/netbox/issues/419) - Fixed a potential database performance issue when gathering tenant statistics

---

# v1.4.0 (2016-08-01)

## New Features

### Multitenancy ([#16](https://github.com/netbox-community/netbox/issues/16))

NetBox now supports tenants and tenant groups. Sites, racks, devices, VRFs, prefixes, IP addresses, VLANs, and circuits can be assigned to tenants to track the allocation of these resources among customers or internal departments. If a prefix or IP address does not have a tenant assigned, it will fall back to the tenant assigned to its parent VRF (where applicable).

## Improvements

* [#176](https://github.com/netbox-community/netbox/issues/176) - Introduced seed data for new installs
* [#358](https://github.com/netbox-community/netbox/issues/358) - Improved search for all objects
* [#394](https://github.com/netbox-community/netbox/issues/394) - Improved VRF selection during bulk editing of prefixes and IP addresses
* Miscellaneous cosmetic improvements to the UI

## Bug Fixes

* [#392](https://github.com/netbox-community/netbox/issues/392) - Don't include child devices in non-racked devices table
* [#397](https://github.com/netbox-community/netbox/issues/397) - Only include child IPs which belong to the same VRF as the parent prefix
