# v1.5.2 (2016-08-16)

## Bug Fixes

* [#460](https://github.com/netbox-community/netbox/issues/460) - Corrected ordering of IP addresses with differing prefix lengths
* [#463](https://github.com/netbox-community/netbox/issues/463) - Prevent pre-population of livesearch field with '---------'
* [#467](https://github.com/netbox-community/netbox/issues/467) - Include prefixes and IPs which inherit tenancy from their VRF in tenant stats
* [#468](https://github.com/netbox-community/netbox/issues/468) - Don't allow connected interfaces to be changed to the "virtual" form factor
* [#469](https://github.com/netbox-community/netbox/issues/469) - Added missing import buttons to list views
* [#472](https://github.com/netbox-community/netbox/issues/472) - Hide the connection button for interfaces which have a circuit terminated to them

---

# v1.5.1 (2016-08-11)

## Improvements

* [#421](https://github.com/netbox-community/netbox/issues/421) - Added an asset tag field to devices
* [#456](https://github.com/netbox-community/netbox/issues/456) - Added IP search box to home page
* Colorized rack and device roles

## Bug Fixes

* [#454](https://github.com/netbox-community/netbox/issues/454) - Corrected error on rack export
* [#457](https://github.com/netbox-community/netbox/issues/457) - Added role field to rack edit form

---

# v1.5.0 (2016-08-10)

## New Features

### Rack Enhancements ([#180](https://github.com/netbox-community/netbox/issues/180), [#241](https://github.com/netbox-community/netbox/issues/241))

Like devices, racks can now be assigned to functional roles. This allows users to group racks by designated function as well as by physical location (rack groups). Additionally, rack can now have a defined rail-to-rail width (19 or 23 inches) and a type (two-post-rack, cabinet, etc.).

## Improvements

* [#149](https://github.com/netbox-community/netbox/issues/149) - Added discrete upstream speed field for circuits
* [#157](https://github.com/netbox-community/netbox/issues/157) - Added manufacturer field for device modules
* We have a logo!
* Upgraded to Django 1.10

## Bug Fixes

* [#433](https://github.com/netbox-community/netbox/issues/433) - Corrected form validation when editing child devices
* [#442](https://github.com/netbox-community/netbox/issues/442) - Corrected child device import instructions
* [#443](https://github.com/netbox-community/netbox/issues/443) - Correctly display and initialize VRF for creation of new IP addresses
* [#444](https://github.com/netbox-community/netbox/issues/444) - Corrected prefix model validation
* [#445](https://github.com/netbox-community/netbox/issues/445) - Limit rack height to between 1U and 100U (inclusive)
