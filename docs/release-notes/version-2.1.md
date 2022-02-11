# NetBox v2.1 Release Notes

## v2.1.6 (2017-10-11)

### Enhancements

* [#1548](https://github.com/netbox-community/netbox/issues/1548) - Automatically populate tenant assignment when adding an IP address from the prefix view
* [#1561](https://github.com/netbox-community/netbox/issues/1561) - Added primary IP to the devices table in global search
* [#1563](https://github.com/netbox-community/netbox/issues/1563) - Made necessary updates for Django REST Framework v3.7.0

---

## v2.1.5 (2017-09-25)

### Enhancements

* [#1484](https://github.com/netbox-community/netbox/issues/1484) - Added individual "add VLAN" buttons on the VLAN groups list
* [#1485](https://github.com/netbox-community/netbox/issues/1485) - Added `BANNER_LOGIN` configuration setting to display a banner on the login page
* [#1499](https://github.com/netbox-community/netbox/issues/1499) - Added utilization graph to child prefixes table
* [#1523](https://github.com/netbox-community/netbox/issues/1523) - Improved the natural ordering of interfaces (thanks to [@tarkatronic](https://github.com/tarkatronic))
* [#1536](https://github.com/netbox-community/netbox/issues/1536) - Improved formatting of aggregate prefix statistics

### Bug Fixes

* [#1469](https://github.com/netbox-community/netbox/issues/1469) - Allow a NAT IP to be assigned as the primary IP for a device
* [#1472](https://github.com/netbox-community/netbox/issues/1472) - Prevented truncation when displaying secret strings containing HTML characters
* [#1486](https://github.com/netbox-community/netbox/issues/1486) - Ignore subinterface IDs when validating LLDP neighbor connections
* [#1489](https://github.com/netbox-community/netbox/issues/1489) - Corrected server error on validation of empty required custom field
* [#1507](https://github.com/netbox-community/netbox/issues/1507) - Fixed error when creating the next available IP from a prefix within a VRF
* [#1520](https://github.com/netbox-community/netbox/issues/1520) - Redirect on GET request to bulk edit/delete views
* [#1522](https://github.com/netbox-community/netbox/issues/1522) - Removed object create/edit forms from the browsable API

---

## v2.1.4 (2017-08-30)

### Enhancements

* [#1326](https://github.com/netbox-community/netbox/issues/1326) - Added dropdown widget with common values for circuit speed fields
* [#1341](https://github.com/netbox-community/netbox/issues/1341) - Added a `MEDIA_ROOT` configuration setting to specify where uploaded files are stored on disk
* [#1376](https://github.com/netbox-community/netbox/issues/1376) - Ignore anycast addresses when detecting duplicate IPs
* [#1402](https://github.com/netbox-community/netbox/issues/1402) - Increased max length of name field for device components
* [#1431](https://github.com/netbox-community/netbox/issues/1431) - Added interface form factor for 10GBASE-CX4
* [#1432](https://github.com/netbox-community/netbox/issues/1432) - Added a `commit_rate` field to the circuits list search form
* [#1460](https://github.com/netbox-community/netbox/issues/1460) - Hostnames with no domain are now acceptable in custom URL fields

### Bug Fixes

* [#1429](https://github.com/netbox-community/netbox/issues/1429) - Fixed uptime formatting on device status page
* [#1433](https://github.com/netbox-community/netbox/issues/1433) - Fixed `devicetype_id` filter for DeviceType components
* [#1443](https://github.com/netbox-community/netbox/issues/1443) - Fixed API validation error involving custom field data
* [#1458](https://github.com/netbox-community/netbox/issues/1458) - Corrected permission name on prefix/VLAN roles list

---

## v2.1.3 (2017-08-15)

### Bug Fixes

* [#1330](https://github.com/netbox-community/netbox/issues/1330) - Raise validation error when assigning an unrelated IP as the primary IP for a device
* [#1389](https://github.com/netbox-community/netbox/issues/1389) - Avoid splitting carat/prefix on prefix list
* [#1400](https://github.com/netbox-community/netbox/issues/1400) - Removed redundant display of assigned device interface from IP address list
* [#1414](https://github.com/netbox-community/netbox/issues/1414) - Selecting a site from the rack filters automatically updates the available rack groups
* [#1419](https://github.com/netbox-community/netbox/issues/1419) - Allow editing image attachments without re-uploading an image
* [#1420](https://github.com/netbox-community/netbox/issues/1420) - Exclude virtual interfaces from device LLDP neighbors view
* [#1421](https://github.com/netbox-community/netbox/issues/1421) - Improved model validation logic for API serializers
* Fixed page title capitalization in the browsable API

---

## v2.1.2 (2017-08-04)

### Enhancements

* [#992](https://github.com/netbox-community/netbox/issues/992) - Allow the creation of multiple services per device with the same protocol and port
* Tweaked navigation menu styling

### Bug Fixes

* [#1388](https://github.com/netbox-community/netbox/issues/1388) - Fixed server error when searching globally for IPs/prefixes (rolled back #1379)
* [#1390](https://github.com/netbox-community/netbox/issues/1390) - Fixed IndexError when viewing available IPs within large IPv6 prefixes

---

## v2.1.1 (2017-08-02)

### Enhancements

* [#893](https://github.com/netbox-community/netbox/issues/893) - Allow filtering by null values for NullCharacterFields (e.g. return only unnamed devices)
* [#1368](https://github.com/netbox-community/netbox/issues/1368) - Render reservations in rack elevations view
* [#1374](https://github.com/netbox-community/netbox/issues/1374) - Added NAPALM_ARGS and NAPALM_TIMEOUT configiuration parameters
* [#1375](https://github.com/netbox-community/netbox/issues/1375) - Renamed `NETBOX_USERNAME` and `NETBOX_PASSWORD` configuration parameters to `NAPALM_USERNAME` and `NAPALM_PASSWORD`
* [#1379](https://github.com/netbox-community/netbox/issues/1379) - Allow searching devices by interface MAC address in global search

### Bug Fixes

* [#461](https://github.com/netbox-community/netbox/issues/461) - Display a validation error when attempting to assigning a new child device to a rack face/position
* [#1385](https://github.com/netbox-community/netbox/issues/1385) - Connected device API endpoint no longer requires authentication if `LOGIN_REQUIRED` is False

---

## v2.1.0 (2017-07-25)

### New Features

#### IP Address Roles ([#819](https://github.com/netbox-community/netbox/issues/819))

The IP address model now supports the assignment of a functional role to help identify special-purpose IPs. These include:

* Loopback
* Secondary
* Anycast
* VIP
* VRRP
* HSRP
* GLBP

#### Automatic Provisioning of Next Available IP ([#1246](https://github.com/netbox-community/netbox/issues/1246))

A new API endpoint has been added at `/api/ipam/prefixes/<pk>/available-ips/`. A GET request to this endpoint will return a list of available IP addresses within the prefix (up to the pagination limit). A POST request will automatically create and return the next available IP address.

#### NAPALM Integration ([#1348](https://github.com/netbox-community/netbox/issues/1348))

The [NAPALM automation](https://github.com/napalm-automation/napalm) library provides an abstracted interface for pulling live data (e.g. uptime, software version, running config, LLDP neighbors, etc.) from network devices. The NetBox API has been extended to support executing read-only NAPALM methods on devices defined in NetBox. To enable this functionality, ensure that NAPALM has been installed (`pip install napalm`) and the `NETBOX_USERNAME` and `NETBOX_PASSWORD` [configuration parameters](https://netbox.readthedocs.io/en/stable/configuration/optional-settings/#netbox_username) have been set in configuration.py.

### Enhancements

* [#838](https://github.com/netbox-community/netbox/issues/838) - Display details of all objects being edited/deleted in bulk
* [#1041](https://github.com/netbox-community/netbox/issues/1041) - Added enabled and MTU fields to the interface model
* [#1121](https://github.com/netbox-community/netbox/issues/1121) - Added asset_tag and description fields to the InventoryItem model
* [#1141](https://github.com/netbox-community/netbox/issues/1141) - Include RD when listing VRFs in a form selection field
* [#1203](https://github.com/netbox-community/netbox/issues/1203) - Implemented query filters for all models
* [#1218](https://github.com/netbox-community/netbox/issues/1218) - Added IEEE 802.11 wireless interface types
* [#1269](https://github.com/netbox-community/netbox/issues/1269) - Added circuit termination to interface serializer
* [#1320](https://github.com/netbox-community/netbox/issues/1320) - Removed checkbox from confirmation dialog

### Bug Fixes

* [#1079](https://github.com/netbox-community/netbox/issues/1079) - Order interfaces naturally via API
* [#1285](https://github.com/netbox-community/netbox/issues/1285) - Enforce model validation when creating/editing objects via the API
* [#1358](https://github.com/netbox-community/netbox/issues/1358) - Correct VRF example values in IP/prefix import forms
* [#1362](https://github.com/netbox-community/netbox/issues/1362) - Raise validation error when attempting to create an API key that's too short
* [#1371](https://github.com/netbox-community/netbox/issues/1371) - Extend DeviceSerializer.parent_device to include standard fields

### API changes

* Added a new API endpoint which makes [NAPALM](https://github.com/napalm-automation/napalm) accessible via NetBox
* Device components (console ports, power ports, interfaces, etc.) can only be filtered by a single device name or ID. This limitation was necessary to allow the natural ordering of interfaces according to the device's parent device type.
* Added two new fields to the interface serializer: `enabled` (boolean) and `mtu` (unsigned integer)
* Modified the interface serializer to include three discrete fields relating to connections: `is_connected` (boolean), `interface_connection`, and `circuit_termination`
* Added two new fields to the inventory item serializer: `asset_tag` and `description`
* Added "wireless" to interface type filter (in addition to physical, virtual, and LAG)
* Added a new endpoint at /api/ipam/prefixes/<pk>/available-ips/ to retrieve or create available IPs within a prefix
* Extended `parent_device` on DeviceSerializer to include the `url` and `display_name` of the parent Device, and the `url` of the DeviceBay
