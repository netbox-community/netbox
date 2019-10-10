# v1.2.2 (2016-07-14)

## Improvements

* [#174](https://github.com/netbox-community/netbox/issues/174) - Added search and site filter to provider list
* [#270](https://github.com/netbox-community/netbox/issues/270) - Added the ability to filter devices by rack group

## Bug Fixes

* [#115](https://github.com/netbox-community/netbox/issues/115) - Fix deprecated django.core.context_processors reference
* [#268](https://github.com/netbox-community/netbox/issues/268) - Added support for entire 32-bit ASN space
* [#282](https://github.com/netbox-community/netbox/issues/282) - De-select "all" checkbox if one or more objects are deselected
* [#290](https://github.com/netbox-community/netbox/issues/290) - Always display management interfaces for a device type (even if `is_network_device` is not set)

---

# v1.2.1 (2016-07-13)

**Note:** This release introduces a new dependency ([natsort](https://pypi.python.org/pypi/natsort)). Be sure to run `upgrade.sh` if upgrading from a previous release.

## Improvements

* [#285](https://github.com/netbox-community/netbox/issues/285) - Added the ability to prefer IPv4 over IPv6 for primary device IPs

## Bug Fixes

* [#243](https://github.com/netbox-community/netbox/issues/243) - Improved ordering of device object lists
* [#271](https://github.com/netbox-community/netbox/issues/271) - Fixed primary_ip bug in secrets API
* [#274](https://github.com/netbox-community/netbox/issues/274) - Fixed primary_ip bug in DCIM admin UI
* [#275](https://github.com/netbox-community/netbox/issues/275) - Fixed bug preventing the expansion of an existing aggregate

---

# v1.2.0 (2016-07-12)

## New Features

* [#73](https://github.com/netbox-community/netbox/issues/73) - Added optional persistent banner
* [#93](https://github.com/netbox-community/netbox/issues/73) - Ability to set both IPv4 and IPv6 primary IPs for devices
* [#203](https://github.com/netbox-community/netbox/issues/203) - Introduced support for LDAP

## Bug Fixes

* [#162](https://github.com/netbox-community/netbox/issues/228) - Fixed support for Unicode characters in rack/device/VLAN names
* [#228](https://github.com/netbox-community/netbox/issues/228) - Corrected conditional inclusion of device bay templates
* [#246](https://github.com/netbox-community/netbox/issues/246) - Corrected Docker build instructions
* [#260](https://github.com/netbox-community/netbox/issues/260) - Fixed error on admin UI device type list
* Miscellaneous layout improvements for mobile devices
