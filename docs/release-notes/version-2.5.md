# NetBox v2.5 Release Notes

## v2.5.13 (2019-05-31)

### Enhancements

* [#2813](https://github.com/netbox-community/netbox/issues/2813) - Add tenant group filters
* [#3085](https://github.com/netbox-community/netbox/issues/3085) - Catch all exceptions during export template rendering
* [#3138](https://github.com/netbox-community/netbox/issues/3138) - Add 2.5GE and 5GE interface form factors
* [#3151](https://github.com/netbox-community/netbox/issues/3151) - Add inventory item count to manufacturers list
* [#3156](https://github.com/netbox-community/netbox/issues/3156) - Add site link to rack reservations overview
* [#3183](https://github.com/netbox-community/netbox/issues/3183) - Enable bulk deletion of sites
* [#3185](https://github.com/netbox-community/netbox/issues/3185) - Improve performance for custom field access within templates
* [#3186](https://github.com/netbox-community/netbox/issues/3186) - Add interface name filter for IP addresses

### Bug Fixes

* [#3031](https://github.com/netbox-community/netbox/issues/3031) - Fixed form field population of tags with spaces
* [#3132](https://github.com/netbox-community/netbox/issues/3132) - Circuit termination missing from available cable termination types
* [#3150](https://github.com/netbox-community/netbox/issues/3150) - Fix formatting of cable length during cable trace
* [#3184](https://github.com/netbox-community/netbox/issues/3184) - Correctly display color block for white cables
* [#3190](https://github.com/netbox-community/netbox/issues/3190) - Fix custom field rendering for Jinja2 export templates
* [#3211](https://github.com/netbox-community/netbox/issues/3211) - Fix error handling when attempting to delete a protected object via API
* [#3223](https://github.com/netbox-community/netbox/issues/3223) - Fix filtering devices by "has power outlets"
* [#3227](https://github.com/netbox-community/netbox/issues/3227) - Fix exception when deleting a circuit with a termination(s)
* [#3228](https://github.com/netbox-community/netbox/issues/3228) - Fixed login link retaining query parameters

---

## v2.5.12 (2019-05-01)

### Bug Fixes

* [#3127](https://github.com/netbox-community/netbox/issues/3127) - Fix natural ordering of device components

---

2.5.11 (2019-04-29)

### Notes

This release upgrades the Django framework to version 2.2.

### Enhancements

* [#2986](https://github.com/netbox-community/netbox/issues/2986) - Improve natural ordering of device components
* [#3023](https://github.com/netbox-community/netbox/issues/3023) - Add support for filtering cables by connected device
* [#3070](https://github.com/netbox-community/netbox/issues/3070) - Add decommissioning status for devices

### Bug Fixes

* [#2621](https://github.com/netbox-community/netbox/issues/2621) - Upgrade Django requirement to 2.2 to fix object deletion issue in the changelog middleware
* [#3072](https://github.com/netbox-community/netbox/issues/3072) - Preserve multiselect filter values when updating per-page count for list views
* [#3112](https://github.com/netbox-community/netbox/issues/3112) - Fix ordering of interface connections list by termination B name/device
* [#3116](https://github.com/netbox-community/netbox/issues/3116) - Fix `tagged_items` count in tags API endpoint
* [#3118](https://github.com/netbox-community/netbox/issues/3118) - Disable `last_login` update on login when maintenance mode is enabled

---

## v2.5.10 (2019-04-08)

### Enhancements

* [#3052](https://github.com/netbox-community/netbox/issues/3052) - Add Jinja2 support for export templates

### Bug Fixes

* [#2937](https://github.com/netbox-community/netbox/issues/2937) - Redirect to list view after editing an object from list view
* [#3036](https://github.com/netbox-community/netbox/issues/3036) - DCIM interfaces API endpoint should not include VM interfaces
* [#3039](https://github.com/netbox-community/netbox/issues/3039) - Fix exception when retrieving change object for a component template via API
* [#3041](https://github.com/netbox-community/netbox/issues/3041) - Fix form widget for bulk cable label update
* [#3044](https://github.com/netbox-community/netbox/issues/3044) - Ignore site/rack fields when connecting a new cable via device search
* [#3046](https://github.com/netbox-community/netbox/issues/3046) - Fix exception at reports API endpoint
* [#3047](https://github.com/netbox-community/netbox/issues/3047) - Fix exception when writing mac address for an interface via API

---

## v2.5.9 (2019-04-01)

### Enhancements

* [#2933](https://github.com/netbox-community/netbox/issues/2933) - Add username to outbound webhook requests
* [#3011](https://github.com/netbox-community/netbox/issues/3011) - Add SSL support for django-rq (requires django-rq v1.3.1+)
* [#3025](https://github.com/netbox-community/netbox/issues/3025) - Add request ID to outbound webhook requests (for correlating all changes part of a single request)

### Bug Fixes

* [#2207](https://github.com/netbox-community/netbox/issues/2207) - Fixes deterministic ordering of interfaces
* [#2577](https://github.com/netbox-community/netbox/issues/2577) - Clarification of wording in API regarding filtering
* [#2924](https://github.com/netbox-community/netbox/issues/2924) - Add interface type for QSFP28 50GE
* [#2936](https://github.com/netbox-community/netbox/issues/2936) - Fix device role selection showing duplicate first entry
* [#2998](https://github.com/netbox-community/netbox/issues/2998) - Limit device query to non-racked devices if no rack selected when creating a cable
* [#3001](https://github.com/netbox-community/netbox/issues/3001) - Fix API representation of ObjectChange `action` and add `changed_object_type`
* [#3014](https://github.com/netbox-community/netbox/issues/3014) - Fixes VM Role filtering
* [#3019](https://github.com/netbox-community/netbox/issues/3019) - Fix tag population when running NetBox within a path
* [#3022](https://github.com/netbox-community/netbox/issues/3022) - Add missing cable termination types to DCIM `_choices` endpoint
* [#3026](https://github.com/netbox-community/netbox/issues/3026) - Tweak prefix/IP filter forms to filter using VRF ID rather than route distinguisher
* [#3027](https://github.com/netbox-community/netbox/issues/3027) - Ignore empty local context data when rendering config contexts
* [#3032](https://github.com/netbox-community/netbox/issues/3032) - Save assigned tags when creating a new secret

---

## v2.5.8 (2019-03-11)

### Enhancements

* [#2435](https://github.com/netbox-community/netbox/issues/2435) - Printer friendly CSS

### Bug Fixes

* [#2065](https://github.com/netbox-community/netbox/issues/2065) - Correct documentation for VM interface serializer
* [#2705](https://github.com/netbox-community/netbox/issues/2705) - Fix endpoint grouping in API docs
* [#2781](https://github.com/netbox-community/netbox/issues/2781) - Fix filtering of sites/devices/VMs by multiple regions
* [#2923](https://github.com/netbox-community/netbox/issues/2923) - Provider filter form's site field should be blank by default
* [#2938](https://github.com/netbox-community/netbox/issues/2938) - Enforce deterministic ordering of device components returned by API
* [#2939](https://github.com/netbox-community/netbox/issues/2939) - Exclude circuit terminations from API interface connections endpoint
* [#2940](https://github.com/netbox-community/netbox/issues/2940) - Allow CSV import of prefixes/IPs to VRF without an RD assigned
* [#2944](https://github.com/netbox-community/netbox/issues/2944) - Record the deletion of an IP address in the changelog of its parent interface (if any)
* [#2952](https://github.com/netbox-community/netbox/issues/2952) - Added the `slug` field to the Tenant filter for use in the API and search function
* [#2954](https://github.com/netbox-community/netbox/issues/2954) - Remove trailing slashes to fix root/template paths on Windows
* [#2961](https://github.com/netbox-community/netbox/issues/2961) - Prevent exception when exporting inventory items belonging to unnamed devices
* [#2962](https://github.com/netbox-community/netbox/issues/2962) - Increase ExportTemplate `mime_type` field length
* [#2966](https://github.com/netbox-community/netbox/issues/2966) - Accept `null` cable length_unit via API
* [#2972](https://github.com/netbox-community/netbox/issues/2972) - Improve ContentTypeField serializer to elegantly handle invalid data
* [#2976](https://github.com/netbox-community/netbox/issues/2976) - Add delete button to tag view
* [#2980](https://github.com/netbox-community/netbox/issues/2980) - Improve rendering time for API docs
* [#2982](https://github.com/netbox-community/netbox/issues/2982) - Correct CSS class assignment on color picker
* [#2984](https://github.com/netbox-community/netbox/issues/2984) - Fix logging of unlabeled cable ID on cable deletion
* [#2985](https://github.com/netbox-community/netbox/issues/2985) - Fix pagination page length for rack elevations

---

## v2.5.7 (2019-02-21)

### Enhancements

* [#2357](https://github.com/netbox-community/netbox/issues/2357) - Enable filtering of devices by rack face
* [#2638](https://github.com/netbox-community/netbox/issues/2638) - Add button to copy unlocked secret to clipboard
* [#2870](https://github.com/netbox-community/netbox/issues/2870) - Add Markdown rendering for provider NOC/admin contact fields
* [#2878](https://github.com/netbox-community/netbox/issues/2878) - Add cable types for OS1/OS2 singlemode fiber
* [#2890](https://github.com/netbox-community/netbox/issues/2890) - Add port types for APC fiber
* [#2898](https://github.com/netbox-community/netbox/issues/2898) - Enable filtering cables list by connection status
* [#2903](https://github.com/netbox-community/netbox/issues/2903) - Clarify purpose of tags field on interface edit form

### Bug Fixes

* [#2852](https://github.com/netbox-community/netbox/issues/2852) - Allow filtering devices by null rack position
* [#2884](https://github.com/netbox-community/netbox/issues/2884) - Don't display connect button for wireless interfaces
* [#2888](https://github.com/netbox-community/netbox/issues/2888) - Correct foreground color of device roles in rack elevations
* [#2893](https://github.com/netbox-community/netbox/issues/2893) - Remove duplicate display of VRF RD on IP address view
* [#2895](https://github.com/netbox-community/netbox/issues/2895) - Fix filtering of nullable character fields
* [#2901](https://github.com/netbox-community/netbox/issues/2901) - Fix ordering regions by site count
* [#2910](https://github.com/netbox-community/netbox/issues/2910) - Fix config context list and edit forms to use Select2 elements
* [#2912](https://github.com/netbox-community/netbox/issues/2912) - Cable type in filter form should be blank by default
* [#2913](https://github.com/netbox-community/netbox/issues/2913) - Fix assigned prefixes link on VRF view
* [#2914](https://github.com/netbox-community/netbox/issues/2914) - Fix empty connected circuit link on device interfaces list
* [#2915](https://github.com/netbox-community/netbox/issues/2915) - Fix bulk editing of pass-through ports

---

## v2.5.6 (2019-02-13)

### Enhancements

* [#2758](https://github.com/netbox-community/netbox/issues/2758) - Add cable trace button to pass-through ports
* [#2839](https://github.com/netbox-community/netbox/issues/2839) - Add "110 punch" type for pass-through ports
* [#2854](https://github.com/netbox-community/netbox/issues/2854) - Enable bulk editing of pass-through ports
* [#2866](https://github.com/netbox-community/netbox/issues/2866) - Add cellular interface types (GSM/CDMA/LTE)

### Bug Fixes

* [#2841](https://github.com/netbox-community/netbox/issues/2841) - Fix filtering by VRF for prefix and IP address lists
* [#2844](https://github.com/netbox-community/netbox/issues/2844) - Correct display of far cable end for pass-through ports
* [#2845](https://github.com/netbox-community/netbox/issues/2845) - Enable filtering of rack unit list by unit ID
* [#2856](https://github.com/netbox-community/netbox/issues/2856) - Fix navigation links between LAG interfaces and their members on device view
* [#2857](https://github.com/netbox-community/netbox/issues/2857) - Add `display_name` to DeviceType API serializer; fix DeviceType list for bulk device edit
* [#2862](https://github.com/netbox-community/netbox/issues/2862) - Follow return URL when connecting a cable
* [#2864](https://github.com/netbox-community/netbox/issues/2864) - Correct display of VRF name when no RD is assigned
* [#2877](https://github.com/netbox-community/netbox/issues/2877) - Fixed device role label display on light background color
* [#2880](https://github.com/netbox-community/netbox/issues/2880) - Sanitize user password if an exception is raised during login

---

## v2.5.5 (2019-01-31)

### Enhancements

* [#2805](https://github.com/netbox-community/netbox/issues/2805) - Allow null route distinguisher for VRFs
* [#2809](https://github.com/netbox-community/netbox/issues/2809) - Remove VRF child prefixes table; link to main prefixes view
* [#2825](https://github.com/netbox-community/netbox/issues/2825) - Include directly connected device for front/rear ports

### Bug Fixes

* [#2824](https://github.com/netbox-community/netbox/issues/2824) - Fix template exception when viewing rack elevations list
* [#2833](https://github.com/netbox-community/netbox/issues/2833) - Fix form widget for front port template creation
* [#2835](https://github.com/netbox-community/netbox/issues/2835) - Fix certain model filters did not support the `q` query param
* [#2837](https://github.com/netbox-community/netbox/issues/2837) - Fix select2 nullable filter fields add multiple null_option elements when paging

---

## v2.5.4 (2019-01-29)

### Enhancements

* [#2516](https://github.com/netbox-community/netbox/issues/2516) - Implemented Select2 for all Model backed selection fields
* [#2590](https://github.com/netbox-community/netbox/issues/2590) - Implemented the color picker with Select2 to show colors in the background
* [#2733](https://github.com/netbox-community/netbox/issues/2733) - Enable bulk assignment of MAC addresses to interfaces
* [#2735](https://github.com/netbox-community/netbox/issues/2735) - Implemented Select2 for all list filter form select elements
* [#2753](https://github.com/netbox-community/netbox/issues/2753) - Implemented Select2 to replace most all instances of select fields in forms
* [#2766](https://github.com/netbox-community/netbox/issues/2766) - Extend users admin table to include superuser and active fields
* [#2782](https://github.com/netbox-community/netbox/issues/2782) - Add `is_pool` field for prefix filtering
* [#2807](https://github.com/netbox-community/netbox/issues/2807) - Include device site/rack assignment in cable trace view
* [#2808](https://github.com/netbox-community/netbox/issues/2808) - Loosen version pinning for Django to allow patch releases
* [#2810](https://github.com/netbox-community/netbox/issues/2810) - Include description fields in interface connections export

### Bug Fixes

* [#2779](https://github.com/netbox-community/netbox/issues/2779) - Include "none" option when filter IP addresses by role
* [#2783](https://github.com/netbox-community/netbox/issues/2783) - Fix AttributeError exception when attempting to delete region(s)
* [#2795](https://github.com/netbox-community/netbox/issues/2795) - Fix duplicate display of pagination controls on child prefix/IP tables
* [#2798](https://github.com/netbox-community/netbox/issues/2798) - Properly URL-encode "map it" link on site view
* [#2802](https://github.com/netbox-community/netbox/issues/2802) - Better error handling for unsupported NAPALM methods
* [#2816](https://github.com/netbox-community/netbox/issues/2816) - Handle exception when deleting a device with connected components

---

## v2.5.3 (2019-01-11)

### Enhancements

* [#1630](https://github.com/netbox-community/netbox/issues/1630) - Enable bulk editing of prefix/IP mask length
* [#1870](https://github.com/netbox-community/netbox/issues/1870) - Add per-page toggle to object lists
* [#1871](https://github.com/netbox-community/netbox/issues/1871) - Enable filtering sites by parent region
* [#1983](https://github.com/netbox-community/netbox/issues/1983) - Enable regular expressions when bulk renaming device components
* [#2682](https://github.com/netbox-community/netbox/issues/2682) - Add DAC and AOC cable types
* [#2693](https://github.com/netbox-community/netbox/issues/2693) - Additional cable colors
* [#2726](https://github.com/netbox-community/netbox/issues/2726) - Include cables in global search

### Bug Fixes

* [#2742](https://github.com/netbox-community/netbox/issues/2742) - Preserve cluster assignment when editing a device
* [#2757](https://github.com/netbox-community/netbox/issues/2757) - Always treat first/last IPs within a /31 or /127 as usable
* [#2762](https://github.com/netbox-community/netbox/issues/2762) - Add missing DCIM field values to API `_choices` endpoint
* [#2777](https://github.com/netbox-community/netbox/issues/2777) - Fix cable validation to handle duplicate connections on import


---

## v2.5.2 (2018-12-21)

### Enhancements

* [#2561](https://github.com/netbox-community/netbox/issues/2561) - Add 200G and 400G interface types
* [#2701](https://github.com/netbox-community/netbox/issues/2701) - Enable filtering of prefixes by exact prefix value

### Bug Fixes

* [#2673](https://github.com/netbox-community/netbox/issues/2673) - Fix exception on LLDP neighbors view for device with a circuit connected
* [#2691](https://github.com/netbox-community/netbox/issues/2691) - Cable trace should follow circuits
* [#2698](https://github.com/netbox-community/netbox/issues/2698) - Remove pagination restriction on bulk component creation for devices/VMs
* [#2704](https://github.com/netbox-community/netbox/issues/2704) - Fix form select widget population on parent with null value
* [#2707](https://github.com/netbox-community/netbox/issues/2707) - Correct permission evaluation for circuit termination cabling
* [#2712](https://github.com/netbox-community/netbox/issues/2712) - Preserve list filtering after editing objects in bulk
* [#2717](https://github.com/netbox-community/netbox/issues/2717) - Fix bulk deletion of tags
* [#2721](https://github.com/netbox-community/netbox/issues/2721) - Detect loops when tracing front/rear ports
* [#2723](https://github.com/netbox-community/netbox/issues/2723) - Correct permission evaluation when bulk deleting tags
* [#2724](https://github.com/netbox-community/netbox/issues/2724) - Limit rear port choices to current device when editing a front port

---

## v2.5.1 (2018-12-13)

### Enhancements

* [#2655](https://github.com/netbox-community/netbox/issues/2655) - Add 128GFC Fibrechannel interface type
* [#2674](https://github.com/netbox-community/netbox/issues/2674) - Enable filtering changelog by object type under web UI

### Bug Fixes

* [#2662](https://github.com/netbox-community/netbox/issues/2662) - Fix ImproperlyConfigured exception when rendering API docs
* [#2663](https://github.com/netbox-community/netbox/issues/2663) - Prevent duplicate interfaces from appearing under VLAN members view
* [#2666](https://github.com/netbox-community/netbox/issues/2666) - Correct display of length unit in cables list
* [#2676](https://github.com/netbox-community/netbox/issues/2676) - Fix exception when passing dictionary value to a ChoiceField
* [#2678](https://github.com/netbox-community/netbox/issues/2678) - Fix error when viewing webhook in admin UI without write permission
* [#2680](https://github.com/netbox-community/netbox/issues/2680) - Disallow POST requests to `/dcim/interface-connections/` API endpoint
* [#2683](https://github.com/netbox-community/netbox/issues/2683) - Fix exception when connecting a cable to a RearPort with no corresponding FrontPort
* [#2684](https://github.com/netbox-community/netbox/issues/2684) - Fix custom field filtering
* [#2687](https://github.com/netbox-community/netbox/issues/2687) - Correct naming of before/after filters for changelog entries

---

## v2.5.0 (2018-12-10)

### Notes

#### Python 3 Required

As promised, Python 2 support has been completed removed. Python 3.5 or higher is now required to run NetBox. Please see [our Python 3 migration guide](https://netbox.readthedocs.io/en/stable/installation/migrating-to-python3/) for assistance with upgrading.

#### Removed Deprecated User Activity Log

The UserAction model, which was deprecated by the new change logging feature in NetBox v2.4, has been removed. If you need to archive legacy user activity, do so prior to upgrading to NetBox v2.5, as the database migration will remove all data associated with this model.

#### View Permissions in Django 2.1

Django 2.1 introduces view permissions for object types (not to be confused with object-level permissions). Implementation of [#323](https://github.com/netbox-community/netbox/issues/323) is planned for NetBox v2.6. Users are encourage to begin assigning view permissions as desired in preparation for their eventual enforcement.

#### upgrade.sh No Longer Invokes sudo

The `upgrade.sh` script has been tweaked so that it no longer invokes `sudo` internally. This was done to ensure compatibility when running NetBox inside a Python virtual environment. If you need elevated permissions when upgrading NetBox, call the upgrade script with `sudo upgrade.sh`.

### New Features

#### Patch Panels and Cables ([#20](https://github.com/netbox-community/netbox/issues/20))

NetBox now supports modeling physical cables for console, power, and interface connections. The new pass-through port component type has also been introduced to model patch panels and similar devices.

### Enhancements

* [#450](https://github.com/netbox-community/netbox/issues/450) - Added `outer_width` and `outer_depth` fields to rack model
* [#867](https://github.com/netbox-community/netbox/issues/867) - Added `description` field to circuit terminations
* [#1444](https://github.com/netbox-community/netbox/issues/1444) - Added an `asset_tag` field for racks
* [#1931](https://github.com/netbox-community/netbox/issues/1931) - Added a count of assigned IP addresses to the interface API serializer
* [#2000](https://github.com/netbox-community/netbox/issues/2000) - Dropped support for Python 2
* [#2053](https://github.com/netbox-community/netbox/issues/2053) - Introduced the `LOGIN_TIMEOUT` configuration setting
* [#2057](https://github.com/netbox-community/netbox/issues/2057) - Added description columns to interface connections list
* [#2104](https://github.com/netbox-community/netbox/issues/2104) - Added a `status` field for racks
* [#2165](https://github.com/netbox-community/netbox/issues/2165) - Improved natural ordering of Interfaces
* [#2292](https://github.com/netbox-community/netbox/issues/2292) - Removed the deprecated UserAction model
* [#2367](https://github.com/netbox-community/netbox/issues/2367) - Removed deprecated RPCClient functionality
* [#2426](https://github.com/netbox-community/netbox/issues/2426) - Introduced `SESSION_FILE_PATH` configuration setting for authentication without write access to database
* [#2594](https://github.com/netbox-community/netbox/issues/2594) - `upgrade.sh` no longer invokes sudo

### Changes From v2.5-beta2

* [#2474](https://github.com/netbox-community/netbox/issues/2474) - Add `cabled` and `connection_status` filters for device components
* [#2616](https://github.com/netbox-community/netbox/issues/2616) - Convert Rack `outer_unit` and Cable `length_unit` to integer-based choice fields
* [#2622](https://github.com/netbox-community/netbox/issues/2622) - Enable filtering cables by multiple types/colors
* [#2624](https://github.com/netbox-community/netbox/issues/2624) - Delete associated content type and permissions when removing InterfaceConnection model
* [#2626](https://github.com/netbox-community/netbox/issues/2626) - Remove extraneous permissions generated from proxy models
* [#2632](https://github.com/netbox-community/netbox/issues/2632) - Change representation of null values from `0` to `null`
* [#2639](https://github.com/netbox-community/netbox/issues/2639) - Fix preservation of length/dimensions unit for racks and cables
* [#2648](https://github.com/netbox-community/netbox/issues/2648) - Include the `connection_status` field in nested represenations of connectable device components
* [#2649](https://github.com/netbox-community/netbox/issues/2649) - Add `connected_endpoint_type` to connectable device component API representations

### API Changes

* The `/extras/recent-activity/` endpoint (replaced by change logging in v2.4) has been removed
* The `rpc_client` field has been removed from dcim.Platform (see #2367)
* Introduced a new API endpoint for cables at `/dcim/cables/`
* New endpoints for front and rear pass-through ports (and their templates) in parallel with existing device components
* The fields `interface_connection` on Interface and `interface` on CircuitTermination have been replaced with `connected_endpoint` and `connection_status`
* A new `cable` field has been added to console, power, and interface components and to circuit terminations
* New fields for dcim.Rack: `status`, `asset_tag`, `outer_width`, `outer_depth`, `outer_unit`
* The following boolean filters on dcim.Device and dcim.DeviceType have been renamed:
    * `is_console_server`: `console_server_ports`
    * `is_pdu`: `power_outlets`
    * `is_network_device`: `interfaces`
* The following new boolean filters have been introduced for dcim.Device and dcim.DeviceType:
    * `console_ports`
    * `power_ports`
    * `pass_through_ports`
* The field `interface_ordering` has been removed from the DeviceType serializer
* Added a `description` field to the CircuitTermination serializer
* Added `ipaddress_count` to InterfaceSerializer to show the count of assigned IP addresses for each interface
* The `available-prefixes` and `available-ips` IPAM endpoints now return an HTTP 204 response instead of HTTP 400 when no new objects can be created
* Filtering on null values now uses the string `null` instead of zero
