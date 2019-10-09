# v1.0.7-r1 (2016-07-05)

* [#199](https://github.com/netbox-community/netbox/issues/199) - Correct IP address validation

---

# v1.0.7 (2016-06-30)

**Note:** If upgrading from a previous release, be sure to run ./upgrade.sh after downloading the new code.
* [#135](https://github.com/netbox-community/netbox/issues/135) - Fixed display of navigation menu on mobile screens
* [#141](https://github.com/netbox-community/netbox/issues/141) - Fixed rendering of "getting started" guide
* Modified upgrade.sh to use sudo for pip installations
* [#109](https://github.com/netbox-community/netbox/issues/109) - Hide the navigation menu from anonymous users if login is required
* [#143](https://github.com/netbox-community/netbox/issues/143) - Add help_text to Device.position
* [#136](https://github.com/netbox-community/netbox/issues/136) - Prefixes which have host bits set will trigger an error instead of being silently corrected
* [#140](https://github.com/netbox-community/netbox/issues/140) - Improved support for Unicode in object names

---

# v1.0.0 (2016-06-27)

NetBox was originally developed internally at DigitalOcean by the network development team. This release marks the debut of NetBox as an open source project.
