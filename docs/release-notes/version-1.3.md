# v1.3.2 (2016-07-26)

## Improvements

* [#292](https://github.com/netbox-community/netbox/issues/292) - Added part_number field to DeviceType
* [#363](https://github.com/netbox-community/netbox/issues/363) - Added a description field to the VLAN model
* [#374](https://github.com/netbox-community/netbox/issues/374) - Increased VLAN name length to 64 characters
* Enabled bulk deletion of interfaces from devices

## Bug Fixes

* [#359](https://github.com/netbox-community/netbox/issues/359) - Corrected the DCIM API endpoint for finding related connections
* [#370](https://github.com/netbox-community/netbox/issues/370) - Notify user when secret decryption fails
* [#381](https://github.com/netbox-community/netbox/issues/381) - Fix 'u_consumed' error on rack import
* [#384](https://github.com/netbox-community/netbox/issues/384) - Fixed description field's maximum length on IPAM bulk edit forms
* [#385](https://github.com/netbox-community/netbox/issues/385) - Fixed error when deleting a user with one or more associated UserActions

---

# v1.3.1 (2016-07-21)

## Improvements

* [#258](https://github.com/netbox-community/netbox/issues/258) - Add an API endpoint to list interface connections
* [#303](https://github.com/netbox-community/netbox/issues/303) - Improved numeric ordering of sites, racks, and devices
* [#304](https://github.com/netbox-community/netbox/issues/304) - Display utilization percentage on rack list
* [#327](https://github.com/netbox-community/netbox/issues/327) - Disable rack assignment for installed child devices

## Bug Fixes

* [#331](https://github.com/netbox-community/netbox/issues/331) - Add group field to VLAN bulk edit form
* Miscellaneous improvements to Unicode handling

---

# v1.3.0 (2016-07-18)

## New Features

* [#42](https://github.com/netbox-community/netbox/issues/42) - Allow assignment of VLAN on prefix import
* [#43](https://github.com/netbox-community/netbox/issues/43) - Toggling of IP space uniqueness within a VRF
* [#111](https://github.com/netbox-community/netbox/issues/111) - Introduces VLAN groups
* [#227](https://github.com/netbox-community/netbox/issues/227) - Support for bulk import of child devices

## Bug Fixes

* [#301](https://github.com/netbox-community/netbox/issues/301) - Prevent deletion of DeviceBay when installed device is deleted
* [#306](https://github.com/netbox-community/netbox/issues/306) - Fixed device import to allow an unspecified rack face
* [#307](https://github.com/netbox-community/netbox/issues/307) - Catch `RelatedObjectDoesNotExist` when an invalid device type is defined during device import
* [#308](https://github.com/netbox-community/netbox/issues/308) - Update rack assignment for all child devices when moving a parent device
* [#311](https://github.com/netbox-community/netbox/issues/311) - Fix assignment of primary_ip on IP address import
* [#317](https://github.com/netbox-community/netbox/issues/317) - Rack elevation display fix for device types greater than 42U in height
* [#320](https://github.com/netbox-community/netbox/issues/320) - Disallow import of prefixes with host masks
* [#322](https://github.com/netbox-community/netbox/issues/320) - Corrected VLAN import behavior
