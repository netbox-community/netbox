# NetBox v2.3 Release Notes

## v2.3.7 (2018-07-26)

### Enhancements

* [#2166](https://github.com/netbox-community/netbox/issues/2166) - Enable partial matching on device asset_tag during search

### Bug Fixes

* [#1977](https://github.com/netbox-community/netbox/issues/1977) - Fixed exception when creating a virtual chassis with a non-master device in position 1
* [#1992](https://github.com/netbox-community/netbox/issues/1992) - Isolate errors when one of multiple NAPALM methods fails
* [#2202](https://github.com/netbox-community/netbox/issues/2202) - Ditched half-baked concept of tenancy inheritance via VRF
* [#2222](https://github.com/netbox-community/netbox/issues/2222) - IP addresses created via the `available-ips` API endpoint should have the same mask as their parent prefix (not /32)
* [#2231](https://github.com/netbox-community/netbox/issues/2231) - Remove `get_absolute_url()` from DeviceRole (can apply to devices or VMs)
* [#2250](https://github.com/netbox-community/netbox/issues/2250) - Include stat counters on report result navigation
* [#2255](https://github.com/netbox-community/netbox/issues/2255) - Corrected display of results in reports list
* [#2256](https://github.com/netbox-community/netbox/issues/2256) - Prevent navigation menu overlap when jumping to test results on report page
* [#2257](https://github.com/netbox-community/netbox/issues/2257) - Corrected casting of RIR utilization stats as floats
* [#2266](https://github.com/netbox-community/netbox/issues/2266) - Permit additional logging of exceptions beyond custom middleware

---

## v2.3.6 (2018-07-16)

### Enhancements

* [#2107](https://github.com/netbox-community/netbox/issues/2107) - Added virtual chassis to global search
* [#2125](https://github.com/netbox-community/netbox/issues/2125) - Show child status in device bay list

### Bug Fixes

* [#2214](https://github.com/netbox-community/netbox/issues/2214) - Error when assigning a VLAN to an interface on a VM in a cluster with no assigned site
* [#2239](https://github.com/netbox-community/netbox/issues/2239) - Pin django-filter to version 1.1.0

---

## v2.3.5 (2018-07-02)

### Enhancements

* [#2159](https://github.com/netbox-community/netbox/issues/2159) - Allow custom choice field to specify a default choice
* [#2177](https://github.com/netbox-community/netbox/issues/2177) - Include device serial number in rack elevation pop-up
* [#2194](https://github.com/netbox-community/netbox/issues/2194) - Added `address` filter to IPAddress model

### Bug Fixes

* [#1826](https://github.com/netbox-community/netbox/issues/1826) - Corrected description of security parameters under API definition
* [#2021](https://github.com/netbox-community/netbox/issues/2021) - Fix recursion error when viewing API docs under Python 3.4
* [#2064](https://github.com/netbox-community/netbox/issues/2064) - Disable calls to online swagger validator
* [#2173](https://github.com/netbox-community/netbox/issues/2173) - Fixed IndexError when automatically allocating IP addresses from large IPv6 prefixes
* [#2181](https://github.com/netbox-community/netbox/issues/2181) - Raise validation error on invalid `prefix_length` when allocating next-available prefix
* [#2182](https://github.com/netbox-community/netbox/issues/2182) - ValueError can be raised when viewing the interface connections table
* [#2191](https://github.com/netbox-community/netbox/issues/2191) - Added missing static choices to circuits and DCIM API endpoints
* [#2192](https://github.com/netbox-community/netbox/issues/2192) - Prevent a 0U device from being assigned to a rack position

---

## v2.3.4 (2018-06-07)

### Bug Fixes

* [#2066](https://github.com/netbox-community/netbox/issues/2066) - Catch `AddrFormatError` exception on invalid IP addresses
* [#2075](https://github.com/netbox-community/netbox/issues/2075) - Enable tenant assignment when creating a rack reservation via the API
* [#2083](https://github.com/netbox-community/netbox/issues/2083) - Add missing export button to rack roles list view
* [#2087](https://github.com/netbox-community/netbox/issues/2087) - Don't overwrite existing vc_position of master device when creating a virtual chassis
* [#2093](https://github.com/netbox-community/netbox/issues/2093) - Fix link to circuit termination in device interfaces table
* [#2097](https://github.com/netbox-community/netbox/issues/2097) - Fixed queryset-based bulk deletion of clusters and regions
* [#2098](https://github.com/netbox-community/netbox/issues/2098) - Fixed missing checkboxes for host devices in cluster view
* [#2127](https://github.com/netbox-community/netbox/issues/2127) - Prevent non-conntectable interfaces from being connected
* [#2143](https://github.com/netbox-community/netbox/issues/2143) - Accept null value for empty time zone field
* [#2148](https://github.com/netbox-community/netbox/issues/2148) - Do not force timezone selection when editing sites in bulk
* [#2150](https://github.com/netbox-community/netbox/issues/2150) - Fix display of LLDP neighbors when interface name contains a colon

---

## v2.3.3 (2018-04-19)

### Enhancements

* [#1990](https://github.com/netbox-community/netbox/issues/1990) - Improved search function when assigning an IP address to an interface

### Bug Fixes

* [#1975](https://github.com/netbox-community/netbox/issues/1975) - Correct filtering logic for custom boolean fields
* [#1988](https://github.com/netbox-community/netbox/issues/1988) - Order interfaces naturally when bulk renaming
* [#1993](https://github.com/netbox-community/netbox/issues/1993) - Corrected status choices in site CSV import form
* [#1999](https://github.com/netbox-community/netbox/issues/1999) - Added missing description field to site edit form
* [#2012](https://github.com/netbox-community/netbox/issues/2012) - Fixed deselection of an IP address as the primary IP for its parent device/VM
* [#2014](https://github.com/netbox-community/netbox/issues/2014) - Allow assignment of VLANs to VM interfaces via the API
* [#2019](https://github.com/netbox-community/netbox/issues/2019) - Avoid casting oversized numbers as integers
* [#2022](https://github.com/netbox-community/netbox/issues/2022) - Show 0 for zero-value fields on CSV export
* [#2023](https://github.com/netbox-community/netbox/issues/2023) - Manufacturer should not be a required field when importing platforms
* [#2037](https://github.com/netbox-community/netbox/issues/2037) - Fixed IndexError exception when attempting to create a new rack reservation

---

## v2.3.2 (2018-03-22)

### Enhancements

* [#1586](https://github.com/netbox-community/netbox/issues/1586) - Extend bulk interface creation to support alphanumeric characters
* [#1866](https://github.com/netbox-community/netbox/issues/1866) - Introduced AnnotatedMultipleChoiceField for filter forms
* [#1930](https://github.com/netbox-community/netbox/issues/1930) - Switched to drf-yasg for Swagger API documentation
* [#1944](https://github.com/netbox-community/netbox/issues/1944) - Enable assigning VLANs to virtual machine interfaces
* [#1945](https://github.com/netbox-community/netbox/issues/1945) - Implemented a VLAN members view
* [#1949](https://github.com/netbox-community/netbox/issues/1949) - Added a button to view elevations on rack groups list
* [#1952](https://github.com/netbox-community/netbox/issues/1952) - Implemented a more robust mechanism for assigning VLANs to interfaces

### Bug Fixes

* [#1948](https://github.com/netbox-community/netbox/issues/1948) - Fix TypeError when attempting to add a member to an existing virtual chassis
* [#1951](https://github.com/netbox-community/netbox/issues/1951) - Fix TypeError exception when importing platforms
* [#1953](https://github.com/netbox-community/netbox/issues/1953) - Ignore duplicate IPs when calculating prefix utilization
* [#1955](https://github.com/netbox-community/netbox/issues/1955) - Require a plaintext value when creating a new secret
* [#1978](https://github.com/netbox-community/netbox/issues/1978) - Include all virtual chassis member interfaces in LLDP neighbors view
* [#1980](https://github.com/netbox-community/netbox/issues/1980) - Fixed bug when trying to nullify a selection custom field under Python 2

---

## v2.3.1 (2018-03-01)

### Enhancements

* [#1910](https://github.com/netbox-community/netbox/issues/1910) - Added filters for cluster group and cluster type

### Bug Fixes

* [#1915](https://github.com/netbox-community/netbox/issues/1915) - Redirect to device view after deleting a component
* [#1919](https://github.com/netbox-community/netbox/issues/1919) - Prevent exception when attempting to create a virtual machine without selecting devices
* [#1921](https://github.com/netbox-community/netbox/issues/1921) - Ignore ManyToManyFields when validating a new object created via the API
* [#1924](https://github.com/netbox-community/netbox/issues/1924) - Include VID in VLAN lists when editing an interface
* [#1926](https://github.com/netbox-community/netbox/issues/1926) - Prevent reassignment of parent device when bulk editing VC member interfaces
* [#1927](https://github.com/netbox-community/netbox/issues/1927) - Include all VC member interfaces on A side when creating a new interface connection
* [#1928](https://github.com/netbox-community/netbox/issues/1928) - Fixed form validation when modifying VLANs assigned to an interface
* [#1934](https://github.com/netbox-community/netbox/issues/1934) - Fixed exception when rendering export template on an object type with custom fields assigned
* [#1935](https://github.com/netbox-community/netbox/issues/1935) - Correct API validation of VLANs assigned to interfaces
* [#1936](https://github.com/netbox-community/netbox/issues/1936) - Trigger validation error when attempting to create a virtual chassis without specifying member positions

---

## v2.3.0 (2018-02-26)

### New Features

#### Virtual Chassis ([#99](https://github.com/netbox-community/netbox/issues/99))

A virtual chassis represents a set of physical devices with a shared control plane; for example, a stack of switches managed as a single device. Viewing the master device of a virtual chassis will show all member interfaces and IP addresses.

#### Interface VLAN Assignments ([#150](https://github.com/netbox-community/netbox/issues/150))

Interfaces can now be assigned an 802.1Q mode (access or trunked) and associated with particular VLANs. Thanks to [John Anderson](https://github.com/lampwins) for his work on this!

#### Bulk Object Creation via the API ([#1553](https://github.com/netbox-community/netbox/issues/1553))

The REST API now supports the creation of multiple objects of the same type using a single POST request. For example, to create multiple devices:

```
curl -X POST -H "Authorization: Token <TOKEN>" -H "Content-Type: application/json" -H "Accept: application/json; indent=4" http://localhost:8000/api/dcim/devices/ --data '[
{"name": "device1", "device_type": 24, "device_role": 17, "site": 6},
{"name": "device2", "device_type": 24, "device_role": 17, "site": 6},
{"name": "device3", "device_type": 24, "device_role": 17, "site": 6},
]'
```

Bulk creation is all-or-none: If any of the creations fails, the entire operation is rolled back.

#### Automatic Provisioning of Next Available Prefixes ([#1694](https://github.com/netbox-community/netbox/issues/1694))

Similar to IP addresses, NetBox now supports automated provisioning of available prefixes from within a parent prefix. For example, to retrieve the next three available /28s within a parent /24:

```
curl -X POST -H "Authorization: Token <TOKEN>" -H "Content-Type: application/json" -H "Accept: application/json; indent=4" http://localhost:8000/api/ipam/prefixes/10153/available-prefixes/ --data '[
{"prefix_length": 28},
{"prefix_length": 28},
{"prefix_length": 28}
]'
```

If the parent prefix cannot accommodate all requested prefixes, the operation is cancelled and no new prefixes are created.

#### Bulk Renaming of Device/VM Components ([#1781](https://github.com/netbox-community/netbox/issues/1781))

Device components (interfaces, console ports, etc.) can now be renamed in bulk via the web interface. This was implemented primarily to support the bulk renumbering of interfaces whose parent is part of a virtual chassis.

### Enhancements

* [#1283](https://github.com/netbox-community/netbox/issues/1283) - Added a `time_zone` field to the site model
* [#1321](https://github.com/netbox-community/netbox/issues/1321) - Added `created` and `last_updated` fields for relevant models to their API serializers
* [#1553](https://github.com/netbox-community/netbox/issues/1553) - Introduced support for bulk object creation via the API
* [#1592](https://github.com/netbox-community/netbox/issues/1592) - Added tenancy assignment for rack reservations
* [#1744](https://github.com/netbox-community/netbox/issues/1744) - Allow associating a platform with a specific manufacturer
* [#1758](https://github.com/netbox-community/netbox/issues/1758) - Added a `status` field to the site model
* [#1821](https://github.com/netbox-community/netbox/issues/1821) - Added a `description` field to the site model
* [#1864](https://github.com/netbox-community/netbox/issues/1864) - Added a `status` field to the circuit model

### Bug Fixes

* [#1136](https://github.com/netbox-community/netbox/issues/1136) - Enforce model validation during bulk update
* [#1645](https://github.com/netbox-community/netbox/issues/1645) - Simplified interface serialzier for IP addresses and optimized API view queryset
* [#1838](https://github.com/netbox-community/netbox/issues/1838) - Fix KeyError when attempting to create a VirtualChassis with no devices selected
* [#1847](https://github.com/netbox-community/netbox/issues/1847) - RecursionError when a virtual chasis master device has no name
* [#1848](https://github.com/netbox-community/netbox/issues/1848) - Allow null value for interface encapsulation mode
* [#1867](https://github.com/netbox-community/netbox/issues/1867) - Allow filtering on device status with multiple values
* [#1881](https://github.com/netbox-community/netbox/issues/1881)* - Fixed bulk editing of interface 802.1Q settings
* [#1884](https://github.com/netbox-community/netbox/issues/1884)* - Provide additional context to identify devices when creating/editing a virtual chassis
* [#1907](https://github.com/netbox-community/netbox/issues/1907) - Allow removing an IP as the primary for a device when editing the IP directly

\* New since v2.3-beta2

### Breaking Changes

* Constants representing device status have been renamed for clarity (for example, `STATUS_ACTIVE` is now `DEVICE_STATUS_ACTIVE`). Custom validation reports will need to be updated if they reference any of these constants.

### API Changes

* API creation calls now accept either a single JSON object or a list of JSON objects. If multiple objects are passed and one or more them fail validation, no objects will be created.
* Added `created` and `last_updated` fields for objects inheriting from CreatedUpdatedModel.
* Removed the `parent` filter for prefixes (use `within` or `within_include` instead).
* The IP address serializer now includes only a minimal nested representation of the assigned interface (if any) and its parent device or virtual machine.
* The rack reservation serializer now includes a nested representation of its owning user (as well as the assigned tenant, if any).
* Added endpoints for virtual chassis and VC memberships.
* Added `status`, `time_zone` (pytz format), and `description` fields to dcim.Site.
* Added a `manufacturer` foreign key field on dcim.Platform.
* Added a `status` field on circuits.Circuit.
