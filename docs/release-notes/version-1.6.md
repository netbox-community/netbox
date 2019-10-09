# v1.6.3 (2016-10-19)

## Improvements

* [#353](https://github.com/netbox-community/netbox/issues/353) - Bulk editing of device and device type interfaces
* [#527](https://github.com/netbox-community/netbox/issues/527) - Support for nullification of fields when bulk editing
* [#592](https://github.com/netbox-community/netbox/issues/592) - Allow space-delimited lists of ALLOWED_HOSTS in Docker
* [#608](https://github.com/netbox-community/netbox/issues/608) - Added "select all" button for device and device type components

## Bug Fixes

* [#602](https://github.com/netbox-community/netbox/issues/602) - Correct display of custom integer fields with value of 0 or 1
* [#604](https://github.com/netbox-community/netbox/issues/604) - Correct display of unnamed devices in form selection fields
* [#611](https://github.com/netbox-community/netbox/issues/611) - Power/console/interface connection import: status field should be case-insensitive
* [#615](https://github.com/netbox-community/netbox/issues/615) - Account for BASE_PATH in static URLs and during login
* [#616](https://github.com/netbox-community/netbox/issues/616) - Correct display of custom URL fields

---

# v1.6.2-r1 (2016-10-04)

## Improvements

* [#212](https://github.com/netbox-community/netbox/issues/212) - Introduced the `BASE_PATH` configuration setting to allow running NetBox in a URL subdirectory
* [#345](https://github.com/netbox-community/netbox/issues/345) - Bulk edit: allow user to select all objects on page or all matching query
* [#475](https://github.com/netbox-community/netbox/issues/475) - Display "add" buttons at top and bottom of all device/device type panels
* [#480](https://github.com/netbox-community/netbox/issues/480) - Improved layout on mobile devices
* [#481](https://github.com/netbox-community/netbox/issues/481) - Require interface creation before trying to assign an IP to a device
* [#575](https://github.com/netbox-community/netbox/issues/575) - Allow all valid URL schemes in custom fields
* [#579](https://github.com/netbox-community/netbox/issues/579) - Add a description field to export templates

## Bug Fixes

* [#466](https://github.com/netbox-community/netbox/issues/466) - Validate available free space for all instances when increasing the U height of a device type
* [#571](https://github.com/netbox-community/netbox/issues/571) - Correct rack group filter on device list
* [#576](https://github.com/netbox-community/netbox/issues/576) - Delete all relevant CustomFieldValues when deleting a CustomFieldChoice
* [#581](https://github.com/netbox-community/netbox/issues/581) - Correct initialization of custom boolean and select fields
* [#591](https://github.com/netbox-community/netbox/issues/591) - Correct display of component creation buttons in device type view

---

# v1.6.1-r1 (2016-09-21)

## Improvements
* [#415](https://github.com/netbox-community/netbox/issues/415) - Add an expand/collapse toggle button to the prefix list
* [#552](https://github.com/netbox-community/netbox/issues/552) - Allow filtering on custom select fields by "none"
* [#561](https://github.com/netbox-community/netbox/issues/561) - Make custom fields accessible from within export templates

## Bug Fixes
* [#493](https://github.com/netbox-community/netbox/issues/493) - CSV import support for UTF-8
* [#531](https://github.com/netbox-community/netbox/issues/531) - Order prefix list by VRF assignment
* [#542](https://github.com/netbox-community/netbox/issues/542) - Add LDAP support in Docker
* [#557](https://github.com/netbox-community/netbox/issues/557) - Add 'global' choice to VRF filter for prefixes and IP addresses
* [#558](https://github.com/netbox-community/netbox/issues/558) - Update slug field when name is populated without a key press
* [#562](https://github.com/netbox-community/netbox/issues/562) - Fixed bulk interface creation
* [#564](https://github.com/netbox-community/netbox/issues/564) - Display custom fields for all applicable objects

---

# v1.6.0 (2016-09-13)

## New Features

### Custom Fields ([#129](https://github.com/netbox-community/netbox/issues/129))

Users can now create custom fields to associate arbitrary data with core NetBox objects. For example, you might want to add a geolocation tag to IP prefixes, or a ticket number to each device. Text, integer, boolean, date, URL, and selection fields are supported.

## Improvements

* [#489](https://github.com/netbox-community/netbox/issues/489) - Docker file now builds from a `python:2.7-wheezy` base instead of `ubuntu:14.04`
* [#540](https://github.com/netbox-community/netbox/issues/540) - Add links for VLAN roles under VLAN navigation menu
* Added new interface form factors
* Added address family filters to aggregate and prefix lists

## Bug Fixes

* [#476](https://github.com/netbox-community/netbox/issues/476) - Corrected rack import instructions
* [#484](https://github.com/netbox-community/netbox/issues/484) - Allow bulk deletion of >1K objects
* [#486](https://github.com/netbox-community/netbox/issues/486) - Prompt for secret key only if updating a secret's value
* [#490](https://github.com/netbox-community/netbox/issues/490) - Corrected display of circuit commit rate
* [#495](https://github.com/netbox-community/netbox/issues/495) - Include tenant in prefix and IP CSV export
* [#507](https://github.com/netbox-community/netbox/issues/507) - Corrected rendering of nav menu on screens narrower than 1200px
* [#515](https://github.com/netbox-community/netbox/issues/515) - Clarified instructions for the "face" field when importing devices
* [#522](https://github.com/netbox-community/netbox/issues/522) - Remove obsolete check for staff status when bulk deleting objects
* [#544](https://github.com/netbox-community/netbox/issues/544) - Strip CRLF-style line terminators from rendered export templates
