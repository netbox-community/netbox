# NetBox v4.2

## v4.2.9 (2025-04-30)

### Enhancements

* [#17151](https://github.com/netbox-community/netbox/issues/17151) - Display circuit type with background color in circuits list
* [#17319](https://github.com/netbox-community/netbox/issues/17319) - Improve layout of component template edit forms
* [#17405](https://github.com/netbox-community/netbox/issues/17405) - Display plugin icons in plugins list
* [#18215](https://github.com/netbox-community/netbox/issues/18215) - Link to script results list from script history
* [#18334](https://github.com/netbox-community/netbox/issues/18334) - Add region, site group, site, location, and rack filters for modules
* [#18982](https://github.com/netbox-community/netbox/issues/18982) - Reference rack as related object in changelog records for rack reservations
* [#18989](https://github.com/netbox-community/netbox/issues/18989) - List virtual circuits under provider view
* [#19110](https://github.com/netbox-community/netbox/issues/19110) - Enable filtering devices and virtual machines by primary IP address
* [#19358](https://github.com/netbox-community/netbox/issues/19358) - Move release info from footer to the navigation menu

### Bug Fixes

* [#15739](https://github.com/netbox-community/netbox/issues/15739) - Account for parallel cables when calculating total path length
* [#15971](https://github.com/netbox-community/netbox/issues/15971) - Preserve "none" selection in filter form fields
* [#16238](https://github.com/netbox-community/netbox/issues/16238) - Fix styling for white, gray, and black custom link buttons
* [#17613](https://github.com/netbox-community/netbox/issues/17613) - Fix layout of object view content on mobile
* [#17676](https://github.com/netbox-community/netbox/issues/17676) - Fix support for module bay creation when bulk importing module types
* [#18706](https://github.com/netbox-community/netbox/issues/18706) - Fix validation for VLANs assigned to both a group and a site
* [#18717](https://github.com/netbox-community/netbox/issues/18717) - Ensure change logs populated for many-to-one changes
* [#19117](https://github.com/netbox-community/netbox/issues/19117) - Avoid `AttributeError` exception when bulk import objects which have a multi-object custom field with a default value
* [#19204](https://github.com/netbox-community/netbox/issues/19204) - Improve JSON serialization support for data returned by a custom script
* [#19217](https://github.com/netbox-community/netbox/issues/19217) - Ensure static assets for the debug toolbar are installed even if `DEBUG` is false
* [#19228](https://github.com/netbox-community/netbox/issues/19228) - Fix ordering of custom scripts to avoid `NoReverseMatch` exception
* [#19229](https://github.com/netbox-community/netbox/issues/19229) - Fix `ValueError` exception when attempting to nullify interface mode when a VLAN is assigned
* [#19275](https://github.com/netbox-community/netbox/issues/19275) - `type` field should not be required when bulk editing interfaces
* [#19279](https://github.com/netbox-community/netbox/issues/19279) - `status` field should not be required when bulk editing inventory items
* [#19281](https://github.com/netbox-community/netbox/issues/19281) - Fix form validation failure when attempting to create a service from a service template
* [#19320](https://github.com/netbox-community/netbox/issues/19320) - Include Q-in-Q VLAN (if any) in VM interface details
* [#19322](https://github.com/netbox-community/netbox/issues/19322) - Correct URL paths for bulk import views
* [#19346](https://github.com/netbox-community/netbox/issues/19346) - Ensure all redirect URLs are validated before use

---

## v4.2.8 (2025-04-22)

### Enhancements

* [#17136](https://github.com/netbox-community/netbox/issues/17136) - Introduce the `--readonly` flag on upgrade script
* [#17908](https://github.com/netbox-community/netbox/issues/17908) - Add trace buttons to terminations under cable view
* [#18879](https://github.com/netbox-community/netbox/issues/18879) - Enable filtering prefixes by group of assigned VLAN
* [#18976](https://github.com/netbox-community/netbox/issues/18976) - Include FHRP group name on interface lists
* [#18978](https://github.com/netbox-community/netbox/issues/18978) - Add 802.1Q mode to interface filter form
* [#19038](https://github.com/netbox-community/netbox/issues/19038) - Show count of related VLAN groups under cluster view
* [#19040](https://github.com/netbox-community/netbox/issues/19040) - Add "copy to clipboard" button for rendered config
* [#19056](https://github.com/netbox-community/netbox/issues/19056) - Enable filtering devices by location slug
* [#19196](https://github.com/netbox-community/netbox/issues/19196) - Add filtering by VLAN translation policy to interface filter forms

### Bug Fixes

* [#18500](https://github.com/netbox-community/netbox/issues/18500) - `prepare_cloned_fields()` should validate cloning support on model
* [#18669](https://github.com/netbox-community/netbox/issues/18669) - Ensure default custom field values are respected when creating objects via the REST API
* [#18881](https://github.com/netbox-community/netbox/issues/18881) - Include missing related object counts under certain views
* [#18955](https://github.com/netbox-community/netbox/issues/18955) - Omit "clear" button on required choice fields
* [#18959](https://github.com/netbox-community/netbox/issues/18959) - Preserve ordering of terminations in cable traces
* [#18961](https://github.com/netbox-community/netbox/issues/18961) - Virtual chassis form should exclude members of other VCs when adding members
* [#19166](https://github.com/netbox-community/netbox/issues/19166) - Fix custom field choices bulk import support for `base_choices`
* [#19189](https://github.com/netbox-community/netbox/issues/19189) - The `load_yaml()` convenience method on BaseScript should use SafeLoader
* [#19195](https://github.com/netbox-community/netbox/issues/19195) - Language cookie should respect `SESSION_COOKIE_SECURE` value
* [#19230](https://github.com/netbox-community/netbox/issues/19230) - Allow label reuse when creating multiple components from a pattern
* [#19268](https://github.com/netbox-community/netbox/issues/19268) - Restore editing conflict protection for several object forms

---

## v4.2.7 (2025-04-10)

### Enhancements

* [#16144](https://github.com/netbox-community/netbox/issues/16144) - Add support for plugin models to GetReturnURLMixin
* [#18138](https://github.com/netbox-community/netbox/issues/18138) - Enable filtering of ObjectVar and MultiObjectVar input selections for custom fields
* [#18656](https://github.com/netbox-community/netbox/issues/18656) - Enable FHRP group assignment when bulk importing IP addresses
* [#18980](https://github.com/netbox-community/netbox/issues/18980) - Optimize bulk updates of custom field values when custom fields are added/removed
* [#19018](https://github.com/netbox-community/netbox/issues/19018) - Add MoCA interface type

### Bug Fixes

* [#18553](https://github.com/netbox-community/netbox/issues/18553) - Avoid clearing site of assigned virtual machines when editing a cluster
* [#18738](https://github.com/netbox-community/netbox/issues/18738) - Respect declared ordering of custom scripts within a module
* [#18895](https://github.com/netbox-community/netbox/issues/18895) - Fix GraphQL support for interfaces which terminate virtual circuits
* [#18904](https://github.com/netbox-community/netbox/issues/18904) - Add missing tags column to config contexts table
* [#18964](https://github.com/netbox-community/netbox/issues/18964) - Fix "select all" behavior on object lists
* [#18965](https://github.com/netbox-community/netbox/issues/18965) - "Run script" button should respect default commit toggle for custom scripts
* [#18991](https://github.com/netbox-community/netbox/issues/18991) - Fix cable path tracing for pass-through ports in REST API
* [#18999](https://github.com/netbox-community/netbox/issues/18999) - Fix filtering of inventory items with no manufacturer in GraphQL API
* [#19021](https://github.com/netbox-community/netbox/issues/19021) - Preserve JSONField stylign when `help_text` is passed
* [#19023](https://github.com/netbox-community/netbox/issues/19023) - `get_field_value()` should honor null values on bound form fields
* [#19030](https://github.com/netbox-community/netbox/issues/19030) - Prevent pagination buttons from overlapping bulk action buttons on object lists
* [#19041](https://github.com/netbox-community/netbox/issues/19041) - Fix `IndexError` exception when creating multiple front ports with a label
* [#19092](https://github.com/netbox-community/netbox/issues/19092) - Fix clearing of scope field when bulk editing prefixes
* [#19122](https://github.com/netbox-community/netbox/issues/19122) - Fix styling of server error page

---

## v4.2.6 (2025-03-21)

### Enhancements

* [#17503](https://github.com/netbox-community/netbox/issues/17503) - Add rack title above rack on rack detail view
* [#17686](https://github.com/netbox-community/netbox/issues/17686) - Add config option for disk space divisor
* [#18579](https://github.com/netbox-community/netbox/issues/18579) - Update filtersets and filter forms to include contact filters where missing
* [#18744](https://github.com/netbox-community/netbox/issues/18744) - Ensure contact link in tables is hyperlinked
* [#18816](https://github.com/netbox-community/netbox/issues/18816) - Add FC/UPC, FC/APC and FC/PC port types
* [#18880](https://github.com/netbox-community/netbox/issues/18880) - Delay enqueuing background tasks until DB transaction is committed to avoid race condition
* [#18939](https://github.com/netbox-community/netbox/issues/18939) - Support site group search for ASNs

### Bug Fixes

* [#18409](https://github.com/netbox-community/netbox/issues/18409) - Eliminate N+1 issue by adding generic prefetch operation to Interface API endpoint
* [#18557](https://github.com/netbox-community/netbox/issues/18557) - Update JSONField to enclose bare string values in quotes
* [#18582](https://github.com/netbox-community/netbox/issues/18582) - Fix prefix bulk import with associated VLAN and conflicting VLAN IDs
* [#18742](https://github.com/netbox-community/netbox/issues/18742) - Ensure location list and detail views show related VLAN group information
* [#18782](https://github.com/netbox-community/netbox/issues/18782) - Ensure misconfigured object list widgets on the dashboard now degrade gracefully
* [#18833](https://github.com/netbox-community/netbox/issues/18833) - Fix inventory item bulk edit to ensure that component name and type are both validated Ensure
* [#18838](https://github.com/netbox-community/netbox/issues/18838) - Ensure that local context data correctly rejects falsy values
* [#18845](https://github.com/netbox-community/netbox/issues/18845) - Restore default sort behavior of name column on devices list view
* [#18863](https://github.com/netbox-community/netbox/issues/18863) - Exempt MPTT-based models from ordering fix introduced in #18279
* [#18869](https://github.com/netbox-community/netbox/issues/18869) - Ensure numeric conversion helper always return a clean decimal value
* [#18872](https://github.com/netbox-community/netbox/issues/18872) - Ensure that `kind` is a required field when making journal entries
* [#18884](https://github.com/netbox-community/netbox/issues/18884) - Ensure tag deserialization is handled correctly
* [#18887](https://github.com/netbox-community/netbox/issues/18887) - Allow VM interface objects to be set on prefix object-type custom field
* [#18926](https://github.com/netbox-community/netbox/issues/18926) - Fix icon displayed for GitHub authentication on login page
* [#18928](https://github.com/netbox-community/netbox/issues/18928) - Support cascading deletions when cleaning up expired changelog records
* [#18933](https://github.com/netbox-community/netbox/issues/18933) - Allow filtering VLAN groups by associated site groups
* [#18944](https://github.com/netbox-community/netbox/issues/18944) - Ensure clearing "Widget type" field when adding widgets to dashboard does not cause a "ValueError: Unregistered widget class" error
* [#18949](https://github.com/netbox-community/netbox/issues/18949) - Add missing contacts property to GraphQL types where the associated model has a connection to a contact

---

## v4.2.5 (2025-03-06)

### Enhancements

* [#17357](https://github.com/netbox-community/netbox/issues/17357) - Use VirtualChassis name as fallback for unnamed devices
* [#17542](https://github.com/netbox-community/netbox/issues/17542) - Add contact assignments to VPN tunnels
* [#17944](https://github.com/netbox-community/netbox/issues/17944) - Allow script inputs to be filtered on ObjectVar and MultiObjectVar selections
* [#18024](https://github.com/netbox-community/netbox/issues/18024) - Add permalink URL pattern to match a custom script by module and class name
* [#18141](https://github.com/netbox-community/netbox/issues/18141) - Support "Quick Add" for plugins
* [#18403](https://github.com/netbox-community/netbox/issues/18403) - Improve performance of job list views
* [#18693](https://github.com/netbox-community/netbox/issues/18693) - Support setting VLAN translation on bulk edit of interfaces
* [#18772](https://github.com/netbox-community/netbox/issues/18772) - Add "type" filter for virtual circuits
* [#18774](https://github.com/netbox-community/netbox/issues/18774) - Add tooltip preview of tag descriptions when hovering over tags

### Bug Fixes

* [#15016](https://github.com/netbox-community/netbox/issues/15016) - Prevent AssertionError when adding multiple devices "mid-span" in a cable trace
* [#15924](https://github.com/netbox-community/netbox/issues/15924) - Prevent setting tagged VLANs on interfaces with mode: tagged-all
* [#17488](https://github.com/netbox-community/netbox/issues/17488) - Ensure VLANGroup.vid_ranges shows up in API results
* [#17709](https://github.com/netbox-community/netbox/issues/17709) - Allow primary key for nested models in OpenAPI request schemas
* [#17796](https://github.com/netbox-community/netbox/issues/17796) - Fix IndexError on "Create & Add Another" operation on custom field choices
* [#18605](https://github.com/netbox-community/netbox/issues/18605) - Limit VLAN selection dropdown to choices appropriate to site
* [#18722](https://github.com/netbox-community/netbox/issues/18722) - Improve UI feedback on failed script execution
* [#18729](https://github.com/netbox-community/netbox/issues/18729) - Fix unpredictable ordering on querysets with annotations/groupings
* [#18753](https://github.com/netbox-community/netbox/issues/18753) - Prevent webhooks from being triggered on a script dry-run
* [#18758](https://github.com/netbox-community/netbox/issues/18758) - Fix FieldError when sorting by account count field in providers list
* [#18768](https://github.com/netbox-community/netbox/issues/18768) - Fix removing a secondary MAC address from an interface

---

## v4.2.4 (2025-02-21)

### Enhancements

* [#17309](https://github.com/netbox-community/netbox/issues/17309) - Omit empty counts in related object tables
* [#18277](https://github.com/netbox-community/netbox/issues/18277) - Improve multi-table inheritance in serialization of change-logged models
* [#18286](https://github.com/netbox-community/netbox/issues/18286) - Add more job duration choices
* [#18357](https://github.com/netbox-community/netbox/issues/18357) - Display author name in plugin list for locally installed plugins
* [#18408](https://github.com/netbox-community/netbox/issues/18408) - Add Paused status for virtual machines
* [#18584](https://github.com/netbox-community/netbox/issues/18584) - Add rack type column to manufacturer list

### Bug Fixes

* [#17436](https://github.com/netbox-community/netbox/issues/17436) - Fix {module} replacement in module bays
* [#18013](https://github.com/netbox-community/netbox/issues/18013) - Limit object type to selected object in change log filter
* [#18241](https://github.com/netbox-community/netbox/issues/18241) - Default logging level of custom scripts changed to INFO
* [#18247](https://github.com/netbox-community/netbox/issues/18247) - Fix visibility of disabled cable paths in dark mode
* [#18480](https://github.com/netbox-community/netbox/issues/18480) - Clean data passed to script in runscript command
* [#18555](https://github.com/netbox-community/netbox/issues/18555) - Add default get_absolute_url method to plugin models
* [#18585](https://github.com/netbox-community/netbox/issues/18585) - Fix filtering circuits by location
* [#18593](https://github.com/netbox-community/netbox/issues/18593) - Fix "Create & Add Another" IP Address workflow
* [#18594](https://github.com/netbox-community/netbox/issues/18594) - Enable sorting by ASN count on site and provider lists
* [#18619](https://github.com/netbox-community/netbox/issues/18619) - Ensure shift-click selection selects only visible list items
* [#18674](https://github.com/netbox-community/netbox/issues/18674) - Preserve form values when selecting speed on circuit termination

---

## v4.2.3 (2025-02-04)

### Enhancements

* [#18518](https://github.com/netbox-community/netbox/issues/18518) - Add a "hostname" `<meta>` tag to the page header

### Bug Fixes

* [#18497](https://github.com/netbox-community/netbox/issues/18497) - Fix unhandled `FieldDoesNotExist` exception when search results include virtual circuit
* [#18433](https://github.com/netbox-community/netbox/issues/18433) - Fix MAC address not shown as "primary for interface" in MAC address detail view
* [#18154](https://github.com/netbox-community/netbox/issues/18154) - Allow anonymous users to change default table preferences
* [#18515](https://github.com/netbox-community/netbox/issues/18515) - Fix Django `collectstatic` management command in debug mode with Redis not running
* [#18456](https://github.com/netbox-community/netbox/issues/18456) - Avoid duplicate MAC Address column in interface tables
* [#18447](https://github.com/netbox-community/netbox/issues/18447) - Fix `FieldError` exception when sorting interface tables on MAC Address columns 
* [#18438](https://github.com/netbox-community/netbox/issues/18438) - Improve performance in IPAM migration `0072_prefix_cached_relations` when upgrading from v4.1 or earlier
* [#18436](https://github.com/netbox-community/netbox/issues/18436) - Reset primary MAC address when unassigning MAC address from interface
* [#18181](https://github.com/netbox-community/netbox/issues/18181) - Fix "Create & Add Another" workflow when adding IP addresses to interfaces

---

## v4.2.2 (2025-01-17)

### Bug Fixes

* [#18336](https://github.com/netbox-community/netbox/issues/18336) - Validate new rack height against installed devices when changing a rack's type
* [#18350](https://github.com/netbox-community/netbox/issues/18350) - Fix `FieldDoesNotExist` exception when global search results include a circuit termination
* [#18353](https://github.com/netbox-community/netbox/issues/18353) - Disable fetching of plugin catalog data when `ISOLATED_DEPLOYMENT` is enabled
* [#18362](https://github.com/netbox-community/netbox/issues/18362) - Avoid transmitting census data on every worker restart
* [#18363](https://github.com/netbox-community/netbox/issues/18363) - Fix support for assigning a MAC address to an interface via the REST API
* [#18368](https://github.com/netbox-community/netbox/issues/18368) - Restore missing attributes from REST API serializer for MAC addresses (`tags`, `created`, `last_updated`, and custom fields)
* [#18369](https://github.com/netbox-community/netbox/issues/18369) - Fix `TypeError` exception when rendering the system configuration view with one or more custom classes defined under `PROTECTION_RULES`
* [#18373](https://github.com/netbox-community/netbox/issues/18373) - Fix `AttributeError` exception when attempting to assign host devices to a cluster
* [#18376](https://github.com/netbox-community/netbox/issues/18376) - Fix the display of tagged VLANs in interfaces list for Q-in-Q interfaces
* [#18379](https://github.com/netbox-community/netbox/issues/18379) - Ensure RSS feed dashboard widget content is sanitized
* [#18392](https://github.com/netbox-community/netbox/issues/18392) - Virtual machines should not inherit config contexts assigned to locations
* [#18400](https://github.com/netbox-community/netbox/issues/18400) - Fix support for `STORAGE_BACKEND` configuration parameter
* [#18406](https://github.com/netbox-community/netbox/issues/18406) - Scope column headers in object lists should not be orderable

---

## v4.2.1 (2025-01-08)

### Bug Fixes

* [#18282](https://github.com/netbox-community/netbox/issues/18282) - Fix ordering of prefixes list by assigned VLAN
* [#18314](https://github.com/netbox-community/netbox/issues/18314) - Fix KeyError exception when rendering pre-saved dashboard (`requires_internet` missing)
* [#18316](https://github.com/netbox-community/netbox/issues/18316) - Fix AttributeError exception when global search results include prefixes and/or clusters
* [#18318](https://github.com/netbox-community/netbox/issues/18318) - Correct navigation breadcrumbs for module type UI view
* [#18324](https://github.com/netbox-community/netbox/issues/18324) - Correct filtering for certain related object listings
* [#18329](https://github.com/netbox-community/netbox/issues/18329) - Address upstream bug in GraphQL API where only one primary IP address is returned within a device/VM list

---

## v4.2.0 (2025-01-06)

### Breaking Changes

* Support for the Django admin UI has been completely removed. (The Django admin UI was disabled by default in NetBox v4.0.)
* This release drops support for PostgreSQL 12. PostgreSQL 13 or later is required to run this release.
* NetBox has adopted collation-based natural ordering for many models. This may alter the order in which some objects are listed by default.
* Automatic redirects from pre-v4.1 UI views for virtual disks have been removed.
* The `site` and `provider_network` foreign key fields on `circuits.CircuitTermination` have been replaced by the `termination` generic foreign key.
* The `site` foreign key field on `ipam.Prefix` has been replaced by the `scope` generic foreign key.
* The `site` foreign key field on `virtualization.Cluster` has been replaced by the `scope` generic foreign key.
* The `circuit` foreign key field on `circuits.CircuitGroupAssignment` has been replaced by the `member` generic foreign key.
* Obsolete nested REST API serializers have been removed. These were deprecated in NetBox v4.1 under [#17143](https://github.com/netbox-community/netbox/issues/17143).

### New Features

#### Assign Multiple MAC Addresses per Interface ([#4867](https://github.com/netbox-community/netbox/issues/4867))

MAC addresses are now managed as independent objects, rather than attributes on device and VM interfaces. NetBox now supports the assignment of multiple MAC addresses per interface, and allows a primary MAC address to be designated for each.

#### Quick Add UI Widget ([#5858](https://github.com/netbox-community/netbox/issues/5858))

A new UI widget has been introduced to enable conveniently creating new related objects while creating or editing an object. For instance, it is now possible to create and assign a new device role when creating or editing a device from within the device form.

#### VLAN Translation ([#7336](https://github.com/netbox-community/netbox/issues/7336))

User can now define policies which track the translation of VLAN IDs on IEEE 802.1Q-encapsulated interfaces. Translation policies can be reused across multiple interfaces.

#### Virtual Circuits ([#13086](https://github.com/netbox-community/netbox/issues/13086))

New models have been introduced to support the documentation of virtual circuits as an extension to the physical circuit modeling already supported. This enables users to accurately reflect point-to-point or multipoint virtual circuits atop infrastructure comprising physical circuits and cables.

#### Q-in-Q Encapsulation ([#13428](https://github.com/netbox-community/netbox/issues/13428))

NetBox now supports the designation of customer VLANs (CVLANs) and service VLANs (SVLANs) to support IEEE 802.1ad/Q-in-Q encapsulation. Each interface can now have it mode designated "Q-in-Q" and be assigned an SVLAN.

### Enhancements

* [#6414](https://github.com/netbox-community/netbox/issues/6414) - Prefixes can now be scoped by region, site group, site, or location
* [#7699](https://github.com/netbox-community/netbox/issues/7699) - Virtualization clusters can now be scoped by region, site group, site, or location
* [#9604](https://github.com/netbox-community/netbox/issues/9604) - The scope of a circuit termination now include a region, site group, site, location, or provider network
* [#10711](https://github.com/netbox-community/netbox/issues/10711) - Wireless LANs can now be scoped by region, site group, site, or location
* [#11279](https://github.com/netbox-community/netbox/issues/11279) - Improved the use of natural ordering for various models throughout the application
* [#12596](https://github.com/netbox-community/netbox/issues/12596) - Extended the virtualization clusters REST API endpoint to report on allocated VM resources
* [#16547](https://github.com/netbox-community/netbox/issues/16547) - Add a geographic distance field for circuits
* [#16783](https://github.com/netbox-community/netbox/issues/16783) - Add an operational status field for inventory items
* [#17195](https://github.com/netbox-community/netbox/issues/17195) - Add a color field for power outlets

### Plugins

* [#15093](https://github.com/netbox-community/netbox/issues/15093) - Introduced the `events_pipeline` configuration parameter, which allows plugins to hook into NetBox event processing
* [#16546](https://github.com/netbox-community/netbox/issues/16546) - NetBoxModel now provides a default `get_absolute_url()` method
* [#16971](https://github.com/netbox-community/netbox/issues/16971) - Plugins can now easily register system jobs to perform background tasks
* [#17029](https://github.com/netbox-community/netbox/issues/17029) - Registering a `PluginTemplateExtension` subclass for a single model has been deprecated (replace `model` with `models`)
* [#18023](https://github.com/netbox-community/netbox/issues/18023) - Extend `register_model_view()` to handle list views

### Other Changes

* [#16136](https://github.com/netbox-community/netbox/issues/16136) - Removed support for the Django admin UI
* [#17165](https://github.com/netbox-community/netbox/issues/17165) - All obsolete nested REST API serializers have been removed
* [#17472](https://github.com/netbox-community/netbox/issues/17472) - The legacy staged changes API has been deprecated, and will be removed in Netbox v4.3
* [#17476](https://github.com/netbox-community/netbox/issues/17476) - Upgrade to Django 5.1
* [#17752](https://github.com/netbox-community/netbox/issues/17752) - Bulk object import URL paths have been renamed from `*_import` to `*_bulk_import`
* [#17761](https://github.com/netbox-community/netbox/issues/17761) - Optional choice fields now store empty values as null (rather than empty strings) in the database
* [#18093](https://github.com/netbox-community/netbox/issues/18093) - Redirects for pre-v4.1 virtual disk UI views have been removed

### REST API Changes

* Added the following endpoints:
    * `/api/circuits/virtual-circuits/`
    * `/api/circuits/virtual-circuit-terminations/`
    * `/api/dcim/mac-addresses/`
    * `/api/ipam/vlan-translation-policies/`
    * `/api/ipam/vlan-translation-rules/`
* circuits.Circuit
    * Added the optional `distance` and `distance_unit` fields
* circuits.CircuitGroupAssignment
    * Replaced the `circuit` field with `member_type` and `member_id` to support virtual circuit assignment
* circuits.CircuitTermination
    * Removed the `site` & `provider_network` fields
    * Added the `termination_type` & `termination_id` fields to facilitate termination assignment
    * Added the read-only `termination` field
* dcim.Interface
    * The `mac_address` field is now read-only
    * Added the `primary_mac_address` relation to dcim.MACAddress
    * Added the read-only `mac_addresses` list
    * Added the `qinq_svlan` relation to ipam.VLAN
    * Added the `vlan_translation_policy` relation to ipam.VLANTranslationPolicy
    * Added `mode` choice "Q-in-Q"
* dcim.InventoryItem
    * Added the optional `status` choice field
* dcim.Location
    * Added the read-only `prefix_count` field
* dcim.PowerOutlet
    * Added the optional `color` field
* dcim.Region
    * Added the read-only `prefix_count` field
* dcim.SiteGroup
    * Added the read-only `prefix_count` field
* ipam.Prefix
    * Removed the `site` field
    * Added the `scope_type` & `scope_id` fields to facilitate scope assignment
    * Added the read-only `scope` field
* ipam.VLAN
    * Added the optional `qinq_role` selection field
    * Added the `qinq_svlan` recursive relation
* virtualization.Cluster
    * Removed the `site` field
    * Added the `scope_type` & `scope_id` fields to facilitate scope assignment
    * Added the read-only `scope` field
* virtualization.Cluster
    * Added the read-only fields `allocated_vcpus`, `allocated_memory`, and `allocated_disk`
* virtualization.VMInterface
    * The `mac_address` field is now read-only
    * Added the `primary_mac_address` relation to dcim.MACAddress
    * Added the read-only `mac_addresses` list
    * Added the `qinq_svlan` relation to ipam.VLAN
    * Added the `vlan_translation_policy` relation to ipam.VLANTranslationPolicy
    * Added `mode` choice "Q-in-Q"
* wireless.WirelessLAN
    * Added the `scope_type` & `scope_id` fields to support scope assignment
    * Added the read-only `scope` field
