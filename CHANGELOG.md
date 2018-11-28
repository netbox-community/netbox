v2.4.9 (FUTURE)

## Enhancements

* [#2597](https://github.com/digitalocean/netbox/issues/2597) - Add FibreChannel SFP28 (32GFC) interface form factor

## Bug Fixes

* [#2400](https://github.com/digitalocean/netbox/issues/2400) - Correct representation of nested object assignment in API docs
* [#2576](https://github.com/digitalocean/netbox/issues/2576) - Correct type for count_* fields in site API representation
* [#2606](https://github.com/digitalocean/netbox/issues/2606) - Fixed filtering for interfaces with a virtual form factor
* [#2613](https://github.com/digitalocean/netbox/issues/2613) - Decrease live search minimum characters to three
* [#2615](https://github.com/digitalocean/netbox/issues/2615) - Tweak live search widget to use brief format for API requests

---

v2.4.8 (2018-11-20)

## Enhancements

* [#2490](https://github.com/digitalocean/netbox/issues/2490) - Added bulk editing for config contexts
* [#2557](https://github.com/digitalocean/netbox/issues/2557) - Added object view for tags

## Bug Fixes

* [#2473](https://github.com/digitalocean/netbox/issues/2473) - Fix encoding of long (>127 character) secrets
* [#2558](https://github.com/digitalocean/netbox/issues/2558) - Filter on all tags when multiple are passed
* [#2565](https://github.com/digitalocean/netbox/issues/2565) - Improved rendering of Markdown tables
* [#2575](https://github.com/digitalocean/netbox/issues/2575) - Correct model specified for rack roles table
* [#2588](https://github.com/digitalocean/netbox/issues/2588) - Catch all exceptions from failed NAPALM API Calls
* [#2589](https://github.com/digitalocean/netbox/issues/2589) - Virtual machine API serializer should require cluster assignment

---

v2.4.7 (2018-11-06)

## Enhancements

* [#2388](https://github.com/digitalocean/netbox/issues/2388) - Enable filtering of devices/VMs by region
* [#2427](https://github.com/digitalocean/netbox/issues/2427) - Allow filtering of interfaces by assigned VLAN or VLAN ID
* [#2512](https://github.com/digitalocean/netbox/issues/2512) - Add device field to inventory item filter form

## Bug Fixes

* [#2502](https://github.com/digitalocean/netbox/issues/2502) - Allow duplicate VIPs inside a uniqueness-enforced VRF
* [#2514](https://github.com/digitalocean/netbox/issues/2514) - Prevent new connections to already connected interfaces
* [#2515](https://github.com/digitalocean/netbox/issues/2515) - Only use django-rq admin tmeplate if webhooks are enabled
* [#2528](https://github.com/digitalocean/netbox/issues/2528) - Enable creating circuit terminations with interface assignment via API
* [#2549](https://github.com/digitalocean/netbox/issues/2549) - Changed naming of `peer_device` and `peer_interface` on API /dcim/connected-device/ endpoint to use underscores

---

v2.4.6 (2018-10-05)

## Enhancements

* [#2479](https://github.com/digitalocean/netbox/issues/2479) - Add user permissions for creating/modifying API tokens
* [#2487](https://github.com/digitalocean/netbox/issues/2487) - Return abbreviated API output when passed `?brief=1`

## Bug Fixes

* [#2393](https://github.com/digitalocean/netbox/issues/2393) - Fix Unicode support for CSV import under Python 2
* [#2483](https://github.com/digitalocean/netbox/issues/2483) - Set max item count of API-populated form fields to MAX_PAGE_SIZE
* [#2484](https://github.com/digitalocean/netbox/issues/2484) - Local config context not available on the Virtual Machine Edit Form
* [#2485](https://github.com/digitalocean/netbox/issues/2485) - Fix cancel button when assigning a service to a device/VM
* [#2491](https://github.com/digitalocean/netbox/issues/2491) - Fix exception when importing devices with invalid device type
* [#2492](https://github.com/digitalocean/netbox/issues/2492) - Sanitize hostname and port values returned through LLDP

---

v2.4.5 (2018-10-02)

## Enhancements

* [#2392](https://github.com/digitalocean/netbox/issues/2392) - Implemented local context data for devices and virtual machines
* [#2402](https://github.com/digitalocean/netbox/issues/2402) - Order and format JSON data in form fields
* [#2432](https://github.com/digitalocean/netbox/issues/2432) - Link remote interface connections to the Interface view
* [#2438](https://github.com/digitalocean/netbox/issues/2438) - API optimizations for tagged objects

## Bug Fixes

* [#2406](https://github.com/digitalocean/netbox/issues/2406) - Remove hard-coded limit of 1000 objects from API-populated form fields
* [#2414](https://github.com/digitalocean/netbox/issues/2414) - Tags field missing from device/VM component creation forms
* [#2442](https://github.com/digitalocean/netbox/issues/2442) - Nullify "next" link in API when limit=0 is passed
* [#2443](https://github.com/digitalocean/netbox/issues/2443) - Enforce JSON object format when creating config contexts
* [#2444](https://github.com/digitalocean/netbox/issues/2444) - Improve validation of interface MAC addresses
* [#2455](https://github.com/digitalocean/netbox/issues/2455) - Ignore unique address enforcement for IPs with a shared/virtual role
* [#2470](https://github.com/digitalocean/netbox/issues/2470) - Log the creation of device/VM components as object changes

---

v2.4.4 (2018-08-22)

## Enhancements

* [#2168](https://github.com/digitalocean/netbox/issues/2168) - Added Extreme SummitStack interface form factors
* [#2356](https://github.com/digitalocean/netbox/issues/2356) - Include cluster site as read-only field in VirtualMachine serializer
* [#2362](https://github.com/digitalocean/netbox/issues/2362) - Implemented custom admin site to properly handle BASE_PATH
* [#2254](https://github.com/digitalocean/netbox/issues/2254) - Implemented searchability for Rack Groups

## Bug Fixes

* [#2353](https://github.com/digitalocean/netbox/issues/2353) - Handle `DoesNotExist` exception when deleting a device with connected interfaces
* [#2354](https://github.com/digitalocean/netbox/issues/2354) - Increased maximum MTU for interfaces to 65536 bytes
* [#2355](https://github.com/digitalocean/netbox/issues/2355) - Added item count to inventory tab on device view
* [#2368](https://github.com/digitalocean/netbox/issues/2368) - Record change in device changelog when altering cluster assignment
* [#2369](https://github.com/digitalocean/netbox/issues/2369) - Corrected time zone validation on site API serializer
* [#2370](https://github.com/digitalocean/netbox/issues/2370) - Redirect to parent device after deleting device bays
* [#2374](https://github.com/digitalocean/netbox/issues/2374) - Fix toggling display of IP addresses in virtual machine interfaces list
* [#2378](https://github.com/digitalocean/netbox/issues/2378) - Corrected "edit" link for virtual machine interfaces

---

v2.4.3 (2018-08-09)

## Enhancements

* [#2333](https://github.com/digitalocean/netbox/issues/2333) - Added search filters for ConfigContexts

## Bug Fixes

* [#2334](https://github.com/digitalocean/netbox/issues/2334) - TypeError raised when WritableNestedSerializer receives a non-integer value
* [#2335](https://github.com/digitalocean/netbox/issues/2335) - API requires group field when creating/updating a rack
* [#2336](https://github.com/digitalocean/netbox/issues/2336) - Bulk deleting power outlets and console server ports from a device redirects to home page
* [#2337](https://github.com/digitalocean/netbox/issues/2337) - Attempting to create the next available prefix within a parent assigned to a VRF raises an AssertionError
* [#2340](https://github.com/digitalocean/netbox/issues/2340) - API requires manufacturer field when creating/updating an inventory item
* [#2342](https://github.com/digitalocean/netbox/issues/2342) - IntegrityError raised when attempting to assign an invalid IP address as the primary for a VM
* [#2344](https://github.com/digitalocean/netbox/issues/2344) - AttributeError when assigning VLANs to an interface on a device/VM not assigned to a site

---

v2.4.2 (2018-08-08)

## Bug Fixes

* [#2318](https://github.com/digitalocean/netbox/issues/2318) - ImportError when viewing a report
* [#2319](https://github.com/digitalocean/netbox/issues/2319) - Extend ChoiceField to properly handle true/false choice keys
* [#2320](https://github.com/digitalocean/netbox/issues/2320) - TypeError when dispatching a webhook with a secret key configured
* [#2321](https://github.com/digitalocean/netbox/issues/2321) - Allow explicitly setting a null value on nullable ChoiceFields
* [#2322](https://github.com/digitalocean/netbox/issues/2322) - Webhooks firing on non-enabled event types
* [#2323](https://github.com/digitalocean/netbox/issues/2323) - DoesNotExist raised when deleting devices or virtual machines
* [#2330](https://github.com/digitalocean/netbox/issues/2330) - Incorrect tab link in VRF changelog view

---

v2.4.1 (2018-08-07)

## Bug Fixes

* [#2303](https://github.com/digitalocean/netbox/issues/2303) - Always redirect to parent object when bulk editing/deleting components
* [#2308](https://github.com/digitalocean/netbox/issues/2308) - Custom fields panel absent from object view in UI
* [#2310](https://github.com/digitalocean/netbox/issues/2310) - False validation error on certain nested serializers
* [#2311](https://github.com/digitalocean/netbox/issues/2311) - Redirect to parent after editing interface from device/VM view
* [#2312](https://github.com/digitalocean/netbox/issues/2312) - Running a report yields a ValueError exception
* [#2314](https://github.com/digitalocean/netbox/issues/2314) - Serialized representation of object in change log does not include assigned tags

---

v2.4.0 (2018-08-06)

## New Features

### Webhooks ([#81](https://github.com/digitalocean/netbox/issues/81))

Webhooks enable NetBox to send a representation of an object every time one is created, updated, or deleted. Webhooks are sent from NetBox to external services via HTTP, and can be limited by object type. Services which receive a webhook can act on the data provided by NetBox to automate other tasks.

Special thanks to [John Anderson](https://github.com/lampwins) for doing the heavy lifting for this feature!

### Tagging ([#132](https://github.com/digitalocean/netbox/issues/132))

Tags are free-form labels which can be assigned to a variety of objects in NetBox. Tags can be used to categorize and filter objects in addition to built-in and custom fields. Objects to which tags apply now include a `tags` field in the API.

### Contextual Configuration Data ([#1349](https://github.com/digitalocean/netbox/issues/1349))

Sometimes it is desirable to associate arbitrary data with a group of devices to aid in their configuration. (For example, you might want to associate a set of syslog servers for all devices at a particular site.) Context data enables the association of arbitrary data (expressed in JSON format) to devices and virtual machines grouped by region, site, role, platform, and/or tenancy. Context data is arranged hierarchically, so that data with a higher weight can be entered to override more general lower-weight data. Multiple instances of data are automatically merged by NetBox to present a single dictionary for each object.

### Change Logging ([#1898](https://github.com/digitalocean/netbox/issues/1898))

When an object is created, updated, or deleted, NetBox now automatically records a serialized representation of that object (similar to how it appears in the REST API) as well the event time and user account associated with the change.

## Enhancements

* [#238](https://github.com/digitalocean/netbox/issues/238) - Allow racks with the same name within a site (but in different groups)
* [#971](https://github.com/digitalocean/netbox/issues/971) - Add a view to show all VLAN IDs available within a group
* [#1673](https://github.com/digitalocean/netbox/issues/1673) - Added object/list views for services
* [#1687](https://github.com/digitalocean/netbox/issues/1687) - Enabled custom fields for services
* [#1739](https://github.com/digitalocean/netbox/issues/1739) - Enabled custom fields for secrets
* [#1794](https://github.com/digitalocean/netbox/issues/1794) - Improved POST/PATCH representation of nested objects
* [#2029](https://github.com/digitalocean/netbox/issues/2029) - Added optional NAPALM arguments to Platform model
* [#2034](https://github.com/digitalocean/netbox/issues/2034) - Include the ID when showing nested interface connections (API change)
* [#2118](https://github.com/digitalocean/netbox/issues/2118) - Added `latitude` and `longitude` fields to Site for GPS coordinates
* [#2131](https://github.com/digitalocean/netbox/issues/2131) - Added `created` and `last_updated` fields to DeviceType
* [#2157](https://github.com/digitalocean/netbox/issues/2157) - Fixed natural ordering of objects when sorted by name
* [#2225](https://github.com/digitalocean/netbox/issues/2225) - Add "view elevations" button for site rack groups

## Bug Fixes

* [#2272](https://github.com/digitalocean/netbox/issues/2272) - Allow subdevice_role to be null on DeviceTypeSerializer"
* [#2286](https://github.com/digitalocean/netbox/issues/2286) - Fixed "mark connected" button for PDU outlet connections

## API Changes

* Introduced the `/extras/config-contexts/`, `/extras/object-changes/`, and `/extras/tags/` API endpoints
* API writes now return a nested representation of related objects (rather than only a numeric ID)
* The dcim.DeviceType serializer now includes `created` and `last_updated` fields
* The dcim.Site serializer now includes `latitude` and `longitude` fields
* The ipam.Service and secrets.Secret serializers now include custom fields
* The dcim.Platform serializer now includes a free-form (JSON) `napalm_args` field

## Changes Since v2.4-beta1

### Enhancements

* [#2229](https://github.com/digitalocean/netbox/issues/2229) - Allow mapping of ConfigContexts to tenant groups
* [#2259](https://github.com/digitalocean/netbox/issues/2259) - Add changelog tab to interface view
* [#2264](https://github.com/digitalocean/netbox/issues/2264) - Added "map it" link for site GPS coordinates

### Bug Fixes

* [#2137](https://github.com/digitalocean/netbox/issues/2137) - Fixed JSON serialization of dates
* [#2258](https://github.com/digitalocean/netbox/issues/2258) - Include changed object type on home page changelog
* [#2265](https://github.com/digitalocean/netbox/issues/2265) - Include parent regions when filtering applicable ConfigContexts
* [#2288](https://github.com/digitalocean/netbox/issues/2288) - Fix exception when assigning objects to a ConfigContext via the API
* [#2296](https://github.com/digitalocean/netbox/issues/2296) - Fix AttributeError when creating a new object with tags assigned
* [#2300](https://github.com/digitalocean/netbox/issues/2300) - Fix assignment of an interface to an IP address via API PATCH
* [#2301](https://github.com/digitalocean/netbox/issues/2301) - Fix model validation on assignment of ManyToMany fields via API PATCH
* [#2305](https://github.com/digitalocean/netbox/issues/2305) - Make VLAN fields optional when creating a VM interface via the API

---

v2.3.7 (2018-07-26)

## Enhancements

* [#2166](https://github.com/digitalocean/netbox/issues/2166) - Enable partial matching on device asset_tag during search

## Bug Fixes

* [#1977](https://github.com/digitalocean/netbox/issues/1977) - Fixed exception when creating a virtual chassis with a non-master device in position 1
* [#1992](https://github.com/digitalocean/netbox/issues/1992) - Isolate errors when one of multiple NAPALM methods fails
* [#2202](https://github.com/digitalocean/netbox/issues/2202) - Ditched half-baked concept of tenancy inheritance via VRF
* [#2222](https://github.com/digitalocean/netbox/issues/2222) - IP addresses created via the `available-ips` API endpoint should have the same mask as their parent prefix (not /32)
* [#2231](https://github.com/digitalocean/netbox/issues/2231) - Remove `get_absolute_url()` from DeviceRole (can apply to devices or VMs)
* [#2250](https://github.com/digitalocean/netbox/issues/2250) - Include stat counters on report result navigation
* [#2255](https://github.com/digitalocean/netbox/issues/2255) - Corrected display of results in reports list
* [#2256](https://github.com/digitalocean/netbox/issues/2256) - Prevent navigation menu overlap when jumping to test results on report page
* [#2257](https://github.com/digitalocean/netbox/issues/2257) - Corrected casting of RIR utilization stats as floats
* [#2266](https://github.com/digitalocean/netbox/issues/2266) - Permit additional logging of exceptions beyond custom middleware

---

v2.3.6 (2018-07-16)

## Enhancements

* [#2107](https://github.com/digitalocean/netbox/issues/2107) - Added virtual chassis to global search
* [#2125](https://github.com/digitalocean/netbox/issues/2125) - Show child status in device bay list

## Bug Fixes

* [#2214](https://github.com/digitalocean/netbox/issues/2214) - Error when assigning a VLAN to an interface on a VM in a cluster with no assigned site
* [#2239](https://github.com/digitalocean/netbox/issues/2239) - Pin django-filter to version 1.1.0

---

v2.3.5 (2018-07-02)

## Enhancements

* [#2159](https://github.com/digitalocean/netbox/issues/2159) - Allow custom choice field to specify a default choice
* [#2177](https://github.com/digitalocean/netbox/issues/2177) - Include device serial number in rack elevation pop-up
* [#2194](https://github.com/digitalocean/netbox/issues/2194) - Added `address` filter to IPAddress model

## Bug Fixes

* [#1826](https://github.com/digitalocean/netbox/issues/1826) - Corrected description of security parameters under API definition
* [#2021](https://github.com/digitalocean/netbox/issues/2021) - Fix recursion error when viewing API docs under Python 3.4
* [#2064](https://github.com/digitalocean/netbox/issues/2064) - Disable calls to online swagger validator
* [#2173](https://github.com/digitalocean/netbox/issues/2173) - Fixed IndexError when automatically allocating IP addresses from large IPv6 prefixes
* [#2181](https://github.com/digitalocean/netbox/issues/2181) - Raise validation error on invalid `prefix_length` when allocating next-available prefix
* [#2182](https://github.com/digitalocean/netbox/issues/2182) - ValueError can be raised when viewing the interface connections table
* [#2191](https://github.com/digitalocean/netbox/issues/2191) - Added missing static choices to circuits and DCIM API endpoints
* [#2192](https://github.com/digitalocean/netbox/issues/2192) - Prevent a 0U device from being assigned to a rack position

---

v2.3.4 (2018-06-07)

## Bug Fixes

* [#2066](https://github.com/digitalocean/netbox/issues/2066) - Catch `AddrFormatError` exception on invalid IP addresses
* [#2075](https://github.com/digitalocean/netbox/issues/2075) - Enable tenant assignment when creating a rack reservation via the API
* [#2083](https://github.com/digitalocean/netbox/issues/2083) - Add missing export button to rack roles list view
* [#2087](https://github.com/digitalocean/netbox/issues/2087) - Don't overwrite existing vc_position of master device when creating a virtual chassis
* [#2093](https://github.com/digitalocean/netbox/issues/2093) - Fix link to circuit termination in device interfaces table
* [#2097](https://github.com/digitalocean/netbox/issues/2097) - Fixed queryset-based bulk deletion of clusters and regions
* [#2098](https://github.com/digitalocean/netbox/issues/2098) - Fixed missing checkboxes for host devices in cluster view
* [#2127](https://github.com/digitalocean/netbox/issues/2127) - Prevent non-conntectable interfaces from being connected
* [#2143](https://github.com/digitalocean/netbox/issues/2143) - Accept null value for empty time zone field
* [#2148](https://github.com/digitalocean/netbox/issues/2148) - Do not force timezone selection when editing sites in bulk
* [#2150](https://github.com/digitalocean/netbox/issues/2150) - Fix display of LLDP neighbors when interface name contains a colon

---

v2.3.3 (2018-04-19)

## Enhancements

* [#1990](https://github.com/digitalocean/netbox/issues/1990) - Improved search function when assigning an IP address to an interface

## Bug Fixes

* [#1975](https://github.com/digitalocean/netbox/issues/1975) - Correct filtering logic for custom boolean fields
* [#1988](https://github.com/digitalocean/netbox/issues/1988) - Order interfaces naturally when bulk renaming
* [#1993](https://github.com/digitalocean/netbox/issues/1993) - Corrected status choices in site CSV import form
* [#1999](https://github.com/digitalocean/netbox/issues/1999) - Added missing description field to site edit form
* [#2012](https://github.com/digitalocean/netbox/issues/2012) - Fixed deselection of an IP address as the primary IP for its parent device/VM
* [#2014](https://github.com/digitalocean/netbox/issues/2014) - Allow assignment of VLANs to VM interfaces via the API
* [#2019](https://github.com/digitalocean/netbox/issues/2019) - Avoid casting oversized numbers as integers
* [#2022](https://github.com/digitalocean/netbox/issues/2022) - Show 0 for zero-value fields on CSV export
* [#2023](https://github.com/digitalocean/netbox/issues/2023) - Manufacturer should not be a required field when importing platforms
* [#2037](https://github.com/digitalocean/netbox/issues/2037) - Fixed IndexError exception when attempting to create a new rack reservation

---

v2.3.2 (2018-03-22)

## Enhancements

* [#1586](https://github.com/digitalocean/netbox/issues/1586) - Extend bulk interface creation to support alphanumeric characters
* [#1866](https://github.com/digitalocean/netbox/issues/1866) - Introduced AnnotatedMultipleChoiceField for filter forms
* [#1930](https://github.com/digitalocean/netbox/issues/1930) - Switched to drf-yasg for Swagger API documentation
* [#1944](https://github.com/digitalocean/netbox/issues/1944) - Enable assigning VLANs to virtual machine interfaces
* [#1945](https://github.com/digitalocean/netbox/issues/1945) - Implemented a VLAN members view
* [#1949](https://github.com/digitalocean/netbox/issues/1949) - Added a button to view elevations on rack groups list
* [#1952](https://github.com/digitalocean/netbox/issues/1952) - Implemented a more robust mechanism for assigning VLANs to interfaces

## Bug Fixes

* [#1948](https://github.com/digitalocean/netbox/issues/1948) - Fix TypeError when attempting to add a member to an existing virtual chassis
* [#1951](https://github.com/digitalocean/netbox/issues/1951) - Fix TypeError exception when importing platforms
* [#1953](https://github.com/digitalocean/netbox/issues/1953) - Ignore duplicate IPs when calculating prefix utilization
* [#1955](https://github.com/digitalocean/netbox/issues/1955) - Require a plaintext value when creating a new secret
* [#1978](https://github.com/digitalocean/netbox/issues/1978) - Include all virtual chassis member interfaces in LLDP neighbors view
* [#1980](https://github.com/digitalocean/netbox/issues/1980) - Fixed bug when trying to nullify a selection custom field under Python 2

---

v2.3.1 (2018-03-01)

## Enhancements

* [#1910](https://github.com/digitalocean/netbox/issues/1910) - Added filters for cluster group and cluster type

## Bug Fixes

* [#1915](https://github.com/digitalocean/netbox/issues/1915) - Redirect to device view after deleting a component
* [#1919](https://github.com/digitalocean/netbox/issues/1919) - Prevent exception when attempting to create a virtual machine without selecting devices
* [#1921](https://github.com/digitalocean/netbox/issues/1921) - Ignore ManyToManyFields when validating a new object created via the API
* [#1924](https://github.com/digitalocean/netbox/issues/1924) - Include VID in VLAN lists when editing an interface
* [#1926](https://github.com/digitalocean/netbox/issues/1926) - Prevent reassignment of parent device when bulk editing VC member interfaces
* [#1927](https://github.com/digitalocean/netbox/issues/1927) - Include all VC member interfaces on A side when creating a new interface connection
* [#1928](https://github.com/digitalocean/netbox/issues/1928) - Fixed form validation when modifying VLANs assigned to an interface
* [#1934](https://github.com/digitalocean/netbox/issues/1934) - Fixed exception when rendering export template on an object type with custom fields assigned
* [#1935](https://github.com/digitalocean/netbox/issues/1935) - Correct API validation of VLANs assigned to interfaces
* [#1936](https://github.com/digitalocean/netbox/issues/1936) - Trigger validation error when attempting to create a virtual chassis without specifying member positions

---

v2.3.0 (2018-02-26)

## New Features

### Virtual Chassis ([#99](https://github.com/digitalocean/netbox/issues/99))

A virtual chassis represents a set of physical devices with a shared control plane; for example, a stack of switches managed as a single device. Viewing the master device of a virtual chassis will show all member interfaces and IP addresses.

### Interface VLAN Assignments ([#150](https://github.com/digitalocean/netbox/issues/150))

Interfaces can now be assigned an 802.1Q mode (access or trunked) and associated with particular VLANs. Thanks to [John Anderson](https://github.com/lampwins) for his work on this!

### Bulk Object Creation via the API ([#1553](https://github.com/digitalocean/netbox/issues/1553))

The REST API now supports the creation of multiple objects of the same type using a single POST request. For example, to create multiple devices:

```
curl -X POST -H "Authorization: Token <TOKEN>" -H "Content-Type: application/json" -H "Accept: application/json; indent=4" http://localhost:8000/api/dcim/devices/ --data '[
{"name": "device1", "device_type": 24, "device_role": 17, "site": 6},
{"name": "device2", "device_type": 24, "device_role": 17, "site": 6},
{"name": "device3", "device_type": 24, "device_role": 17, "site": 6},
]'
```

Bulk creation is all-or-none: If any of the creations fails, the entire operation is rolled back.

### Automatic Provisioning of Next Available Prefixes ([#1694](https://github.com/digitalocean/netbox/issues/1694))

Similar to IP addresses, NetBox now supports automated provisioning of available prefixes from within a parent prefix. For example, to retrieve the next three available /28s within a parent /24:

```
curl -X POST -H "Authorization: Token <TOKEN>" -H "Content-Type: application/json" -H "Accept: application/json; indent=4" http://localhost:8000/api/ipam/prefixes/10153/available-prefixes/ --data '[
{"prefix_length": 28},
{"prefix_length": 28},
{"prefix_length": 28}
]'
```

If the parent prefix cannot accommodate all requested prefixes, the operation is cancelled and no new prefixes are created.

### Bulk Renaming of Device/VM Components ([#1781](https://github.com/digitalocean/netbox/issues/1781))

Device components (interfaces, console ports, etc.) can now be renamed in bulk via the web interface. This was implemented primarily to support the bulk renumbering of interfaces whose parent is part of a virtual chassis.

## Enhancements

* [#1283](https://github.com/digitalocean/netbox/issues/1283) - Added a `time_zone` field to the site model
* [#1321](https://github.com/digitalocean/netbox/issues/1321) - Added `created` and `last_updated` fields for relevant models to their API serializers
* [#1553](https://github.com/digitalocean/netbox/issues/1553) - Introduced support for bulk object creation via the API
* [#1592](https://github.com/digitalocean/netbox/issues/1592) - Added tenancy assignment for rack reservations
* [#1744](https://github.com/digitalocean/netbox/issues/1744) - Allow associating a platform with a specific manufacturer
* [#1758](https://github.com/digitalocean/netbox/issues/1758) - Added a `status` field to the site model
* [#1821](https://github.com/digitalocean/netbox/issues/1821) - Added a `description` field to the site model
* [#1864](https://github.com/digitalocean/netbox/issues/1864) - Added a `status` field to the circuit model

## Bug Fixes

* [#1136](https://github.com/digitalocean/netbox/issues/1136) - Enforce model validation during bulk update
* [#1645](https://github.com/digitalocean/netbox/issues/1645) - Simplified interface serialzier for IP addresses and optimized API view queryset
* [#1838](https://github.com/digitalocean/netbox/issues/1838) - Fix KeyError when attempting to create a VirtualChassis with no devices selected
* [#1847](https://github.com/digitalocean/netbox/issues/1847) - RecursionError when a virtual chasis master device has no name
* [#1848](https://github.com/digitalocean/netbox/issues/1848) - Allow null value for interface encapsulation mode
* [#1867](https://github.com/digitalocean/netbox/issues/1867) - Allow filtering on device status with multiple values
* [#1881](https://github.com/digitalocean/netbox/issues/1881)* - Fixed bulk editing of interface 802.1Q settings
* [#1884](https://github.com/digitalocean/netbox/issues/1884)* - Provide additional context to identify devices when creating/editing a virtual chassis
* [#1907](https://github.com/digitalocean/netbox/issues/1907) - Allow removing an IP as the primary for a device when editing the IP directly

\* New since v2.3-beta2

## Breaking Changes

* Constants representing device status have been renamed for clarity (for example, `STATUS_ACTIVE` is now `DEVICE_STATUS_ACTIVE`). Custom validation reports will need to be updated if they reference any of these constants.

## API Changes

* API creation calls now accept either a single JSON object or a list of JSON objects. If multiple objects are passed and one or more them fail validation, no objects will be created.
* Added `created` and `last_updated` fields for objects inheriting from CreatedUpdatedModel.
* Removed the `parent` filter for prefixes (use `within` or `within_include` instead).
* The IP address serializer now includes only a minimal nested representation of the assigned interface (if any) and its parent device or virtual machine.
* The rack reservation serializer now includes a nested representation of its owning user (as well as the assigned tenant, if any).
* Added endpoints for virtual chassis and VC memberships.
* Added `status`, `time_zone` (pytz format), and `description` fields to dcim.Site.
* Added a `manufacturer` foreign key field on dcim.Platform.
* Added a `status` field on circuits.Circuit.

---

v2.2.10 (2018-02-21)

## Enhancements

* [#78](https://github.com/digitalocean/netbox/issues/78) - Extended topology maps to support console and power connections
* [#1693](https://github.com/digitalocean/netbox/issues/1693) - Allow specifying loose or exact matching for custom field filters
* [#1714](https://github.com/digitalocean/netbox/issues/1714) - Standardized CSV export functionality for all object lists
* [#1876](https://github.com/digitalocean/netbox/issues/1876) - Added explanatory title text to disabled NAPALM buttons on device view
* [#1885](https://github.com/digitalocean/netbox/issues/1885) - Added a device filter field for primary IP

## Bug Fixes

* [#1858](https://github.com/digitalocean/netbox/issues/1858) - Include device/VM count for cluster list in global search results
* [#1859](https://github.com/digitalocean/netbox/issues/1859) - Implemented support for line breaks within CSV fields
* [#1860](https://github.com/digitalocean/netbox/issues/1860) - Do not populate initial values for custom fields when editing objects in bulk
* [#1869](https://github.com/digitalocean/netbox/issues/1869) - Corrected ordering of VRFs with duplicate names
* [#1886](https://github.com/digitalocean/netbox/issues/1886) - Allow setting the primary IPv4/v6 address for a virtual machine via the web UI

---

v2.2.9 (2018-01-31)

## Enhancements

* [#144](https://github.com/digitalocean/netbox/issues/144) - Implemented bulk import/edit/delete views for InventoryItems
* [#1073](https://github.com/digitalocean/netbox/issues/1073) - Include prefixes/IPs from all VRFs when viewing the children of a container prefix in the global table
* [#1366](https://github.com/digitalocean/netbox/issues/1366) - Enable searching for regions by name/slug
* [#1406](https://github.com/digitalocean/netbox/issues/1406) - Display tenant description as title text in object tables
* [#1824](https://github.com/digitalocean/netbox/issues/1824) - Add virtual machine count to platforms list
* [#1835](https://github.com/digitalocean/netbox/issues/1835) - Consistent positioning of previous/next rack buttons

## Bug Fixes

* [#1621](https://github.com/digitalocean/netbox/issues/1621) - Tweaked LLDP interface name evaluation logic
* [#1765](https://github.com/digitalocean/netbox/issues/1765) - Improved rendering of null options for model choice fields in filter forms
* [#1807](https://github.com/digitalocean/netbox/issues/1807) - Populate VRF from parent when creating a new prefix
* [#1809](https://github.com/digitalocean/netbox/issues/1809) - Populate tenant assignment from parent when creating a new prefix
* [#1818](https://github.com/digitalocean/netbox/issues/1818) - InventoryItem API serializer no longer requires specifying a null value for items with no parent
* [#1845](https://github.com/digitalocean/netbox/issues/1845) - Correct display of VMs in list with no role assigned
* [#1850](https://github.com/digitalocean/netbox/issues/1850) - Fix TypeError when attempting IP address import if only unnamed devices exist

---

v2.2.8 (2017-12-20)

## Enhancements

* [#1771](https://github.com/digitalocean/netbox/issues/1771) - Added name filter for racks
* [#1772](https://github.com/digitalocean/netbox/issues/1772) - Added position filter for devices
* [#1773](https://github.com/digitalocean/netbox/issues/1773) - Moved child prefixes table to its own view
* [#1774](https://github.com/digitalocean/netbox/issues/1774) - Include a button to refine search results for all object types under global search
* [#1784](https://github.com/digitalocean/netbox/issues/1784) - Added `cluster_type` filters for virtual machines

## Bug Fixes

* [#1766](https://github.com/digitalocean/netbox/issues/1766) - Fixed display of "select all" button on device power outlets list
* [#1767](https://github.com/digitalocean/netbox/issues/1767) - Use proper template for 404 responses
* [#1778](https://github.com/digitalocean/netbox/issues/1778) - Preserve initial VRF assignment when adding IP addresses in bulk from a prefix
* [#1783](https://github.com/digitalocean/netbox/issues/1783) - Added `vm_role` filter for device roles
* [#1785](https://github.com/digitalocean/netbox/issues/1785) - Omit filter forms from browsable API
* [#1787](https://github.com/digitalocean/netbox/issues/1787) - Added missing site field to virtualization cluster CSV export

---

v2.2.7 (2017-12-07)

## Enhancements

* [#1722](https://github.com/digitalocean/netbox/issues/1722) - Added virtual machine count to site view
* [#1737](https://github.com/digitalocean/netbox/issues/1737) - Added a `contains` API filter to find all prefixes containing a given IP or prefix

## Bug Fixes

* [#1712](https://github.com/digitalocean/netbox/issues/1712) - Corrected tenant inheritance for new IP addresses created from a parent prefix
* [#1721](https://github.com/digitalocean/netbox/issues/1721) - Differentiated child IP count from utilization percentage for prefixes
* [#1740](https://github.com/digitalocean/netbox/issues/1740) - Delete session_key cookie on logout
* [#1741](https://github.com/digitalocean/netbox/issues/1741) - Fixed Unicode support for secret plaintexts
* [#1743](https://github.com/digitalocean/netbox/issues/1743) - Include number of instances for device types in global search
* [#1751](https://github.com/digitalocean/netbox/issues/1751) - Corrected filtering for IPv6 addresses containing letters
* [#1756](https://github.com/digitalocean/netbox/issues/1756) - Improved natural ordering of console server ports and power outlets

---

v2.2.6 (2017-11-16)

## Enhancements

* [#1669](https://github.com/digitalocean/netbox/issues/1669) - Clicking "add an IP" from the prefix view will default to the first available IP within the prefix

## Bug Fixes

* [#1397](https://github.com/digitalocean/netbox/issues/1397) - Display global search in navigation menu unless display is less than 1200px wide
* [#1599](https://github.com/digitalocean/netbox/issues/1599) - Reduce mobile cut-off for navigation menu to 960px
* [#1715](https://github.com/digitalocean/netbox/issues/1715) - Added missing import buttons on object lists
* [#1717](https://github.com/digitalocean/netbox/issues/1717) - Fixed interface validation for virtual machines
* [#1718](https://github.com/digitalocean/netbox/issues/1718) - Set empty label to "Global" or VRF field in IP assignment form

---

v2.2.5 (2017-11-14)

## Enhancements

* [#1512](https://github.com/digitalocean/netbox/issues/1512) - Added a view to search for an IP address being assigned to an interface
* [#1679](https://github.com/digitalocean/netbox/issues/1679) - Added IP address roles to device/VM interface lists
* [#1683](https://github.com/digitalocean/netbox/issues/1683) - Replaced default 500 handler with custom middleware to provide preliminary troubleshooting assistance
* [#1684](https://github.com/digitalocean/netbox/issues/1684) - Replaced prefix `parent` filter with `within` and `within_include`

## Bug Fixes

* [#1471](https://github.com/digitalocean/netbox/issues/1471) - Correct bulk selection of IP addresses within a prefix assigned to a VRF
* [#1642](https://github.com/digitalocean/netbox/issues/1642) - Validate device type classification when creating console server ports and power outlets
* [#1650](https://github.com/digitalocean/netbox/issues/1650) - Correct numeric ordering for interfaces with no alphabetic type
* [#1676](https://github.com/digitalocean/netbox/issues/1676) - Correct filtering of child prefixes upon bulk edit/delete from the parent prefix view
* [#1689](https://github.com/digitalocean/netbox/issues/1689) - Disregard IP address mask when filtering for child IPs of a prefix
* [#1696](https://github.com/digitalocean/netbox/issues/1696) - Fix for NAPALM v2.0+
* [#1699](https://github.com/digitalocean/netbox/issues/1699) - Correct nested representation in the API of primary IPs for virtual machines and add missing primary_ip property
* [#1701](https://github.com/digitalocean/netbox/issues/1701) - Fixed validation in `extras/0008_reports.py` migration for certain versions of PostgreSQL
* [#1703](https://github.com/digitalocean/netbox/issues/1703) - Added API serializer validation for custom integer fields
* [#1705](https://github.com/digitalocean/netbox/issues/1705) - Fixed filtering of devices with a status of offline

---

v2.2.4 (2017-10-31)

## Bug Fixes

* [#1670](https://github.com/digitalocean/netbox/issues/1670) - Fixed server error when calling certain filters (regression from #1649)

---

v2.2.3 (2017-10-31)

## Enhancements

* [#999](https://github.com/digitalocean/netbox/issues/999) - Display devices on which circuits are terminated in circuits list
* [#1491](https://github.com/digitalocean/netbox/issues/1491) - Added initial data for the virtualization app
* [#1620](https://github.com/digitalocean/netbox/issues/1620) - Loosen IP address search filter to match all IPs that start with the given string
* [#1631](https://github.com/digitalocean/netbox/issues/1631) - Added a `post_run` method to the Report class
* [#1666](https://github.com/digitalocean/netbox/issues/1666) - Allow modifying the owner of a rack reservation

## Bug Fixes

* [#1513](https://github.com/digitalocean/netbox/issues/1513) - Correct filtering of custom field choices
* [#1603](https://github.com/digitalocean/netbox/issues/1603) - Hide selection checkboxes for tables with no available actions
* [#1618](https://github.com/digitalocean/netbox/issues/1618) - Allow bulk deletion of all virtual machines
* [#1619](https://github.com/digitalocean/netbox/issues/1619) - Correct text-based filtering of IP network and address fields
* [#1624](https://github.com/digitalocean/netbox/issues/1624) - Add VM count to device roles table
* [#1634](https://github.com/digitalocean/netbox/issues/1634) - Cluster should not be a required field when importing child devices
* [#1649](https://github.com/digitalocean/netbox/issues/1649) - Correct filtering on null values (e.g. ?tenant_id=0) for django-filters v1.1.0+
* [#1653](https://github.com/digitalocean/netbox/issues/1653) - Remove outdated description for DeviceType's `is_network_device` flag
* [#1664](https://github.com/digitalocean/netbox/issues/1664) - Added missing `serial` field in default rack CSV export

---

v2.2.2 (2017-10-17)

## Enhancements

* [#1580](https://github.com/digitalocean/netbox/issues/1580) - Allow cluster assignment when bulk importing devices
* [#1587](https://github.com/digitalocean/netbox/issues/1587) - Add primary IP column for virtual machines in global search results

## Bug Fixes

* [#1498](https://github.com/digitalocean/netbox/issues/1498) - Avoid duplicating nodes when generating topology maps
* [#1579](https://github.com/digitalocean/netbox/issues/1579) - Devices already assigned to a cluster cannot be added to a different cluster
* [#1582](https://github.com/digitalocean/netbox/issues/1582) - Add `virtual_machine` attribute to IPAddress
* [#1584](https://github.com/digitalocean/netbox/issues/1584) - Colorized virtual machine role column
* [#1585](https://github.com/digitalocean/netbox/issues/1585) - Fixed slug-based filtering of virtual machines
* [#1605](https://github.com/digitalocean/netbox/issues/1605) - Added clusters and virtual machines to object list for global search
* [#1609](https://github.com/digitalocean/netbox/issues/1609) - Added missing `virtual_machine` field to IP address interface serializer

---

v2.2.1 (2017-10-12)

## Bug Fixes

* [#1576](https://github.com/digitalocean/netbox/issues/1576) - Moved PostgreSQL validation logic into the relevant migration (fixed ImproperlyConfigured exception on init)

---

v2.2.0 (2017-10-12)

**Note:** This release requires PostgreSQL 9.4 or higher. Do not attempt to upgrade unless you are running at least PostgreSQL 9.4.

**Note:** The release replaces the deprecated pycrypto library with [pycryptodome](https://github.com/Legrandin/pycryptodome). The upgrade script has been extended to automatically uninstall the old library, but please verify your installed packages with `pip freeze | grep pycrypto` if you run into problems.

## New Features

### Virtual Machines and Clusters ([#142](https://github.com/digitalocean/netbox/issues/142))

Our second-most popular feature request has arrived! NetBox now supports the creation of virtual machines, which can be assigned virtual interfaces and IP addresses. VMs are arranged into clusters, each of which has a type and (optionally) a group.

### Custom Validation Reports ([#1511](https://github.com/digitalocean/netbox/issues/1511))

Users can now create custom reports which are run to validate data in NetBox. Reports work very similar to Python unit tests: Each report inherits from NetBox's Report class and contains one or more test method. Reports can be run and retrieved via the web UI, API, or CLI. See [the docs](http://netbox.readthedocs.io/en/stable/miscellaneous/reports/) for more info.

## Enhancements

* [#494](https://github.com/digitalocean/netbox/issues/494) - Include asset tag in device info pop-up on rack elevation
* [#1444](https://github.com/digitalocean/netbox/issues/1444) - Added a `serial` field to the rack model
* [#1479](https://github.com/digitalocean/netbox/issues/1479) - Added an IP address role for CARP
* [#1506](https://github.com/digitalocean/netbox/issues/1506) - Extended rack facility ID field from 30 to 50 characters
* [#1510](https://github.com/digitalocean/netbox/issues/1510) - Added ability to search by name when adding devices to a cluster
* [#1527](https://github.com/digitalocean/netbox/issues/1527) - Replace deprecated pycrypto library with pycryptodome
* [#1551](https://github.com/digitalocean/netbox/issues/1551) - Added API endpoints listing static field choices for each app
* [#1556](https://github.com/digitalocean/netbox/issues/1556) - Added CPAK, CFP2, and CFP4 100GE interface form factors
* Added CSV import views for all object types

## Bug Fixes

* [#1550](https://github.com/digitalocean/netbox/issues/1550) - Corrected interface connections link in navigation menu
* [#1554](https://github.com/digitalocean/netbox/issues/1554) - Don't require form_factor when creating an interface assigned to a virtual machine
* [#1557](https://github.com/digitalocean/netbox/issues/1557) - Added filtering for virtual machine interfaces
* [#1567](https://github.com/digitalocean/netbox/issues/1567) - Prompt user for session key when importing secrets

## API Changes

* Introduced the virtualization app and its associated endpoints at `/api/virtualization`
* Added the `/api/extras/reports` endpoint for fetching and running reports
* The `ipam.Service` and `dcim.Interface` models now have a `virtual_machine` field in addition to the `device` field. Only one of the two fields may be defined for each object
* Added a `vm_role` field to `dcim.DeviceRole`, which indicates whether a role is suitable for assigned to a virtual machine
* Added a `serial` field to 'dcim.Rack` for serial numbers
* Each app now has a `_choices` endpoint, which lists the available options for all model field with static choices (e.g. interface form factors)

---

v2.1.6 (2017-10-11)

## Enhancements

* [#1548](https://github.com/digitalocean/netbox/issues/1548) - Automatically populate tenant assignment when adding an IP address from the prefix view
* [#1561](https://github.com/digitalocean/netbox/issues/1561) - Added primary IP to the devices table in global search
* [#1563](https://github.com/digitalocean/netbox/issues/1563) - Made necessary updates for Django REST Framework v3.7.0

---

v2.1.5 (2017-09-25)

## Enhancements

* [#1484](https://github.com/digitalocean/netbox/issues/1484) - Added individual "add VLAN" buttons on the VLAN groups list
* [#1485](https://github.com/digitalocean/netbox/issues/1485) - Added `BANNER_LOGIN` configuration setting to display a banner on the login page
* [#1499](https://github.com/digitalocean/netbox/issues/1499) - Added utilization graph to child prefixes table
* [#1523](https://github.com/digitalocean/netbox/issues/1523) - Improved the natural ordering of interfaces (thanks to [@tarkatronic](https://github.com/tarkatronic))
* [#1536](https://github.com/digitalocean/netbox/issues/1536) - Improved formatting of aggregate prefix statistics

## Bug Fixes

* [#1469](https://github.com/digitalocean/netbox/issues/1469) - Allow a NAT IP to be assigned as the primary IP for a device
* [#1472](https://github.com/digitalocean/netbox/issues/1472) - Prevented truncation when displaying secret strings containing HTML characters
* [#1486](https://github.com/digitalocean/netbox/issues/1486) - Ignore subinterface IDs when validating LLDP neighbor connections
* [#1489](https://github.com/digitalocean/netbox/issues/1489) - Corrected server error on validation of empty required custom field
* [#1507](https://github.com/digitalocean/netbox/issues/1507) - Fixed error when creating the next available IP from a prefix within a VRF
* [#1520](https://github.com/digitalocean/netbox/issues/1520) - Redirect on GET request to bulk edit/delete views
* [#1522](https://github.com/digitalocean/netbox/issues/1522) - Removed object create/edit forms from the browsable API

---

v2.1.4 (2017-08-30)

## Enhancements

* [#1326](https://github.com/digitalocean/netbox/issues/1326) - Added dropdown widget with common values for circuit speed fields
* [#1341](https://github.com/digitalocean/netbox/issues/1341) - Added a `MEDIA_ROOT` configuration setting to specify where uploaded files are stored on disk
* [#1376](https://github.com/digitalocean/netbox/issues/1376) - Ignore anycast addresses when detecting duplicate IPs
* [#1402](https://github.com/digitalocean/netbox/issues/1402) - Increased max length of name field for device components
* [#1431](https://github.com/digitalocean/netbox/issues/1431) - Added interface form factor for 10GBASE-CX4
* [#1432](https://github.com/digitalocean/netbox/issues/1432) - Added a `commit_rate` field to the circuits list search form
* [#1460](https://github.com/digitalocean/netbox/issues/1460) - Hostnames with no domain are now acceptable in custom URL fields

## Bug Fixes

* [#1429](https://github.com/digitalocean/netbox/issues/1429) - Fixed uptime formatting on device status page
* [#1433](https://github.com/digitalocean/netbox/issues/1433) - Fixed `devicetype_id` filter for DeviceType components
* [#1443](https://github.com/digitalocean/netbox/issues/1443) - Fixed API validation error involving custom field data
* [#1458](https://github.com/digitalocean/netbox/issues/1458) - Corrected permission name on prefix/VLAN roles list

---

v2.1.3 (2017-08-15)

## Bug Fixes

* [#1330](https://github.com/digitalocean/netbox/issues/1330) - Raise validation error when assigning an unrelated IP as the primary IP for a device
* [#1389](https://github.com/digitalocean/netbox/issues/1389) - Avoid splitting carat/prefix on prefix list
* [#1400](https://github.com/digitalocean/netbox/issues/1400) - Removed redundant display of assigned device interface from IP address list
* [#1414](https://github.com/digitalocean/netbox/issues/1414) - Selecting a site from the rack filters automatically updates the available rack groups
* [#1419](https://github.com/digitalocean/netbox/issues/1419) - Allow editing image attachments without re-uploading an image
* [#1420](https://github.com/digitalocean/netbox/issues/1420) - Exclude virtual interfaces from device LLDP neighbors view
* [#1421](https://github.com/digitalocean/netbox/issues/1421) - Improved model validation logic for API serializers
* Fixed page title capitalization in the browsable API

---

v2.1.2 (2017-08-04)

## Enhancements

* [#992](https://github.com/digitalocean/netbox/issues/992) - Allow the creation of multiple services per device with the same protocol and port
* Tweaked navigation menu styling

## Bug Fixes

* [#1388](https://github.com/digitalocean/netbox/issues/1388) - Fixed server error when searching globally for IPs/prefixes (rolled back #1379)
* [#1390](https://github.com/digitalocean/netbox/issues/1390) - Fixed IndexError when viewing available IPs within large IPv6 prefixes

---

v2.1.1 (2017-08-02)

## Enhancements

* [#893](https://github.com/digitalocean/netbox/issues/893) - Allow filtering by null values for NullCharacterFields (e.g. return only unnamed devices)
* [#1368](https://github.com/digitalocean/netbox/issues/1368) - Render reservations in rack elevations view
* [#1374](https://github.com/digitalocean/netbox/issues/1374) - Added NAPALM_ARGS and NAPALM_TIMEOUT configiuration parameters
* [#1375](https://github.com/digitalocean/netbox/issues/1375) - Renamed `NETBOX_USERNAME` and `NETBOX_PASSWORD` configuration parameters to `NAPALM_USERNAME` and `NAPALM_PASSWORD`
* [#1379](https://github.com/digitalocean/netbox/issues/1379) - Allow searching devices by interface MAC address in global search

## Bug Fixes

* [#461](https://github.com/digitalocean/netbox/issues/461) - Display a validation error when attempting to assigning a new child device to a rack face/position
* [#1385](https://github.com/digitalocean/netbox/issues/1385) - Connected device API endpoint no longer requires authentication if `LOGIN_REQUIRED` is False

---

v2.1.0 (2017-07-25)

## New Features

### IP Address Roles ([#819](https://github.com/digitalocean/netbox/issues/819))

The IP address model now supports the assignment of a functional role to help identify special-purpose IPs. These include:

* Loopback
* Secondary
* Anycast
* VIP
* VRRP
* HSRP
* GLBP

### Automatic Provisioning of Next Available IP ([#1246](https://github.com/digitalocean/netbox/issues/1246))

A new API endpoint has been added at `/api/ipam/prefixes/<pk>/available-ips/`. A GET request to this endpoint will return a list of available IP addresses within the prefix (up to the pagination limit). A POST request will automatically create and return the next available IP address.

### NAPALM Integration ([#1348](https://github.com/digitalocean/netbox/issues/1348))

The [NAPALM automation](https://napalm-automation.net/) library provides an abstracted interface for pulling live data (e.g. uptime, software version, running config, LLDP neighbors, etc.) from network devices. The NetBox API has been extended to support executing read-only NAPALM methods on devices defined in NetBox. To enable this functionality, ensure that NAPALM has been installed (`pip install napalm`) and the `NETBOX_USERNAME` and `NETBOX_PASSWORD` [configuration parameters](http://netbox.readthedocs.io/en/stable/configuration/optional-settings/#netbox_username) have been set in configuration.py.

## Enhancements

* [#838](https://github.com/digitalocean/netbox/issues/838) - Display details of all objects being edited/deleted in bulk
* [#1041](https://github.com/digitalocean/netbox/issues/1041) - Added enabled and MTU fields to the interface model
* [#1121](https://github.com/digitalocean/netbox/issues/1121) - Added asset_tag and description fields to the InventoryItem model
* [#1141](https://github.com/digitalocean/netbox/issues/1141) - Include RD when listing VRFs in a form selection field
* [#1203](https://github.com/digitalocean/netbox/issues/1203) - Implemented query filters for all models
* [#1218](https://github.com/digitalocean/netbox/issues/1218) - Added IEEE 802.11 wireless interface types
* [#1269](https://github.com/digitalocean/netbox/issues/1269) - Added circuit termination to interface serializer
* [#1320](https://github.com/digitalocean/netbox/issues/1320) - Removed checkbox from confirmation dialog

## Bug Fixes

* [#1079](https://github.com/digitalocean/netbox/issues/1079) - Order interfaces naturally via API
* [#1285](https://github.com/digitalocean/netbox/issues/1285) - Enforce model validation when creating/editing objects via the API
* [#1358](https://github.com/digitalocean/netbox/issues/1358) - Correct VRF example values in IP/prefix import forms
* [#1362](https://github.com/digitalocean/netbox/issues/1362) - Raise validation error when attempting to create an API key that's too short
* [#1371](https://github.com/digitalocean/netbox/issues/1371) - Extend DeviceSerializer.parent_device to include standard fields

## API changes

* Added a new API endpoint which makes [NAPALM](https://github.com/napalm-automation/napalm) accessible via NetBox
* Device components (console ports, power ports, interfaces, etc.) can only be filtered by a single device name or ID. This limitation was necessary to allow the natural ordering of interfaces according to the device's parent device type.
* Added two new fields to the interface serializer: `enabled` (boolean) and `mtu` (unsigned integer)
* Modified the interface serializer to include three discrete fields relating to connections: `is_connected` (boolean), `interface_connection`, and `circuit_termination`
* Added two new fields to the inventory item serializer: `asset_tag` and `description`
* Added "wireless" to interface type filter (in addition to physical, virtual, and LAG)
* Added a new endpoint at /api/ipam/prefixes/<pk>/available-ips/ to retrieve or create available IPs within a prefix
* Extended `parent_device` on DeviceSerializer to include the `url` and `display_name` of the parent Device, and the `url` of the DeviceBay

---

v2.0.10 (2017-07-14)

## Bug Fixes

* [#1312](https://github.com/digitalocean/netbox/issues/1312) - Catch error when attempting to activate a user key with an invalid private key
* [#1333](https://github.com/digitalocean/netbox/issues/1333) - Corrected label on is_console_server field of DeviceType bulk edit form
* [#1338](https://github.com/digitalocean/netbox/issues/1338) - Allow importing prefixes with "container" status
* [#1339](https://github.com/digitalocean/netbox/issues/1339) - Fixed disappearing checkbox column under django-tables2 v1.7+
* [#1342](https://github.com/digitalocean/netbox/issues/1342) - Allow designation of users and groups when creating/editing a secret role

---

v2.0.9 (2017-07-10)

## Bug Fixes

* [#1319](https://github.com/digitalocean/netbox/issues/1319) - Fixed server error when attempting to create console/power connections
* [#1325](https://github.com/digitalocean/netbox/issues/1325) - Retain interface attachment when editing a circuit termination

---

v2.0.8 (2017-07-05)

## Enhancements

* [#1298](https://github.com/digitalocean/netbox/issues/1298) - Calculate prefix utilization based on its status (container or non-container)
* [#1303](https://github.com/digitalocean/netbox/issues/1303) - Highlight installed interface connections in green on device view
* [#1315](https://github.com/digitalocean/netbox/issues/1315) - Enforce lowercase file extensions for image attachments

## Bug Fixes

* [#1279](https://github.com/digitalocean/netbox/issues/1279) - Fix primary_ip assignment during IP address import
* [#1281](https://github.com/digitalocean/netbox/issues/1281) - Show LLDP neighbors tab on device view only if necessary conditions are met
* [#1282](https://github.com/digitalocean/netbox/issues/1282) - Fixed tooltips on "mark connected/planned" toggle buttons for device connections
* [#1288](https://github.com/digitalocean/netbox/issues/1288) - Corrected permission name for deleting image attachments
* [#1289](https://github.com/digitalocean/netbox/issues/1289) - Retain inside NAT assignment when editing an IP address
* [#1297](https://github.com/digitalocean/netbox/issues/1297) - Allow passing custom field choice selection PKs to API as string-quoted integers
* [#1299](https://github.com/digitalocean/netbox/issues/1299) - Corrected permission name for adding services to devices

---

v2.0.7 (2017-06-15)

## Enhancements

* [#626](https://github.com/digitalocean/netbox/issues/626) - Added bulk disconnect function for console/power/interface connections on device view

## Bug Fixes

* [#1238](https://github.com/digitalocean/netbox/issues/1238) - Fix error when editing an IP with a NAT assignment which has no assigned device
* [#1263](https://github.com/digitalocean/netbox/issues/1263) - Differentiate add and edit permissions for objects
* [#1265](https://github.com/digitalocean/netbox/issues/1265) - Fix console/power/interface connection validation when selecting a device via live search
* [#1266](https://github.com/digitalocean/netbox/issues/1266) - Prevent terminating a circuit to an already-connected interface
* [#1268](https://github.com/digitalocean/netbox/issues/1268) - Fix CSV import error under Python 3
* [#1273](https://github.com/digitalocean/netbox/issues/1273) - Corrected status choices in IP address import form
* [#1274](https://github.com/digitalocean/netbox/issues/1274) - Exclude unterminated circuits from topology maps
* [#1275](https://github.com/digitalocean/netbox/issues/1275) - Raise validation error on prefix import when multiple VLANs are found

---

v2.0.6 (2017-06-12)

## Enhancements

* [#40](https://github.com/digitalocean/netbox/issues/40) - Added IP utilization graph to prefix list
* [#704](https://github.com/digitalocean/netbox/issues/704) - Allow filtering VLANs by group when editing prefixes
* [#913](https://github.com/digitalocean/netbox/issues/913) - Added headers to object CSV exports
* [#990](https://github.com/digitalocean/netbox/issues/990) - Enable logging configuration in configuration.py
* [#1180](https://github.com/digitalocean/netbox/issues/1180) - Simplified the process of finding related devices when viewing a device

## Bug Fixes

* [#1253](https://github.com/digitalocean/netbox/issues/1253) - Improved `upgrade.sh` to allow forcing Python2

---

v2.0.5 (2017-06-08)

## Notes

The maximum number of objects an API consumer can request has been set to 1000 (e.g. `?limit=1000`). This limit can be modified by defining `MAX_PAGE_SIZE` in confgiuration.py. (To remove this limit, set `MAX_PAGE_SIZE=0`.)

## Enhancements

* [#655](https://github.com/digitalocean/netbox/issues/655) - Implemented header-based CSV import of objects
* [#1190](https://github.com/digitalocean/netbox/issues/1190) - Allow partial string matching when searching on custom fields
* [#1237](https://github.com/digitalocean/netbox/issues/1237) - Enabled setting limit=0 to disable pagination in API requests; added `MAX_PAGE_SIZE` configuration setting

## Bug Fixes

* [#837](https://github.com/digitalocean/netbox/issues/837) - Enforce uniqueness where applicable during bulk import of IP addresses
* [#1226](https://github.com/digitalocean/netbox/issues/1226) - Improved validation for custom field values submitted via the API
* [#1232](https://github.com/digitalocean/netbox/issues/1232) - Improved rack space validation on bulk import of devices (see #655)
* [#1235](https://github.com/digitalocean/netbox/issues/1235) - Fix permission name for adding/editing inventory items
* [#1236](https://github.com/digitalocean/netbox/issues/1236) - Truncate rack names in elevations list; add facility ID
* [#1239](https://github.com/digitalocean/netbox/issues/1239) - Fix server error when creating VLANGroup via API
* [#1243](https://github.com/digitalocean/netbox/issues/1243) - Catch ValueError in IP-based object filters
* [#1244](https://github.com/digitalocean/netbox/issues/1244) - Corrected "device" secrets filter to accept a device name

---

v2.0.4 (2017-05-25)

## Bug Fixes

* [#1206](https://github.com/digitalocean/netbox/issues/1206) - Fix redirection in admin UI after activating secret keys when BASE_PATH is set
* [#1207](https://github.com/digitalocean/netbox/issues/1207) - Include nested LAG serializer when showing interface connections (API)
* [#1210](https://github.com/digitalocean/netbox/issues/1210) - Fix TemplateDoesNotExist errors on browsable API views
* [#1212](https://github.com/digitalocean/netbox/issues/1212) - Allow assigning new VLANs to global VLAN groups
* [#1213](https://github.com/digitalocean/netbox/issues/1213) - Corrected table header ordering links on object list views
* [#1214](https://github.com/digitalocean/netbox/issues/1214) - Add status to list of required fields on child device import form
* [#1219](https://github.com/digitalocean/netbox/issues/1219) - Fix image attachment URLs when BASE_PATH is set
* [#1220](https://github.com/digitalocean/netbox/issues/1220) - Suppressed innocuous warning about untracked migrations under Python 3
* [#1229](https://github.com/digitalocean/netbox/issues/1229) - Fix validation error on forms where API search is used

---

v2.0.3 (2017-05-18)

## Enhancements

* [#1196](https://github.com/digitalocean/netbox/issues/1196) - Added a lag_id filter to the API interfaces view
* [#1198](https://github.com/digitalocean/netbox/issues/1198) - Allow filtering unracked devices on device list

## Bug Fixes

* [#1157](https://github.com/digitalocean/netbox/issues/1157) - Hide nav menu search bar on small displays
* [#1186](https://github.com/digitalocean/netbox/issues/1186) - Corrected VLAN edit form so that site assignment is not required
* [#1187](https://github.com/digitalocean/netbox/issues/1187) - Fixed table pagination by introducing a custom table template
* [#1188](https://github.com/digitalocean/netbox/issues/1188) - Serialize interface LAG as nested objected (API)
* [#1189](https://github.com/digitalocean/netbox/issues/1189) - Enforce consistent ordering of objects returned by a global search
* [#1191](https://github.com/digitalocean/netbox/issues/1191) - Bulk selection of IPs under a prefix incorrect when "select all" is used
* [#1195](https://github.com/digitalocean/netbox/issues/1195) - Unable to create an interface connection when searching for peer device
* [#1197](https://github.com/digitalocean/netbox/issues/1197) - Fixed status assignment during bulk import of devices, prefixes, IPs, and VLANs
* [#1199](https://github.com/digitalocean/netbox/issues/1199) - Bulk import of secrets does not prompt user to generate a session key
* [#1200](https://github.com/digitalocean/netbox/issues/1200) - Form validation error when connecting power ports to power outlets

---

v2.0.2 (2017-05-15)

## Enhancements

* [#1122](https://github.com/digitalocean/netbox/issues/1122) - Include NAT inside IPs in IP address list
* [#1137](https://github.com/digitalocean/netbox/issues/1137) - Allow filtering devices list by rack
* [#1170](https://github.com/digitalocean/netbox/issues/1170) - Include A and Z sites for circuits in global search results
* [#1172](https://github.com/digitalocean/netbox/issues/1172) - Linkify racks in side-by-side elevations view
* [#1177](https://github.com/digitalocean/netbox/issues/1177) - Render planned connections as dashed lines on topology maps
* [#1179](https://github.com/digitalocean/netbox/issues/1179) - Adjust topology map text color based on node background
* On all object edit forms, allow filtering the tenant list by tenant group

## Bug Fixes

* [#1158](https://github.com/digitalocean/netbox/issues/1158) - Exception thrown when creating a device component with an invalid name
* [#1159](https://github.com/digitalocean/netbox/issues/1159) - Only superusers can see "edit IP" buttons on the device interfaces list
* [#1160](https://github.com/digitalocean/netbox/issues/1160) - Linkify secrets and tenants in global search results
* [#1161](https://github.com/digitalocean/netbox/issues/1161) - Fix "add another" behavior when creating an API token
* [#1166](https://github.com/digitalocean/netbox/issues/1166) - Fixed bulk IP address creation when assigning tenants
* [#1168](https://github.com/digitalocean/netbox/issues/1168) - Total count of objects missing from list view paginator
* [#1171](https://github.com/digitalocean/netbox/issues/1171) - Allow removing site assignment when bulk editing VLANs
* [#1173](https://github.com/digitalocean/netbox/issues/1173) - Tweak interface manager to fall back to naive ordering

---

v2.0.1 (2017-05-10)

## Bug Fixes

* [#1149](https://github.com/digitalocean/netbox/issues/1149) - Port list does not populate when creating a console or power connection
* [#1150](https://github.com/digitalocean/netbox/issues/1150) - Error when uploading image attachments with Unicode names under Python 2
* [#1151](https://github.com/digitalocean/netbox/issues/1151) - Server error: name 'escape' is not defined
* [#1152](https://github.com/digitalocean/netbox/issues/1152) - Unable to edit user keys
* [#1153](https://github.com/digitalocean/netbox/issues/1153) - UnicodeEncodeError when searching for non-ASCII characters on Python 2

---

v2.0.0 (2017-05-09)

## New Features

### API 2.0 ([#113](https://github.com/digitalocean/netbox/issues/113))

The NetBox API has been completely rewritten and now features full read/write ability.

### Image Attachments ([#152](https://github.com/digitalocean/netbox/issues/152))

Users are now able to attach photos and other images to sites, racks, and devices. (Please ensure that the new `media` directory is writable by the system account NetBox runs as.)

### Global Search ([#159](https://github.com/digitalocean/netbox/issues/159))

NetBox now supports searching across all primary object types at once.

### Rack Elevations View ([#951](https://github.com/digitalocean/netbox/issues/951))

A new view has been introduced to display the elevations of multiple racks side-by-side.

## Enhancements

* [#154](https://github.com/digitalocean/netbox/issues/154) - Expanded device status field to include options other than active/offline
* [#430](https://github.com/digitalocean/netbox/issues/430) - Include circuits when rendering topology maps
* [#578](https://github.com/digitalocean/netbox/issues/578) - Show topology maps not assigned to a site on the home view
* [#1100](https://github.com/digitalocean/netbox/issues/1100) - Add a "view all" link to completed bulk import views is_pool for prefixes)
* [#1110](https://github.com/digitalocean/netbox/issues/1110) - Expand bulk edit forms to include boolean fields (e.g. toggle is_pool for prefixes)

## Bug Fixes

From v1.9.6:

* [#403](https://github.com/digitalocean/netbox/issues/403) - Record console/power/interface connects and disconnects as user actions
* [#853](https://github.com/digitalocean/netbox/issues/853) -  Added "status" field to device bulk import form
* [#1101](https://github.com/digitalocean/netbox/issues/1101) - Fix AJAX scripting for device component selection forms
* [#1103](https://github.com/digitalocean/netbox/issues/1103) - Correct handling of validation errors when creating IP addresses in bulk
* [#1104](https://github.com/digitalocean/netbox/issues/1104) - Fix VLAN assignment on prefix import
* [#1115](https://github.com/digitalocean/netbox/issues/1115) - Enabled responsive (side-scrolling) tables for small screens
* [#1116](https://github.com/digitalocean/netbox/issues/1116) - Correct object links on recursive deletion error
* [#1125](https://github.com/digitalocean/netbox/issues/1125) - Include MAC addresses on a device's interface list
* [#1144](https://github.com/digitalocean/netbox/issues/1144) - Allow multiple status selections for Prefix, IP address, and VLAN filters

From beta3:

* [#1113](https://github.com/digitalocean/netbox/issues/1113) - Fixed server error when attempting to delete an image attachment
* [#1114](https://github.com/digitalocean/netbox/issues/1114) - Suppress OSError when attempting to access a deleted image attachment
* [#1126](https://github.com/digitalocean/netbox/issues/1126) - Fixed server error when editing a user key via admin UI attachment
* [#1132](https://github.com/digitalocean/netbox/issues/1132) - Prompt user to unlock session key when importing secrets

## Additional Changes

* The Module DCIM model has been renamed to InventoryItem to better reflect its intended function, and to make room for work on [#824](https://github.com/digitalocean/netbox/issues/824).
* Redundant portions of the admin UI have been removed ([#973](https://github.com/digitalocean/netbox/issues/973)).
* The Docker build components have been moved into [their own repository](https://github.com/digitalocean/netbox-docker).

---

v1.9.6 (2017-04-21)

## Improvements

* [#878](https://github.com/digitalocean/netbox/issues/878) - Merged IP addresses with interfaces list on device view
* [#1001](https://github.com/digitalocean/netbox/issues/1001) - Interface assignment can be modified when editing an IP address
* [#1084](https://github.com/digitalocean/netbox/issues/1084) - Include custom fields when creating IP addresses in bulk

## Bug Fixes

* [#1057](https://github.com/digitalocean/netbox/issues/1057) - Corrected VLAN validation during prefix import
* [#1061](https://github.com/digitalocean/netbox/issues/1061) - Fixed potential for script injection via create/edit/delete messages
* [#1070](https://github.com/digitalocean/netbox/issues/1070) - Corrected installation instructions for Python3 on CentOS/RHEL
* [#1071](https://github.com/digitalocean/netbox/issues/1071) - Protect assigned circuit termination when an interface is deleted
* [#1072](https://github.com/digitalocean/netbox/issues/1072) - Order LAG interfaces naturally on bulk interface edit form
* [#1074](https://github.com/digitalocean/netbox/issues/1074) - Require ncclient 0.5.3 (Python 3 fix)
* [#1090](https://github.com/digitalocean/netbox/issues/1090) - Improved installation documentation for Python 3
* [#1092](https://github.com/digitalocean/netbox/issues/1092) - Increase randomness in SECRET_KEY generation tool

---

v1.9.5 (2017-04-06)

## Improvements

* [#1052](https://github.com/digitalocean/netbox/issues/1052) - Added rack reservation list and bulk delete views

## Bug Fixes

* [#1038](https://github.com/digitalocean/netbox/issues/1038) - Suppress upgrading to Django 1.11 (will be supported in v2.0)
* [#1037](https://github.com/digitalocean/netbox/issues/1037) - Fixed error on VLAN import with duplicate VLAN group names
* [#1047](https://github.com/digitalocean/netbox/issues/1047) - Correct ordering of numbered subinterfaces
* [#1051](https://github.com/digitalocean/netbox/issues/1051) - Upgraded django-rest-swagger

---

v1.9.4-r1 (2017-04-04)

## Improvements

* [#362](https://github.com/digitalocean/netbox/issues/362) - Added per_page query parameter to control pagination page length

## Bug Fixes

* [#991](https://github.com/digitalocean/netbox/issues/991) - Correct server error on "create and connect another" interface connection
* [#1022](https://github.com/digitalocean/netbox/issues/1022) - Record user actions when creating IP addresses in bulk
* [#1027](https://github.com/digitalocean/netbox/issues/1027) - Fixed nav menu highlighting when BASE_PATH is set
* [#1034](https://github.com/digitalocean/netbox/issues/1034) - Added migration missing from v1.9.4 release

---

v1.9.3 (2017-03-23)

## Improvements

* [#972](https://github.com/digitalocean/netbox/issues/972) - Add ability to filter connections list by device name
* [#974](https://github.com/digitalocean/netbox/issues/974) - Added MAC address filter to API interfaces list
* [#978](https://github.com/digitalocean/netbox/issues/978) - Allow filtering device types by function and subdevice role
* [#981](https://github.com/digitalocean/netbox/issues/981) - Allow filtering primary objects by a given set of IDs
* [#983](https://github.com/digitalocean/netbox/issues/983) - Include peer device names when listing circuits in device view

## Bug Fixes

* [#967](https://github.com/digitalocean/netbox/issues/967) - Fix error when assigning a new interface to a LAG

---

v1.9.2 (2017-03-14)

## Bug Fixes

* [#950](https://github.com/digitalocean/netbox/issues/950) - Fix site_id error on child device import
* [#956](https://github.com/digitalocean/netbox/issues/956) - Correct bug affecting unnamed rackless devices
* [#957](https://github.com/digitalocean/netbox/issues/957) - Correct device site filter count to include unracked devices
* [#963](https://github.com/digitalocean/netbox/issues/963) - Fix bug in IPv6 address range expansion
* [#964](https://github.com/digitalocean/netbox/issues/964) - Fix bug when bulk editing/deleting filtered set of objects

---

v1.9.1 (2017-03-08)

## Improvements

* [#945](https://github.com/digitalocean/netbox/issues/945) - Display the current user in the navigation menu
* [#946](https://github.com/digitalocean/netbox/issues/946) - Disregard mask length when filtering IP addresses by a parent prefix

## Bug Fixes

* [#941](https://github.com/digitalocean/netbox/issues/941) - Corrected old references to rack.site on Device
* [#943](https://github.com/digitalocean/netbox/issues/943) - Child prefixes missing on Python 3
* [#944](https://github.com/digitalocean/netbox/issues/944) - Corrected console and power connection form behavior
* [#948](https://github.com/digitalocean/netbox/issues/948) - Region name should be hyperlinked to site list

---

v1.9.0-r1 (2017-03-03)

## New Features

### Rack Reservations ([#36](https://github.com/digitalocean/netbox/issues/36))

Users can now reserve an arbitrary number of units within a rack, adding a comment noting their intentions. Reservations do not interfere with installed devices: It is possible to reserve a unit for future use even if it is currently occupied by a device.

### Interface Groups ([#105](https://github.com/digitalocean/netbox/issues/105))

A new Link Aggregation Group (LAG) virtual form factor has been added. Physical interfaces can be assigned to a parent LAG interface to represent a port-channel or similar logical bundling of links.

### Regions ([#164](https://github.com/digitalocean/netbox/issues/164))

A new region model has been introduced to allow for the geographic organization of sites. Regions can be nested recursively to form a hierarchy.

### Rackless Devices ([#198](https://github.com/digitalocean/netbox/issues/198))

Previous releases required each device to be assigned to a particular rack within a site. This requirement has been relaxed so that devices must only be assigned to a site, and may optionally be assigned to a rack.

### Global VLANs ([#235](https://github.com/digitalocean/netbox/issues/235))

Assignment of VLANs and VLAN groups to sites is now optional, allowing for the representation of a VLAN spanning multiple sites.

## Improvements

* [#862](https://github.com/digitalocean/netbox/issues/862) - Show both IPv6 and IPv4 primary IPs in device list
* [#894](https://github.com/digitalocean/netbox/issues/894) - Expand device name max length to 64 characters
* [#898](https://github.com/digitalocean/netbox/issues/898) - Expanded circuits list in provider view rack face
* [#901](https://github.com/digitalocean/netbox/issues/901) - Support for filtering prefixes and IP addresses by mask length

## Bug Fixes

* [#872](https://github.com/digitalocean/netbox/issues/872) - Fixed TypeError on bulk IP address creation (Python 3)
* [#884](https://github.com/digitalocean/netbox/issues/884) - Preserve selected rack unit when changing a device's rack face
* [#892](https://github.com/digitalocean/netbox/issues/892) - Restored missing edit/delete buttons when viewing child prefixes and IP addresses from a parent object
* [#897](https://github.com/digitalocean/netbox/issues/897) - Fixed power connections CSV export
* [#903](https://github.com/digitalocean/netbox/issues/903) - Only alert on missing critical connections if present in the parent device type
* [#935](https://github.com/digitalocean/netbox/issues/935) - Fix form validation error when connecting an interface using live search
* [#937](https://github.com/digitalocean/netbox/issues/937) - Region assignment should be optional when creating a site
* [#938](https://github.com/digitalocean/netbox/issues/938) - Provider view yields an error if one or more circuits is assigned to a tenant

---

v1.8.4 (2017-02-03)

## Improvements

* [#856](https://github.com/digitalocean/netbox/issues/856) - Strip whitespace from fields during CSV import

## Bug Fixes

* [#851](https://github.com/digitalocean/netbox/issues/851) - Resolve encoding issues during import/export (Python 3)
* [#854](https://github.com/digitalocean/netbox/issues/854) - Correct processing of get_return_url() in ObjectDeleteView
* [#859](https://github.com/digitalocean/netbox/issues/859) - Fix Javascript for connection status toggle button on device view
* [#861](https://github.com/digitalocean/netbox/issues/861) - Avoid overwriting device primary IP assignment from alternate family during bulk import of IP addresses
* [#865](https://github.com/digitalocean/netbox/issues/865) - Fix server error when attempting to delete a protected object parent (Python 3)

---

v1.8.3 (2017-01-26)

## Improvements

* [#782](https://github.com/digitalocean/netbox/issues/782) - Allow filtering devices list by manufacturer
* [#820](https://github.com/digitalocean/netbox/issues/820) - Add VLAN column to parent prefixes table on IP address view
* [#821](https://github.com/digitalocean/netbox/issues/821) - Support for comma separation in bulk IP/interface creation
* [#827](https://github.com/digitalocean/netbox/issues/827) - **Introduced support for Python 3**
* [#836](https://github.com/digitalocean/netbox/issues/836) - Add "deprecated" status for IP addresses
* [#841](https://github.com/digitalocean/netbox/issues/841) - Merged search and filter forms on all object lists

## Bug Fixes

* [#816](https://github.com/digitalocean/netbox/issues/816) - Redirect back to parent prefix view after deleting child prefixes termination
* [#817](https://github.com/digitalocean/netbox/issues/817) - Update last_updated time of a circuit when editing a child termination
* [#830](https://github.com/digitalocean/netbox/issues/830) - Redirect user to device view after editing a device component
* [#840](https://github.com/digitalocean/netbox/issues/840) - Correct API path resolution for secrets when BASE_PATH is configured
* [#844](https://github.com/digitalocean/netbox/issues/844) - Apply order_naturally() to API interfaces list
* [#845](https://github.com/digitalocean/netbox/issues/845) - Fix missing edit/delete buttons on object tables for non-superusers


---

v1.8.2 (2017-01-18)

## Improvements

* [#284](https://github.com/digitalocean/netbox/issues/284) - Enabled toggling of interface display order per device type
* [#760](https://github.com/digitalocean/netbox/issues/760) - Redirect user back to device view after deleting an assigned IP address
* [#783](https://github.com/digitalocean/netbox/issues/783) - Add a description field to the Circuit model
* [#797](https://github.com/digitalocean/netbox/issues/797) - Add description column to VLANs table
* [#803](https://github.com/digitalocean/netbox/issues/803) - Clarify that no child objects are deleted when deleting a prefix
* [#805](https://github.com/digitalocean/netbox/issues/805) - Linkify site column in device table

## Bug Fixes

* [#776](https://github.com/digitalocean/netbox/issues/776) - Prevent circuits from appearing twice while searching
* [#778](https://github.com/digitalocean/netbox/issues/778) - Corrected an issue preventing multiple interfaces with the same position ID from appearing in a device's interface list
* [#785](https://github.com/digitalocean/netbox/issues/785) - Trigger validation error when importing a prefix assigned to a nonexistent VLAN
* [#802](https://github.com/digitalocean/netbox/issues/802) - Fixed enforcement of ENFORCE_GLOBAL_UNIQUE for prefixes
* [#807](https://github.com/digitalocean/netbox/issues/807) - Redirect user back to form when adding IP addresses in bulk and "create and add another" is clicked
* [#810](https://github.com/digitalocean/netbox/issues/810) - Suppress unique IP validation on invalid IP addresses and prefixes

---

v1.8.1 (2017-01-04)

## Improvements

* [#771](https://github.com/digitalocean/netbox/issues/771) - Don't automatically redirect user when only one object is returned in a list

## Bug Fixes

* [#764](https://github.com/digitalocean/netbox/issues/764) - Encapsulate in double quotes values containing commas when exporting to CSV
* [#767](https://github.com/digitalocean/netbox/issues/767) - Fixes xconnect_id error when searching for circuits
* [#769](https://github.com/digitalocean/netbox/issues/769) - Show default value for boolean custom fields
* [#772](https://github.com/digitalocean/netbox/issues/772) - Fixes TypeError in API RackUnitListView when no device is excluded

---

v1.8.0 (2017-01-03)

## New Features

### Point-to-Point Circuits ([#49](https://github.com/digitalocean/netbox/issues/49))

Until now, NetBox has supported tracking only one end of a data circuit. This is fine for Internet connections where you don't care (or know) much about the provider side of the circuit, but many users need the ability to track inter-site circuits as well. This release expands circuit modeling so that each circuit can have an A and/or Z side. Each endpoint must be terminated to a site, and may optionally be terminated to a specific device and interface within that site.

### L4 Services ([#539](https://github.com/digitalocean/netbox/issues/539))

Our first major community contribution introduces the ability to track discrete TCP and UDP services associated with a device (for example, SSH or HTTP). Each service can optionally be assigned to one or more specific IP addresses belonging to the device. Thanks to [@if-fi](https://github.com/if-fi) for the addition!

## Improvements

* [#122](https://github.com/digitalocean/netbox/issues/122) - Added comments field to device types
* [#181](https://github.com/digitalocean/netbox/issues/181) - Implemented support for bulk IP address creation
* [#613](https://github.com/digitalocean/netbox/issues/613) - Added prefixes column to VLAN list; added VLAN column to prefix list
* [#716](https://github.com/digitalocean/netbox/issues/716) - Add ASN field to site bulk edit form
* [#722](https://github.com/digitalocean/netbox/issues/722) - Enabled custom fields for device types
* [#743](https://github.com/digitalocean/netbox/issues/743) - Enabled bulk creation of all device components
* [#756](https://github.com/digitalocean/netbox/issues/756) - Added contact details to site model

## Bug Fixes

* [#563](https://github.com/digitalocean/netbox/issues/563) - Allow a device to be flipped from one rack face to the other without moving it
* [#658](https://github.com/digitalocean/netbox/issues/658) - Enabled conditional treatment of network/broadcast IPs for a prefix by defining it as a pool
* [#741](https://github.com/digitalocean/netbox/issues/741) - Hide "select all" button for users without edit permissions
* [#744](https://github.com/digitalocean/netbox/issues/744) - Fixed export of sites without an AS number
* [#747](https://github.com/digitalocean/netbox/issues/747) - Fixed natural_order_by integer cast error on large numbers
* [#751](https://github.com/digitalocean/netbox/issues/751) - Fixed python-cryptography installation issue on Debian
* [#763](https://github.com/digitalocean/netbox/issues/763) - Added missing fields to CSV exports for racks and prefixes

---

v1.7.3 (2016-12-08)

## Bug Fixes

* [#724](https://github.com/digitalocean/netbox/issues/724) - Exempt API views from LoginRequiredMiddleware to enable basic HTTP authentication when LOGIN_REQUIRED is true
* [#729](https://github.com/digitalocean/netbox/issues/729) - Corrected cancellation links when editing secondary objects
* [#732](https://github.com/digitalocean/netbox/issues/732) - Allow custom select field values to be deselected if the field is not required
* [#733](https://github.com/digitalocean/netbox/issues/733) - Fixed MAC address filter on device list
* [#734](https://github.com/digitalocean/netbox/issues/734) - Corrected display of device type when editing a device

---

v1.7.2-r1 (2016-12-06)

## Improvements

* [#663](https://github.com/digitalocean/netbox/issues/663) - Added MAC address search field to device list
* [#672](https://github.com/digitalocean/netbox/issues/672) - Increased the selection of available colors for rack and device roles
* [#695](https://github.com/digitalocean/netbox/issues/695) - Added is_private field to RIR

## Bug Fixes

* [#677](https://github.com/digitalocean/netbox/issues/677) - Fix setuptools installation error on Debian 8.6
* [#696](https://github.com/digitalocean/netbox/issues/696) - Corrected link to VRF in prefix and IP address breadcrumbs
* [#702](https://github.com/digitalocean/netbox/issues/702) - Improved Unicode support for custom fields
* [#712](https://github.com/digitalocean/netbox/issues/712) - Corrected export of tenants which are not assigned to a group
* [#713](https://github.com/digitalocean/netbox/issues/713) - Include a label for the comments field when editing circuits, providers, or racks in bulk
* [#718](https://github.com/digitalocean/netbox/issues/718) - Restore is_primary field on IP assignment form
* [#723](https://github.com/digitalocean/netbox/issues/723) - API documentation is now accessible when using BASE_PATH
* [#727](https://github.com/digitalocean/netbox/issues/727) - Corrected error in rack elevation display (v1.7.2)

---

v1.7.1 (2016-11-15)

## Improvements

* [#667](https://github.com/digitalocean/netbox/issues/667) - Added prefix utilization statistics to the RIR list view
* [#685](https://github.com/digitalocean/netbox/issues/685) - When assigning an IP to a device, automatically select the interface if only one exists

## Bug Fixes

* [#674](https://github.com/digitalocean/netbox/issues/674) - Fix assignment of status to imported IP addresses
* [#676](https://github.com/digitalocean/netbox/issues/676) - Server error when bulk editing device types
* [#678](https://github.com/digitalocean/netbox/issues/678) - Server error on device import specifying an invalid device type
* [#691](https://github.com/digitalocean/netbox/issues/691) - Allow the assignment of power ports to PDUs
* [#692](https://github.com/digitalocean/netbox/issues/692) - Form errors are not displayed on checkbox fields

---

v1.7.0 (2016-11-03)

## New Features

### IP address statuses ([#87](https://github.com/digitalocean/netbox/issues/87))

An IP address can now be designated as active, reserved, or DHCP. The DHCP status implies that the IP address is part of a DHCP pool and may or may not be assigned to a DHCP client.

### Top-to-bottom rack numbering ([#191](https://github.com/digitalocean/netbox/issues/191))

Racks can now be set to have descending rack units, with U1 at the top of the rack. When adding a device to a rack with descending units, be sure to position it in the **lowest-numbered** unit which it occupies (this will be physically the topmost unit).

## Improvements
* [#211](https://github.com/digitalocean/netbox/issues/211) - Allow device assignment and removal from IP address view
* [#630](https://github.com/digitalocean/netbox/issues/630) - Added a custom 404 page
* [#652](https://github.com/digitalocean/netbox/issues/652) - Use password input controls when editing secrets
* [#654](https://github.com/digitalocean/netbox/issues/654) - Added Cisco FlexStack and FlexStack Plus form factors
* [#661](https://github.com/digitalocean/netbox/issues/661) - Display relevant IP addressing when viewing a circuit

## Bug Fixes
* [#632](https://github.com/digitalocean/netbox/issues/632) - Use semicolons instead of commas to separate regexes in topology maps
* [#647](https://github.com/digitalocean/netbox/issues/647) - Extend form used when assigning an IP to a device
* [#657](https://github.com/digitalocean/netbox/issues/657) - Unicode error when adding device modules
* [#660](https://github.com/digitalocean/netbox/issues/660) - Corrected calculation of utilized space in rack list
* [#664](https://github.com/digitalocean/netbox/issues/664) - Fixed bulk creation of interfaces across multiple devices

---

v1.6.3 (2016-10-19)

## Improvements

* [#353](https://github.com/digitalocean/netbox/issues/353) - Bulk editing of device and device type interfaces
* [#527](https://github.com/digitalocean/netbox/issues/527) - Support for nullification of fields when bulk editing
* [#592](https://github.com/digitalocean/netbox/issues/592) - Allow space-delimited lists of ALLOWED_HOSTS in Docker
* [#608](https://github.com/digitalocean/netbox/issues/608) - Added "select all" button for device and device type components

## Bug Fixes

* [#602](https://github.com/digitalocean/netbox/issues/602) - Correct display of custom integer fields with value of 0 or 1
* [#604](https://github.com/digitalocean/netbox/issues/604) - Correct display of unnamed devices in form selection fields
* [#611](https://github.com/digitalocean/netbox/issues/611) - Power/console/interface connection import: status field should be case-insensitive
* [#615](https://github.com/digitalocean/netbox/issues/615) - Account for BASE_PATH in static URLs and during login
* [#616](https://github.com/digitalocean/netbox/issues/616) - Correct display of custom URL fields

---

v1.6.2-r1 (2016-10-04)

## Improvements

* [#212](https://github.com/digitalocean/netbox/issues/212) - Introduced the `BASE_PATH` configuration setting to allow running NetBox in a URL subdirectory
* [#345](https://github.com/digitalocean/netbox/issues/345) - Bulk edit: allow user to select all objects on page or all matching query
* [#475](https://github.com/digitalocean/netbox/issues/475) - Display "add" buttons at top and bottom of all device/device type panels
* [#480](https://github.com/digitalocean/netbox/issues/480) - Improved layout on mobile devices
* [#481](https://github.com/digitalocean/netbox/issues/481) - Require interface creation before trying to assign an IP to a device
* [#575](https://github.com/digitalocean/netbox/issues/575) - Allow all valid URL schemes in custom fields
* [#579](https://github.com/digitalocean/netbox/issues/579) - Add a description field to export templates

## Bug Fixes

* [#466](https://github.com/digitalocean/netbox/issues/466) - Validate available free space for all instances when increasing the U height of a device type
* [#571](https://github.com/digitalocean/netbox/issues/571) - Correct rack group filter on device list
* [#576](https://github.com/digitalocean/netbox/issues/576) - Delete all relevant CustomFieldValues when deleting a CustomFieldChoice
* [#581](https://github.com/digitalocean/netbox/issues/581) - Correct initialization of custom boolean and select fields
* [#591](https://github.com/digitalocean/netbox/issues/591) - Correct display of component creation buttons in device type view

---

v1.6.1-r1 (2016-09-21)

## Improvements
* [#415](https://github.com/digitalocean/netbox/issues/415) - Add an expand/collapse toggle button to the prefix list
* [#552](https://github.com/digitalocean/netbox/issues/552) - Allow filtering on custom select fields by "none"
* [#561](https://github.com/digitalocean/netbox/issues/561) - Make custom fields accessible from within export templates

## Bug Fixes
* [#493](https://github.com/digitalocean/netbox/issues/493) - CSV import support for UTF-8
* [#531](https://github.com/digitalocean/netbox/issues/531) - Order prefix list by VRF assignment
* [#542](https://github.com/digitalocean/netbox/issues/542) - Add LDAP support in Docker
* [#557](https://github.com/digitalocean/netbox/issues/557) - Add 'global' choice to VRF filter for prefixes and IP addresses
* [#558](https://github.com/digitalocean/netbox/issues/558) - Update slug field when name is populated without a key press
* [#562](https://github.com/digitalocean/netbox/issues/562) - Fixed bulk interface creation
* [#564](https://github.com/digitalocean/netbox/issues/564) - Display custom fields for all applicable objects

---

v1.6.0 (2016-09-13)

## New Features

### Custom Fields ([#129](https://github.com/digitalocean/netbox/issues/129))

Users can now create custom fields to associate arbitrary data with core NetBox objects. For example, you might want to add a geolocation tag to IP prefixes, or a ticket number to each device. Text, integer, boolean, date, URL, and selection fields are supported.

## Improvements

* [#489](https://github.com/digitalocean/netbox/issues/489) - Docker file now builds from a `python:2.7-wheezy` base instead of `ubuntu:14.04`
* [#540](https://github.com/digitalocean/netbox/issues/540) - Add links for VLAN roles under VLAN navigation menu
* Added new interface form factors
* Added address family filters to aggregate and prefix lists

## Bug Fixes

* [#476](https://github.com/digitalocean/netbox/issues/476) - Corrected rack import instructions
* [#484](https://github.com/digitalocean/netbox/issues/484) - Allow bulk deletion of >1K objects
* [#486](https://github.com/digitalocean/netbox/issues/486) - Prompt for secret key only if updating a secret's value
* [#490](https://github.com/digitalocean/netbox/issues/490) - Corrected display of circuit commit rate
* [#495](https://github.com/digitalocean/netbox/issues/495) - Include tenant in prefix and IP CSV export
* [#507](https://github.com/digitalocean/netbox/issues/507) - Corrected rendering of nav menu on screens narrower than 1200px
* [#515](https://github.com/digitalocean/netbox/issues/515) - Clarified instructions for the "face" field when importing devices
* [#522](https://github.com/digitalocean/netbox/issues/522) - Remove obsolete check for staff status when bulk deleting objects
* [#544](https://github.com/digitalocean/netbox/issues/544) - Strip CRLF-style line terminators from rendered export templates

---

v1.5.2 (2016-08-16)

## Bug Fixes

* [#460](https://github.com/digitalocean/netbox/issues/460) - Corrected ordering of IP addresses with differing prefix lengths
* [#463](https://github.com/digitalocean/netbox/issues/463) - Prevent pre-population of livesearch field with '---------'
* [#467](https://github.com/digitalocean/netbox/issues/467) - Include prefixes and IPs which inherit tenancy from their VRF in tenant stats
* [#468](https://github.com/digitalocean/netbox/issues/468) - Don't allow connected interfaces to be changed to the "virtual" form factor
* [#469](https://github.com/digitalocean/netbox/issues/469) - Added missing import buttons to list views
* [#472](https://github.com/digitalocean/netbox/issues/472) - Hide the connection button for interfaces which have a circuit terminated to them

---

v1.5.1 (2016-08-11)

## Improvements

* [#421](https://github.com/digitalocean/netbox/issues/421) - Added an asset tag field to devices
* [#456](https://github.com/digitalocean/netbox/issues/456) - Added IP search box to home page
* Colorized rack and device roles

## Bug Fixes

* [#454](https://github.com/digitalocean/netbox/issues/454) - Corrected error on rack export
* [#457](https://github.com/digitalocean/netbox/issues/457) - Added role field to rack edit form

---

v1.5.0 (2016-08-10)

## New Features

### Rack Enhancements ([#180](https://github.com/digitalocean/netbox/issues/180), [#241](https://github.com/digitalocean/netbox/issues/241))

Like devices, racks can now be assigned to functional roles. This allows users to group racks by designated function as well as by physical location (rack groups). Additionally, rack can now have a defined rail-to-rail width (19 or 23 inches) and a type (two-post-rack, cabinet, etc.).

## Improvements

* [#149](https://github.com/digitalocean/netbox/issues/149) - Added discrete upstream speed field for circuits
* [#157](https://github.com/digitalocean/netbox/issues/157) - Added manufacturer field for device modules
* We have a logo!
* Upgraded to Django 1.10

## Bug Fixes

* [#433](https://github.com/digitalocean/netbox/issues/433) - Corrected form validation when editing child devices
* [#442](https://github.com/digitalocean/netbox/issues/442) - Corrected child device import instructions
* [#443](https://github.com/digitalocean/netbox/issues/443) - Correctly display and initialize VRF for creation of new IP addresses
* [#444](https://github.com/digitalocean/netbox/issues/444) - Corrected prefix model validation
* [#445](https://github.com/digitalocean/netbox/issues/445) - Limit rack height to between 1U and 100U (inclusive)

---

v1.4.2 (2016-08-06)

## Improvements

* [#167](https://github.com/digitalocean/netbox/issues/167) - Added new interface form factors
* [#253](https://github.com/digitalocean/netbox/issues/253) - Added new interface form factors
* [#434](https://github.com/digitalocean/netbox/issues/434) - Restored admin UI access to user action history (however bulk deletion is disabled)
* [#435](https://github.com/digitalocean/netbox/issues/435) - Added an "add prefix" button to the VLAN view

## Bug Fixes

* [#425](https://github.com/digitalocean/netbox/issues/425) - Ignore leading and trailing periods when generating a slug
* [#427](https://github.com/digitalocean/netbox/issues/427) - Prevent error when duplicate IPs are present in a prefix's IP list
* [#429](https://github.com/digitalocean/netbox/issues/429) - Correct redirection of user when adding a secret to a device

---

v1.4.1 (2016-08-03)

## Improvements

* [#289](https://github.com/digitalocean/netbox/issues/289) - Annotate available ranges in prefix IP list
* [#412](https://github.com/digitalocean/netbox/issues/412) - Tenant group assignment is no longer mandatory
* [#422](https://github.com/digitalocean/netbox/issues/422) - CSV import now supports double-quoting values which contain commas

## Bug Fixes

* [#395](https://github.com/digitalocean/netbox/issues/395) - Show child prefixes from all VRFs if the parent belongs to the global table
* [#406](https://github.com/digitalocean/netbox/issues/406) - Fixed circuit list rendring when filtering on port speed or commit rate
* [#409](https://github.com/digitalocean/netbox/issues/409) - Filter IPs and prefixes by tenant slug rather than by its PK
* [#411](https://github.com/digitalocean/netbox/issues/411) - Corrected title of secret roles view
* [#419](https://github.com/digitalocean/netbox/issues/419) - Fixed a potential database performance issue when gathering tenant statistics

---

v1.4.0 (2016-08-01)

## New Features

### Multitenancy ([#16](https://github.com/digitalocean/netbox/issues/16))

NetBox now supports tenants and tenant groups. Sites, racks, devices, VRFs, prefixes, IP addresses, VLANs, and circuits can be assigned to tenants to track the allocation of these resources among customers or internal departments. If a prefix or IP address does not have a tenant assigned, it will fall back to the tenant assigned to its parent VRF (where applicable).

## Improvements

* [#176](https://github.com/digitalocean/netbox/issues/176) - Introduced seed data for new installs
* [#358](https://github.com/digitalocean/netbox/issues/358) - Improved search for all objects
* [#394](https://github.com/digitalocean/netbox/issues/394) - Improved VRF selection during bulk editing of prefixes and IP addresses
* Miscellaneous cosmetic improvements to the UI

## Bug Fixes

* [#392](https://github.com/digitalocean/netbox/issues/392) - Don't include child devices in non-racked devices table
* [#397](https://github.com/digitalocean/netbox/issues/397) - Only include child IPs which belong to the same VRF as the parent prefix

---

v1.3.2 (2016-07-26)

## Improvements

* [#292](https://github.com/digitalocean/netbox/issues/292) - Added part_number field to DeviceType
* [#363](https://github.com/digitalocean/netbox/issues/363) - Added a description field to the VLAN model
* [#374](https://github.com/digitalocean/netbox/issues/374) - Increased VLAN name length to 64 characters
* Enabled bulk deletion of interfaces from devices

## Bug Fixes

* [#359](https://github.com/digitalocean/netbox/issues/359) - Corrected the DCIM API endpoint for finding related connections
* [#370](https://github.com/digitalocean/netbox/issues/370) - Notify user when secret decryption fails
* [#381](https://github.com/digitalocean/netbox/issues/381) - Fix 'u_consumed' error on rack import
* [#384](https://github.com/digitalocean/netbox/issues/384) - Fixed description field's maximum length on IPAM bulk edit forms
* [#385](https://github.com/digitalocean/netbox/issues/385) - Fixed error when deleting a user with one or more associated UserActions

---

v1.3.1 (2016-07-21)

## Improvements

* [#258](https://github.com/digitalocean/netbox/issues/258) - Add an API endpoint to list interface connections
* [#303](https://github.com/digitalocean/netbox/issues/303) - Improved numeric ordering of sites, racks, and devices
* [#304](https://github.com/digitalocean/netbox/issues/304) - Display utilization percentage on rack list
* [#327](https://github.com/digitalocean/netbox/issues/327) - Disable rack assignment for installed child devices

## Bug Fixes

* [#331](https://github.com/digitalocean/netbox/issues/331) - Add group field to VLAN bulk edit form
* Miscellaneous improvements to Unicode handling

---

v1.3.0 (2016-07-18)

## New Features

* [#42](https://github.com/digitalocean/netbox/issues/42) - Allow assignment of VLAN on prefix import
* [#43](https://github.com/digitalocean/netbox/issues/43) - Toggling of IP space uniqueness within a VRF
* [#111](https://github.com/digitalocean/netbox/issues/111) - Introduces VLAN groups
* [#227](https://github.com/digitalocean/netbox/issues/227) - Support for bulk import of child devices

## Bug Fixes

* [#301](https://github.com/digitalocean/netbox/issues/301) - Prevent deletion of DeviceBay when installed device is deleted
* [#306](https://github.com/digitalocean/netbox/issues/306) - Fixed device import to allow an unspecified rack face
* [#307](https://github.com/digitalocean/netbox/issues/307) - Catch `RelatedObjectDoesNotExist` when an invalid device type is defined during device import
* [#308](https://github.com/digitalocean/netbox/issues/308) - Update rack assignment for all child devices when moving a parent device
* [#311](https://github.com/digitalocean/netbox/issues/311) - Fix assignment of primary_ip on IP address import
* [#317](https://github.com/digitalocean/netbox/issues/317) - Rack elevation display fix for device types greater than 42U in height
* [#320](https://github.com/digitalocean/netbox/issues/320) - Disallow import of prefixes with host masks
* [#322](https://github.com/digitalocean/netbox/issues/320) - Corrected VLAN import behavior

---

v1.2.2 (2016-07-14)

## Improvements

* [#174](https://github.com/digitalocean/netbox/issues/174) - Added search and site filter to provider list
* [#270](https://github.com/digitalocean/netbox/issues/270) - Added the ability to filter devices by rack group

## Bug Fixes

* [#115](https://github.com/digitalocean/netbox/issues/115) - Fix deprecated django.core.context_processors reference
* [#268](https://github.com/digitalocean/netbox/issues/268) - Added support for entire 32-bit ASN space
* [#282](https://github.com/digitalocean/netbox/issues/282) - De-select "all" checkbox if one or more objects are deselected
* [#290](https://github.com/digitalocean/netbox/issues/290) - Always display management interfaces for a device type (even if `is_network_device` is not set)

---

v1.2.1 (2016-07-13)

**Note:** This release introduces a new dependency ([natsort](https://pypi.python.org/pypi/natsort)). Be sure to run `upgrade.sh` if upgrading from a previous release.

## Improvements

* [#285](https://github.com/digitalocean/netbox/issues/285) - Added the ability to prefer IPv4 over IPv6 for primary device IPs

## Bug Fixes

* [#243](https://github.com/digitalocean/netbox/issues/243) - Improved ordering of device object lists
* [#271](https://github.com/digitalocean/netbox/issues/271) - Fixed primary_ip bug in secrets API
* [#274](https://github.com/digitalocean/netbox/issues/274) - Fixed primary_ip bug in DCIM admin UI
* [#275](https://github.com/digitalocean/netbox/issues/275) - Fixed bug preventing the expansion of an existing aggregate

---

v1.2.0 (2016-07-12)

## New Features

* [#73](https://github.com/digitalocean/netbox/issues/73) - Added optional persistent banner
* [#93](https://github.com/digitalocean/netbox/issues/73) - Ability to set both IPv4 and IPv6 primary IPs for devices
* [#203](https://github.com/digitalocean/netbox/issues/203) - Introduced support for LDAP

## Bug Fixes

* [#162](https://github.com/digitalocean/netbox/issues/228) - Fixed support for Unicode characters in rack/device/VLAN names
* [#228](https://github.com/digitalocean/netbox/issues/228) - Corrected conditional inclusion of device bay templates
* [#246](https://github.com/digitalocean/netbox/issues/246) - Corrected Docker build instructions
* [#260](https://github.com/digitalocean/netbox/issues/260) - Fixed error on admin UI device type list
* Miscellaneous layout improvements for mobile devices

---

v1.1.0 (2016-07-07)

## New Features

* [#107](https://github.com/digitalocean/netbox/pull/107) - Docker support
* [#91](https://github.com/digitalocean/netbox/issues/91) - Support for subdevices within a device
* [#170](https://github.com/digitalocean/netbox/pull/170) - Added MAC address field to interfaces

## Bug Fixes

* [#169](https://github.com/digitalocean/netbox/issues/169) - Fix rendering of cancellation URL when editing objects
* [#183](https://github.com/digitalocean/netbox/issues/183) - Ignore vi swap files
* [#209](https://github.com/digitalocean/netbox/issues/209) - Corrected error when not confirming component template deletions
* [#214](https://github.com/digitalocean/netbox/issues/214) - Fixed redundant message on bulk interface creation
* [#68](https://github.com/digitalocean/netbox/issues/68) - Improved permissions-related error reporting for secrets

---

v1.0.7-r1 (2016-07-05)

* [#199](https://github.com/digitalocean/netbox/issues/199) - Correct IP address validation

---

v1.0.7 (2016-06-30)

**Note:** If upgrading from a previous release, be sure to run ./upgrade.sh after downloading the new code.
* [#135](https://github.com/digitalocean/netbox/issues/135): Fixed display of navigation menu on mobile screens
* [#141](https://github.com/digitalocean/netbox/issues/141): Fixed rendering of "getting started" guide
* Modified upgrade.sh to use sudo for pip installations
* [#109](https://github.com/digitalocean/netbox/issues/109): Hide the navigation menu from anonymous users if login is required
* [#143](https://github.com/digitalocean/netbox/issues/143): Add help_text to Device.position
* [#136](https://github.com/digitalocean/netbox/issues/136): Prefixes which have host bits set will trigger an error instead of being silently corrected
* [#140](https://github.com/digitalocean/netbox/issues/140): Improved support for Unicode in object names

---

1.0.0 (2016-06-27)

NetBox was originally developed internally at DigitalOcean by the network development team. This release marks the debut of NetBox as an open source project.
