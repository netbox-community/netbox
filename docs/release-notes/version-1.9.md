# v1.9.6 (2017-04-21)

## Improvements

* [#878](https://github.com/netbox-community/netbox/issues/878) - Merged IP addresses with interfaces list on device view
* [#1001](https://github.com/netbox-community/netbox/issues/1001) - Interface assignment can be modified when editing an IP address
* [#1084](https://github.com/netbox-community/netbox/issues/1084) - Include custom fields when creating IP addresses in bulk

## Bug Fixes

* [#1057](https://github.com/netbox-community/netbox/issues/1057) - Corrected VLAN validation during prefix import
* [#1061](https://github.com/netbox-community/netbox/issues/1061) - Fixed potential for script injection via create/edit/delete messages
* [#1070](https://github.com/netbox-community/netbox/issues/1070) - Corrected installation instructions for Python3 on CentOS/RHEL
* [#1071](https://github.com/netbox-community/netbox/issues/1071) - Protect assigned circuit termination when an interface is deleted
* [#1072](https://github.com/netbox-community/netbox/issues/1072) - Order LAG interfaces naturally on bulk interface edit form
* [#1074](https://github.com/netbox-community/netbox/issues/1074) - Require ncclient 0.5.3 (Python 3 fix)
* [#1090](https://github.com/netbox-community/netbox/issues/1090) - Improved installation documentation for Python 3
* [#1092](https://github.com/netbox-community/netbox/issues/1092) - Increase randomness in SECRET_KEY generation tool

---

# v1.9.5 (2017-04-06)

## Improvements

* [#1052](https://github.com/netbox-community/netbox/issues/1052) - Added rack reservation list and bulk delete views

## Bug Fixes

* [#1038](https://github.com/netbox-community/netbox/issues/1038) - Suppress upgrading to Django 1.11 (will be supported in v2.0)
* [#1037](https://github.com/netbox-community/netbox/issues/1037) - Fixed error on VLAN import with duplicate VLAN group names
* [#1047](https://github.com/netbox-community/netbox/issues/1047) - Correct ordering of numbered subinterfaces
* [#1051](https://github.com/netbox-community/netbox/issues/1051) - Upgraded django-rest-swagger

---

# v1.9.4-r1 (2017-04-04)

## Improvements

* [#362](https://github.com/netbox-community/netbox/issues/362) - Added per_page query parameter to control pagination page length

## Bug Fixes

* [#991](https://github.com/netbox-community/netbox/issues/991) - Correct server error on "create and connect another" interface connection
* [#1022](https://github.com/netbox-community/netbox/issues/1022) - Record user actions when creating IP addresses in bulk
* [#1027](https://github.com/netbox-community/netbox/issues/1027) - Fixed nav menu highlighting when BASE_PATH is set
* [#1034](https://github.com/netbox-community/netbox/issues/1034) - Added migration missing from v1.9.4 release

---

# v1.9.3 (2017-03-23)

## Improvements

* [#972](https://github.com/netbox-community/netbox/issues/972) - Add ability to filter connections list by device name
* [#974](https://github.com/netbox-community/netbox/issues/974) - Added MAC address filter to API interfaces list
* [#978](https://github.com/netbox-community/netbox/issues/978) - Allow filtering device types by function and subdevice role
* [#981](https://github.com/netbox-community/netbox/issues/981) - Allow filtering primary objects by a given set of IDs
* [#983](https://github.com/netbox-community/netbox/issues/983) - Include peer device names when listing circuits in device view

## Bug Fixes

* [#967](https://github.com/netbox-community/netbox/issues/967) - Fix error when assigning a new interface to a LAG

---

# v1.9.2 (2017-03-14)

## Bug Fixes

* [#950](https://github.com/netbox-community/netbox/issues/950) - Fix site_id error on child device import
* [#956](https://github.com/netbox-community/netbox/issues/956) - Correct bug affecting unnamed rackless devices
* [#957](https://github.com/netbox-community/netbox/issues/957) - Correct device site filter count to include unracked devices
* [#963](https://github.com/netbox-community/netbox/issues/963) - Fix bug in IPv6 address range expansion
* [#964](https://github.com/netbox-community/netbox/issues/964) - Fix bug when bulk editing/deleting filtered set of objects

---

# v1.9.1 (2017-03-08)

## Improvements

* [#945](https://github.com/netbox-community/netbox/issues/945) - Display the current user in the navigation menu
* [#946](https://github.com/netbox-community/netbox/issues/946) - Disregard mask length when filtering IP addresses by a parent prefix

## Bug Fixes

* [#941](https://github.com/netbox-community/netbox/issues/941) - Corrected old references to rack.site on Device
* [#943](https://github.com/netbox-community/netbox/issues/943) - Child prefixes missing on Python 3
* [#944](https://github.com/netbox-community/netbox/issues/944) - Corrected console and power connection form behavior
* [#948](https://github.com/netbox-community/netbox/issues/948) - Region name should be hyperlinked to site list

---

# v1.9.0-r1 (2017-03-03)

## New Features

### Rack Reservations ([#36](https://github.com/netbox-community/netbox/issues/36))

Users can now reserve an arbitrary number of units within a rack, adding a comment noting their intentions. Reservations do not interfere with installed devices: It is possible to reserve a unit for future use even if it is currently occupied by a device.

### Interface Groups ([#105](https://github.com/netbox-community/netbox/issues/105))

A new Link Aggregation Group (LAG) virtual form factor has been added. Physical interfaces can be assigned to a parent LAG interface to represent a port-channel or similar logical bundling of links.

### Regions ([#164](https://github.com/netbox-community/netbox/issues/164))

A new region model has been introduced to allow for the geographic organization of sites. Regions can be nested recursively to form a hierarchy.

### Rackless Devices ([#198](https://github.com/netbox-community/netbox/issues/198))

Previous releases required each device to be assigned to a particular rack within a site. This requirement has been relaxed so that devices must only be assigned to a site, and may optionally be assigned to a rack.

### Global VLANs ([#235](https://github.com/netbox-community/netbox/issues/235))

Assignment of VLANs and VLAN groups to sites is now optional, allowing for the representation of a VLAN spanning multiple sites.

## Improvements

* [#862](https://github.com/netbox-community/netbox/issues/862) - Show both IPv6 and IPv4 primary IPs in device list
* [#894](https://github.com/netbox-community/netbox/issues/894) - Expand device name max length to 64 characters
* [#898](https://github.com/netbox-community/netbox/issues/898) - Expanded circuits list in provider view rack face
* [#901](https://github.com/netbox-community/netbox/issues/901) - Support for filtering prefixes and IP addresses by mask length

## Bug Fixes

* [#872](https://github.com/netbox-community/netbox/issues/872) - Fixed TypeError on bulk IP address creation (Python 3)
* [#884](https://github.com/netbox-community/netbox/issues/884) - Preserve selected rack unit when changing a device's rack face
* [#892](https://github.com/netbox-community/netbox/issues/892) - Restored missing edit/delete buttons when viewing child prefixes and IP addresses from a parent object
* [#897](https://github.com/netbox-community/netbox/issues/897) - Fixed power connections CSV export
* [#903](https://github.com/netbox-community/netbox/issues/903) - Only alert on missing critical connections if present in the parent device type
* [#935](https://github.com/netbox-community/netbox/issues/935) - Fix form validation error when connecting an interface using live search
* [#937](https://github.com/netbox-community/netbox/issues/937) - Region assignment should be optional when creating a site
* [#938](https://github.com/netbox-community/netbox/issues/938) - Provider view yields an error if one or more circuits is assigned to a tenant
