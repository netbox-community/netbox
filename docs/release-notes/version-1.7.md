# v1.7.3 (2016-12-08)

## Bug Fixes

* [#724](https://github.com/netbox-community/netbox/issues/724) - Exempt API views from LoginRequiredMiddleware to enable basic HTTP authentication when LOGIN_REQUIRED is true
* [#729](https://github.com/netbox-community/netbox/issues/729) - Corrected cancellation links when editing secondary objects
* [#732](https://github.com/netbox-community/netbox/issues/732) - Allow custom select field values to be deselected if the field is not required
* [#733](https://github.com/netbox-community/netbox/issues/733) - Fixed MAC address filter on device list
* [#734](https://github.com/netbox-community/netbox/issues/734) - Corrected display of device type when editing a device

---

# v1.7.2-r1 (2016-12-06)

## Improvements

* [#663](https://github.com/netbox-community/netbox/issues/663) - Added MAC address search field to device list
* [#672](https://github.com/netbox-community/netbox/issues/672) - Increased the selection of available colors for rack and device roles
* [#695](https://github.com/netbox-community/netbox/issues/695) - Added is_private field to RIR

## Bug Fixes

* [#677](https://github.com/netbox-community/netbox/issues/677) - Fix setuptools installation error on Debian 8.6
* [#696](https://github.com/netbox-community/netbox/issues/696) - Corrected link to VRF in prefix and IP address breadcrumbs
* [#702](https://github.com/netbox-community/netbox/issues/702) - Improved Unicode support for custom fields
* [#712](https://github.com/netbox-community/netbox/issues/712) - Corrected export of tenants which are not assigned to a group
* [#713](https://github.com/netbox-community/netbox/issues/713) - Include a label for the comments field when editing circuits, providers, or racks in bulk
* [#718](https://github.com/netbox-community/netbox/issues/718) - Restore is_primary field on IP assignment form
* [#723](https://github.com/netbox-community/netbox/issues/723) - API documentation is now accessible when using BASE_PATH
* [#727](https://github.com/netbox-community/netbox/issues/727) - Corrected error in rack elevation display (v1.7.2)

---

# v1.7.1 (2016-11-15)

## Improvements

* [#667](https://github.com/netbox-community/netbox/issues/667) - Added prefix utilization statistics to the RIR list view
* [#685](https://github.com/netbox-community/netbox/issues/685) - When assigning an IP to a device, automatically select the interface if only one exists

## Bug Fixes

* [#674](https://github.com/netbox-community/netbox/issues/674) - Fix assignment of status to imported IP addresses
* [#676](https://github.com/netbox-community/netbox/issues/676) - Server error when bulk editing device types
* [#678](https://github.com/netbox-community/netbox/issues/678) - Server error on device import specifying an invalid device type
* [#691](https://github.com/netbox-community/netbox/issues/691) - Allow the assignment of power ports to PDUs
* [#692](https://github.com/netbox-community/netbox/issues/692) - Form errors are not displayed on checkbox fields

---

# v1.7.0 (2016-11-03)

## New Features

### IP address statuses ([#87](https://github.com/netbox-community/netbox/issues/87))

An IP address can now be designated as active, reserved, or DHCP. The DHCP status implies that the IP address is part of a DHCP pool and may or may not be assigned to a DHCP client.

### Top-to-bottom rack numbering ([#191](https://github.com/netbox-community/netbox/issues/191))

Racks can now be set to have descending rack units, with U1 at the top of the rack. When adding a device to a rack with descending units, be sure to position it in the **lowest-numbered** unit which it occupies (this will be physically the topmost unit).

## Improvements
* [#211](https://github.com/netbox-community/netbox/issues/211) - Allow device assignment and removal from IP address view
* [#630](https://github.com/netbox-community/netbox/issues/630) - Added a custom 404 page
* [#652](https://github.com/netbox-community/netbox/issues/652) - Use password input controls when editing secrets
* [#654](https://github.com/netbox-community/netbox/issues/654) - Added Cisco FlexStack and FlexStack Plus form factors
* [#661](https://github.com/netbox-community/netbox/issues/661) - Display relevant IP addressing when viewing a circuit

## Bug Fixes
* [#632](https://github.com/netbox-community/netbox/issues/632) - Use semicolons instead of commas to separate regexes in topology maps
* [#647](https://github.com/netbox-community/netbox/issues/647) - Extend form used when assigning an IP to a device
* [#657](https://github.com/netbox-community/netbox/issues/657) - Unicode error when adding device modules
* [#660](https://github.com/netbox-community/netbox/issues/660) - Corrected calculation of utilized space in rack list
* [#664](https://github.com/netbox-community/netbox/issues/664) - Fixed bulk creation of interfaces across multiple devices
