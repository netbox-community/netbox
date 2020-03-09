# NetBox v2.4 Release Notes

## v2.4.9 (2018-12-07)

### Enhancements

* [#2089](https://github.com/netbox-community/netbox/issues/2089) - Add SONET interface form factors
* [#2495](https://github.com/netbox-community/netbox/issues/2495) - Enable deep-merging of config context data
* [#2597](https://github.com/netbox-community/netbox/issues/2597) - Add FibreChannel SFP28 (32GFC) interface form factor

### Bug Fixes

* [#2400](https://github.com/netbox-community/netbox/issues/2400) - Correct representation of nested object assignment in API docs
* [#2576](https://github.com/netbox-community/netbox/issues/2576) - Correct type for count_* fields in site API representation
* [#2606](https://github.com/netbox-community/netbox/issues/2606) - Fixed filtering for interfaces with a virtual form factor
* [#2611](https://github.com/netbox-community/netbox/issues/2611) - Fix error handling when assigning a clustered device to a different site
* [#2613](https://github.com/netbox-community/netbox/issues/2613) - Decrease live search minimum characters to three
* [#2615](https://github.com/netbox-community/netbox/issues/2615) - Tweak live search widget to use brief format for API requests
* [#2623](https://github.com/netbox-community/netbox/issues/2623) - Removed the need to pass the model class to the rqworker process for webhooks
* [#2634](https://github.com/netbox-community/netbox/issues/2634) - Enforce consistent representation of unnamed devices in rack view

---

## v2.4.8 (2018-11-20)

### Enhancements

* [#2490](https://github.com/netbox-community/netbox/issues/2490) - Added bulk editing for config contexts
* [#2557](https://github.com/netbox-community/netbox/issues/2557) - Added object view for tags

### Bug Fixes

* [#2473](https://github.com/netbox-community/netbox/issues/2473) - Fix encoding of long (>127 character) secrets
* [#2558](https://github.com/netbox-community/netbox/issues/2558) - Filter on all tags when multiple are passed
* [#2565](https://github.com/netbox-community/netbox/issues/2565) - Improved rendering of Markdown tables
* [#2575](https://github.com/netbox-community/netbox/issues/2575) - Correct model specified for rack roles table
* [#2588](https://github.com/netbox-community/netbox/issues/2588) - Catch all exceptions from failed NAPALM API Calls
* [#2589](https://github.com/netbox-community/netbox/issues/2589) - Virtual machine API serializer should require cluster assignment

---

## v2.4.7 (2018-11-06)

### Enhancements

* [#2388](https://github.com/netbox-community/netbox/issues/2388) - Enable filtering of devices/VMs by region
* [#2427](https://github.com/netbox-community/netbox/issues/2427) - Allow filtering of interfaces by assigned VLAN or VLAN ID
* [#2512](https://github.com/netbox-community/netbox/issues/2512) - Add device field to inventory item filter form

### Bug Fixes

* [#2502](https://github.com/netbox-community/netbox/issues/2502) - Allow duplicate VIPs inside a uniqueness-enforced VRF
* [#2514](https://github.com/netbox-community/netbox/issues/2514) - Prevent new connections to already connected interfaces
* [#2515](https://github.com/netbox-community/netbox/issues/2515) - Only use django-rq admin tmeplate if webhooks are enabled
* [#2528](https://github.com/netbox-community/netbox/issues/2528) - Enable creating circuit terminations with interface assignment via API
* [#2549](https://github.com/netbox-community/netbox/issues/2549) - Changed naming of `peer_device` and `peer_interface` on API /dcim/connected-device/ endpoint to use underscores

---

## v2.4.6 (2018-10-05)

### Enhancements

* [#2479](https://github.com/netbox-community/netbox/issues/2479) - Add user permissions for creating/modifying API tokens
* [#2487](https://github.com/netbox-community/netbox/issues/2487) - Return abbreviated API output when passed `?brief=1`

### Bug Fixes

* [#2393](https://github.com/netbox-community/netbox/issues/2393) - Fix Unicode support for CSV import under Python 2
* [#2483](https://github.com/netbox-community/netbox/issues/2483) - Set max item count of API-populated form fields to MAX_PAGE_SIZE
* [#2484](https://github.com/netbox-community/netbox/issues/2484) - Local config context not available on the Virtual Machine Edit Form
* [#2485](https://github.com/netbox-community/netbox/issues/2485) - Fix cancel button when assigning a service to a device/VM
* [#2491](https://github.com/netbox-community/netbox/issues/2491) - Fix exception when importing devices with invalid device type
* [#2492](https://github.com/netbox-community/netbox/issues/2492) - Sanitize hostname and port values returned through LLDP

---

## v2.4.5 (2018-10-02)

### Enhancements

* [#2392](https://github.com/netbox-community/netbox/issues/2392) - Implemented local context data for devices and virtual machines
* [#2402](https://github.com/netbox-community/netbox/issues/2402) - Order and format JSON data in form fields
* [#2432](https://github.com/netbox-community/netbox/issues/2432) - Link remote interface connections to the Interface view
* [#2438](https://github.com/netbox-community/netbox/issues/2438) - API optimizations for tagged objects

### Bug Fixes

* [#2406](https://github.com/netbox-community/netbox/issues/2406) - Remove hard-coded limit of 1000 objects from API-populated form fields
* [#2414](https://github.com/netbox-community/netbox/issues/2414) - Tags field missing from device/VM component creation forms
* [#2442](https://github.com/netbox-community/netbox/issues/2442) - Nullify "next" link in API when limit=0 is passed
* [#2443](https://github.com/netbox-community/netbox/issues/2443) - Enforce JSON object format when creating config contexts
* [#2444](https://github.com/netbox-community/netbox/issues/2444) - Improve validation of interface MAC addresses
* [#2455](https://github.com/netbox-community/netbox/issues/2455) - Ignore unique address enforcement for IPs with a shared/virtual role
* [#2470](https://github.com/netbox-community/netbox/issues/2470) - Log the creation of device/VM components as object changes

---

## v2.4.4 (2018-08-22)

### Enhancements

* [#2168](https://github.com/netbox-community/netbox/issues/2168) - Added Extreme SummitStack interface form factors
* [#2356](https://github.com/netbox-community/netbox/issues/2356) - Include cluster site as read-only field in VirtualMachine serializer
* [#2362](https://github.com/netbox-community/netbox/issues/2362) - Implemented custom admin site to properly handle BASE_PATH
* [#2254](https://github.com/netbox-community/netbox/issues/2254) - Implemented searchability for Rack Groups

### Bug Fixes

* [#2353](https://github.com/netbox-community/netbox/issues/2353) - Handle `DoesNotExist` exception when deleting a device with connected interfaces
* [#2354](https://github.com/netbox-community/netbox/issues/2354) - Increased maximum MTU for interfaces to 65536 bytes
* [#2355](https://github.com/netbox-community/netbox/issues/2355) - Added item count to inventory tab on device view
* [#2368](https://github.com/netbox-community/netbox/issues/2368) - Record change in device changelog when altering cluster assignment
* [#2369](https://github.com/netbox-community/netbox/issues/2369) - Corrected time zone validation on site API serializer
* [#2370](https://github.com/netbox-community/netbox/issues/2370) - Redirect to parent device after deleting device bays
* [#2374](https://github.com/netbox-community/netbox/issues/2374) - Fix toggling display of IP addresses in virtual machine interfaces list
* [#2378](https://github.com/netbox-community/netbox/issues/2378) - Corrected "edit" link for virtual machine interfaces

---

## v2.4.3 (2018-08-09)

### Enhancements

* [#2333](https://github.com/netbox-community/netbox/issues/2333) - Added search filters for ConfigContexts

### Bug Fixes

* [#2334](https://github.com/netbox-community/netbox/issues/2334) - TypeError raised when WritableNestedSerializer receives a non-integer value
* [#2335](https://github.com/netbox-community/netbox/issues/2335) - API requires group field when creating/updating a rack
* [#2336](https://github.com/netbox-community/netbox/issues/2336) - Bulk deleting power outlets and console server ports from a device redirects to home page
* [#2337](https://github.com/netbox-community/netbox/issues/2337) - Attempting to create the next available prefix within a parent assigned to a VRF raises an AssertionError
* [#2340](https://github.com/netbox-community/netbox/issues/2340) - API requires manufacturer field when creating/updating an inventory item
* [#2342](https://github.com/netbox-community/netbox/issues/2342) - IntegrityError raised when attempting to assign an invalid IP address as the primary for a VM
* [#2344](https://github.com/netbox-community/netbox/issues/2344) - AttributeError when assigning VLANs to an interface on a device/VM not assigned to a site

---

## v2.4.2 (2018-08-08)

### Bug Fixes

* [#2318](https://github.com/netbox-community/netbox/issues/2318) - ImportError when viewing a report
* [#2319](https://github.com/netbox-community/netbox/issues/2319) - Extend ChoiceField to properly handle true/false choice keys
* [#2320](https://github.com/netbox-community/netbox/issues/2320) - TypeError when dispatching a webhook with a secret key configured
* [#2321](https://github.com/netbox-community/netbox/issues/2321) - Allow explicitly setting a null value on nullable ChoiceFields
* [#2322](https://github.com/netbox-community/netbox/issues/2322) - Webhooks firing on non-enabled event types
* [#2323](https://github.com/netbox-community/netbox/issues/2323) - DoesNotExist raised when deleting devices or virtual machines
* [#2330](https://github.com/netbox-community/netbox/issues/2330) - Incorrect tab link in VRF changelog view

---

## v2.4.1 (2018-08-07)

### Bug Fixes

* [#2303](https://github.com/netbox-community/netbox/issues/2303) - Always redirect to parent object when bulk editing/deleting components
* [#2308](https://github.com/netbox-community/netbox/issues/2308) - Custom fields panel absent from object view in UI
* [#2310](https://github.com/netbox-community/netbox/issues/2310) - False validation error on certain nested serializers
* [#2311](https://github.com/netbox-community/netbox/issues/2311) - Redirect to parent after editing interface from device/VM view
* [#2312](https://github.com/netbox-community/netbox/issues/2312) - Running a report yields a ValueError exception
* [#2314](https://github.com/netbox-community/netbox/issues/2314) - Serialized representation of object in change log does not include assigned tags

---

## v2.4.0 (2018-08-06)

### New Features

#### Webhooks ([#81](https://github.com/netbox-community/netbox/issues/81))

Webhooks enable NetBox to send a representation of an object every time one is created, updated, or deleted. Webhooks are sent from NetBox to external services via HTTP, and can be limited by object type. Services which receive a webhook can act on the data provided by NetBox to automate other tasks.

Special thanks to [John Anderson](https://github.com/lampwins) for doing the heavy lifting for this feature!

#### Tagging ([#132](https://github.com/netbox-community/netbox/issues/132))

Tags are free-form labels which can be assigned to a variety of objects in NetBox. Tags can be used to categorize and filter objects in addition to built-in and custom fields. Objects to which tags apply now include a `tags` field in the API.

#### Contextual Configuration Data ([#1349](https://github.com/netbox-community/netbox/issues/1349))

Sometimes it is desirable to associate arbitrary data with a group of devices to aid in their configuration. (For example, you might want to associate a set of syslog servers for all devices at a particular site.) Context data enables the association of arbitrary data (expressed in JSON format) to devices and virtual machines grouped by region, site, role, platform, and/or tenancy. Context data is arranged hierarchically, so that data with a higher weight can be entered to override more general lower-weight data. Multiple instances of data are automatically merged by NetBox to present a single dictionary for each object.

#### Change Logging ([#1898](https://github.com/netbox-community/netbox/issues/1898))

When an object is created, updated, or deleted, NetBox now automatically records a serialized representation of that object (similar to how it appears in the REST API) as well the event time and user account associated with the change.

### Enhancements

* [#238](https://github.com/netbox-community/netbox/issues/238) - Allow racks with the same name within a site (but in different groups)
* [#971](https://github.com/netbox-community/netbox/issues/971) - Add a view to show all VLAN IDs available within a group
* [#1673](https://github.com/netbox-community/netbox/issues/1673) - Added object/list views for services
* [#1687](https://github.com/netbox-community/netbox/issues/1687) - Enabled custom fields for services
* [#1739](https://github.com/netbox-community/netbox/issues/1739) - Enabled custom fields for secrets
* [#1794](https://github.com/netbox-community/netbox/issues/1794) - Improved POST/PATCH representation of nested objects
* [#2029](https://github.com/netbox-community/netbox/issues/2029) - Added optional NAPALM arguments to Platform model
* [#2034](https://github.com/netbox-community/netbox/issues/2034) - Include the ID when showing nested interface connections (API change)
* [#2118](https://github.com/netbox-community/netbox/issues/2118) - Added `latitude` and `longitude` fields to Site for GPS coordinates
* [#2131](https://github.com/netbox-community/netbox/issues/2131) - Added `created` and `last_updated` fields to DeviceType
* [#2157](https://github.com/netbox-community/netbox/issues/2157) - Fixed natural ordering of objects when sorted by name
* [#2225](https://github.com/netbox-community/netbox/issues/2225) - Add "view elevations" button for site rack groups

### Bug Fixes

* [#2272](https://github.com/netbox-community/netbox/issues/2272) - Allow subdevice_role to be null on DeviceTypeSerializer"
* [#2286](https://github.com/netbox-community/netbox/issues/2286) - Fixed "mark connected" button for PDU outlet connections

### API Changes

* Introduced the `/extras/config-contexts/`, `/extras/object-changes/`, and `/extras/tags/` API endpoints
* API writes now return a nested representation of related objects (rather than only a numeric ID)
* The dcim.DeviceType serializer now includes `created` and `last_updated` fields
* The dcim.Site serializer now includes `latitude` and `longitude` fields
* The ipam.Service and secrets.Secret serializers now include custom fields
* The dcim.Platform serializer now includes a free-form (JSON) `napalm_args` field

### Changes Since v2.4-beta1

#### Enhancements

* [#2229](https://github.com/netbox-community/netbox/issues/2229) - Allow mapping of ConfigContexts to tenant groups
* [#2259](https://github.com/netbox-community/netbox/issues/2259) - Add changelog tab to interface view
* [#2264](https://github.com/netbox-community/netbox/issues/2264) - Added "map it" link for site GPS coordinates

#### Bug Fixes

* [#2137](https://github.com/netbox-community/netbox/issues/2137) - Fixed JSON serialization of dates
* [#2258](https://github.com/netbox-community/netbox/issues/2258) - Include changed object type on home page changelog
* [#2265](https://github.com/netbox-community/netbox/issues/2265) - Include parent regions when filtering applicable ConfigContexts
* [#2288](https://github.com/netbox-community/netbox/issues/2288) - Fix exception when assigning objects to a ConfigContext via the API
* [#2296](https://github.com/netbox-community/netbox/issues/2296) - Fix AttributeError when creating a new object with tags assigned
* [#2300](https://github.com/netbox-community/netbox/issues/2300) - Fix assignment of an interface to an IP address via API PATCH
* [#2301](https://github.com/netbox-community/netbox/issues/2301) - Fix model validation on assignment of ManyToMany fields via API PATCH
* [#2305](https://github.com/netbox-community/netbox/issues/2305) - Make VLAN fields optional when creating a VM interface via the API
