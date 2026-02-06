# NetBox v4.4

## v4.4.10 (2026-01-06)

### Enhancements

* [#20953](https://github.com/netbox-community/netbox/issues/20953) - Show reverse bridge relationships on interface detail pages
* [#21071](https://github.com/netbox-community/netbox/issues/21071) - Include request method & URL when displaying server errors

### Bug Fixes

* [#19506](https://github.com/netbox-community/netbox/issues/19506) - Add filter forms for component templates to ensure object selector support
* [#20044](https://github.com/netbox-community/netbox/issues/20044) - Fix dark mode support for rack elevations
* [#20320](https://github.com/netbox-community/netbox/issues/20320) - Restore support for selecting related interfaces when bulk editing device interfaces
* [#20817](https://github.com/netbox-community/netbox/issues/20817) - Re-enable sync button when disabling scheduled syncing for a data source
* [#21045](https://github.com/netbox-community/netbox/issues/21045) - Fix `ValueError` exception when saving a site with an assigned prefix
* [#21049](https://github.com/netbox-community/netbox/issues/21049) - Ignore stale custom field data when validating an object
* [#21063](https://github.com/netbox-community/netbox/issues/21063) - Check for duplicate choice values when validating a custom field choice set
* [#21064](https://github.com/netbox-community/netbox/issues/21064) - Ensures that extra choices in custom field choice sets preserve escaped colons

---

## v4.4.9 (2025-12-23)

### Enhancements

* [#20309](https://github.com/netbox-community/netbox/issues/20309) - Support ASDOT notation for ASN ranges
* [#20720](https://github.com/netbox-community/netbox/issues/20720) - Add Latvian translations
* [#20900](https://github.com/netbox-community/netbox/issues/20900) - Allow filtering custom choice fields by multiple values in the UI

### Bug Fixes

* [#17976](https://github.com/netbox-community/netbox/issues/17976) - Remove `devicetype_count` from nested manufacturer to correct OpenAPI schema
* [#20011](https://github.com/netbox-community/netbox/issues/20011) - Provide a clear message when encountering duplicate object IDs during bulk import
* [#20114](https://github.com/netbox-community/netbox/issues/20114) - Preserve `parent_bay` during device bulk import when tags are present
* [#20491](https://github.com/netbox-community/netbox/issues/20491) - Improve handling of numeric ranges in tests
* [#20873](https://github.com/netbox-community/netbox/issues/20873) - Fix `AttributeError` exception triggered by event rules associated with an object that supports file attachments
* [#20875](https://github.com/netbox-community/netbox/issues/20875) - Ensure that parent object relations are cached (for filtering) on device/module components during instantiation
* [#20876](https://github.com/netbox-community/netbox/issues/20876) - Allow editing an IP address that resides within a range marked as populated
* [#20912](https://github.com/netbox-community/netbox/issues/20912) - Fix inconsistent clearing of `module` field on ModuleBay
* [#20944](https://github.com/netbox-community/netbox/issues/20944) - Ensure cached scope is updated on child objects when a parent region/site/location is changed
* [#20948](https://github.com/netbox-community/netbox/issues/20948) - Handle the deletion of related objects with `on_delete=RESTRICT` the same as `CASCADE`
* [#20966](https://github.com/netbox-community/netbox/issues/20966) - Fix UI rendering issue when scrolling list of object types in permissions form
* [#20969](https://github.com/netbox-community/netbox/issues/20969) - Fix querying of front port templates by `rear_port_id`
* [#21011](https://github.com/netbox-community/netbox/issues/21011) - Avoid writing to the database when loading active ConfigRevision
* [#21032](https://github.com/netbox-community/netbox/issues/21032) - Avoid SQL subquery in RestrictedQuerySet where unnecessary

---

## v4.4.8 (2025-12-09)

### Enhancements

* [#20068](https://github.com/netbox-community/netbox/issues/20068) - Support the assignment of module type profile attributes via bulk import
* [#20914](https://github.com/netbox-community/netbox/issues/20914) - Enable filtering device components by tenant assigned to device

### Bug Fixes

* [#19918](https://github.com/netbox-community/netbox/issues/19918) - Fix support for `{module}` resolution of components of child modules
* [#20759](https://github.com/netbox-community/netbox/issues/20759) - Improve legibility of object types in permissions form
* [#20860](https://github.com/netbox-community/netbox/issues/20860) - Ensure user-provided changelog message is recorded when creating device components via the UI
* [#20878](https://github.com/netbox-community/netbox/issues/20878) - Use the active database connection when executing custom scripts
* [#20888](https://github.com/netbox-community/netbox/issues/20888) - Resolve warnings about non-decimal values for min/max latitude & longitude fields

---

## v4.4.7 (2025-11-25)

### Enhancements

* [#20371](https://github.com/netbox-community/netbox/issues/20371) - Add Molex Micro-Fit 2x3 for power ports & power outlets
* [#20731](https://github.com/netbox-community/netbox/issues/20731) - Enable specifying `data_source` & `data_file` when bulk import config templates
* [#20820](https://github.com/netbox-community/netbox/issues/20820) - Enable filtering of custom fields by object type
* [#20823](https://github.com/netbox-community/netbox/issues/20823) - Disallow creation of API tokens with an expiration date in the past
* [#20841](https://github.com/netbox-community/netbox/issues/20841) - Support advanced filtering for available rack types when creating/editing a rack

### Bug Fixes

* [#20134](https://github.com/netbox-community/netbox/issues/20134) - Prevent out-of-band HTMX content swaps in embedded tables
* [#20432](https://github.com/netbox-community/netbox/issues/20432) - Fix tracing of cables across multiple circuits in parallel
* [#20465](https://github.com/netbox-community/netbox/issues/20465) - Ensure that scripts are updated immediately when a new file is uploaded
* [#20638](https://github.com/netbox-community/netbox/issues/20638) - Correct OpenAPI schema for bulk create operations
* [#20649](https://github.com/netbox-community/netbox/issues/20649) - Enforce view permissions on REST API endpoint for custom scripts
* [#20740](https://github.com/netbox-community/netbox/issues/20740) - Ensure permissions constraints are enforced when executing custom scripts via the REST API
* [#20743](https://github.com/netbox-community/netbox/issues/20743) - Pass request context to custom script when triggered by an event rule
* [#20766](https://github.com/netbox-community/netbox/issues/20766) - Fix inadvertent translations on server error page
* [#20775](https://github.com/netbox-community/netbox/issues/20775) - Fix `TypeError` exception when bulk renaming unnamed devices
* [#20822](https://github.com/netbox-community/netbox/issues/20822) - Add missing `auto_sync_enabled` field in bulk edit forms
* [#20827](https://github.com/netbox-community/netbox/issues/20827) - Fix UI styling issue when toggling between light and dark mode
* [#20839](https://github.com/netbox-community/netbox/issues/20839) - Fix filtering by object type in UI for custom links and saved filters
* [#20840](https://github.com/netbox-community/netbox/issues/20840) - Remove extraneous references to airflow for RackType model
* [#20844](https://github.com/netbox-community/netbox/issues/20844) - Fix object type filter for L2VPN terminations
* [#20859](https://github.com/netbox-community/netbox/issues/20859) - Prevent dashboard crash due to exception raised by a widget
* [#20865](https://github.com/netbox-community/netbox/issues/20865) - Enforce proper min/max values for latitude & longitude fields

---

## v4.4.6 (2025-11-11)

### Enhancements

* [#14171](https://github.com/netbox-community/netbox/issues/14171) - Support VLAN assignment for device & VM interfaces being bulk imported
* [#20297](https://github.com/netbox-community/netbox/issues/20297) - Introduce additional coaxial cable types

### Bug Fixes

* [#20378](https://github.com/netbox-community/netbox/issues/20378) - Prevent exception when attempting to delete a data source utilized by a custom script
* [#20645](https://github.com/netbox-community/netbox/issues/20645) - CSVChoiceField should defer to model field's default value when CSV field is empty
* [#20647](https://github.com/netbox-community/netbox/issues/20647) - Improve handling of empty strings during bulk imports
* [#20653](https://github.com/netbox-community/netbox/issues/20653) - Fix filtering of jobs by object type ID
* [#20660](https://github.com/netbox-community/netbox/issues/20660) - Optimize loading of custom script modules from remote storage
* [#20670](https://github.com/netbox-community/netbox/issues/20670) - Improve validation of related objects during bulk import
* [#20688](https://github.com/netbox-community/netbox/issues/20688) - Suppress non-harmful "No active configuration revision found" warning message
* [#20697](https://github.com/netbox-community/netbox/issues/20697) - Prevent duplication of signals which increment/decrement related object counts
* [#20699](https://github.com/netbox-community/netbox/issues/20699) - Ensure proper ordering of changelog entries resulting from cascading deletions
* [#20713](https://github.com/netbox-community/netbox/issues/20713) - Ensure a pre-change snapshot is recorded on virtual chassis members being added/removed
* [#20721](https://github.com/netbox-community/netbox/issues/20721) - Fix breadcrumb navigation links in UI for background tasks
* [#20738](https://github.com/netbox-community/netbox/issues/20738) - Deleting a virtual chassis should nullify the `vc_position` of all former members
* [#20750](https://github.com/netbox-community/netbox/issues/20750) - Fix cloning of permissions when only one action is enabled
* [#20755](https://github.com/netbox-community/netbox/issues/20755) - Prevent duplicate results under certain conditions when filtering providers
* [#20771](https://github.com/netbox-community/netbox/issues/20771) - Comments are required when creating a new journal entry
* [#20774](https://github.com/netbox-community/netbox/issues/20774) - Bulk action button labels should be translated

---

## v4.4.5 (2025-10-28)

### Enhancements

* [#19751](https://github.com/netbox-community/netbox/issues/19751) - Disable occupied module bays in form dropdowns when installing a new module
* [#20301](https://github.com/netbox-community/netbox/issues/20301) - Add a "dismiss all" option to the notifications dropdown
* [#20399](https://github.com/netbox-community/netbox/issues/20399) - Add `assigned` and `primary` boolean filters for MAC addresses
* [#20567](https://github.com/netbox-community/netbox/issues/20567) - Add contacts column to services table
* [#20675](https://github.com/netbox-community/netbox/issues/20675) - Enable [NetBox Copilot](https://netboxlabs.com/products/netbox-copilot/) integration
* [#20692](https://github.com/netbox-community/netbox/issues/20692) - Add contacts column to IP addresses table
* [#20700](https://github.com/netbox-community/netbox/issues/20700) - Add contacts table column for various additional models

### Bug Fixes

* [#19872](https://github.com/netbox-community/netbox/issues/19872) - Ensure custom script validation failures display error messages
* [#20389](https://github.com/netbox-community/netbox/issues/20389) - Fix "select all" behavior for bulk rename views
* [#20422](https://github.com/netbox-community/netbox/issues/20422) - Enable filtering of aggregates and prefixes by family in GraphQL API
* [#20459](https://github.com/netbox-community/netbox/issues/20459) - Fix validation of `is_oob` & `is_primary` fields under IP address bulk import
* [#20466](https://github.com/netbox-community/netbox/issues/20466) - Fix querying of devices with a primary IP assigned in GraphQL API
* [#20498](https://github.com/netbox-community/netbox/issues/20498) - Enforce the validation regex (if set) for custom URL fields
* [#20524](https://github.com/netbox-community/netbox/issues/20524) - Raise a validation error when attempting to schedule a custom script for a past date/time
* [#20541](https://github.com/netbox-community/netbox/issues/20541) - Fix resolution of GraphQL object fields which rely on custom filters
* [#20551](https://github.com/netbox-community/netbox/issues/20551) - Fix automatic slug generation in quick-add UI form
* [#20606](https://github.com/netbox-community/netbox/issues/20606) - Enable copying of values from table columns rendered as badges
* [#20641](https://github.com/netbox-community/netbox/issues/20641) - Fix `AttributeError` exception raised by the object changes REST API endpoint
* [#20646](https://github.com/netbox-community/netbox/issues/20646) - Prevent cables from connecting to objects marked as connected
* [#20655](https://github.com/netbox-community/netbox/issues/20655) - Fix `FieldError` exception when attempting to sort permissions list by actions

---

## v4.4.4 (2025-10-15)

### Bug Fixes

* [#20554](https://github.com/netbox-community/netbox/issues/20554) - Fix generic relation filters to accept `<app>.<model>` format matching POST requests
* [#20574](https://github.com/netbox-community/netbox/issues/20574) - Fix excessive storage initialization overhead when listing scripts with remote backends
* [#20584](https://github.com/netbox-community/netbox/issues/20584) - Enforce PoE mode requirement on interface templates when PoE type is set
* [#20585](https://github.com/netbox-community/netbox/issues/20585) - Fix API schema generation crash for models with single-field UniqueConstraints
* [#20587](https://github.com/netbox-community/netbox/issues/20587) - Fix upgrade.sh failure when removing stale content types

---

## v4.4.3 (2025-10-14)

### Enhancements

* [#20426](https://github.com/netbox-community/netbox/issues/20426) - Add a copy-to-clipboard button for custom script output
* [#20516](https://github.com/netbox-community/netbox/issues/20516) - Improve rendering of VLAN ID ranges in VLAN group tables

### Bug Fixes

* [#19302](https://github.com/netbox-community/netbox/issues/19302) - Fix uniqueness validation in REST API for nullable fields
* [#19615](https://github.com/netbox-community/netbox/issues/19615) - Fix support for static file parameters in templates when external storage is in use
* [#19818](https://github.com/netbox-community/netbox/issues/19818) - Hide primary IP assignment fields when creating a new virtual machine in the UI
* [#19825](https://github.com/netbox-community/netbox/issues/19825) - Prevent cache for config revisions from being erroneously overwritten when debugging is enabled
* [#20140](https://github.com/netbox-community/netbox/issues/20140) - Changing a site's region or group should update any associated circuit terminations
* [#20156](https://github.com/netbox-community/netbox/issues/20156) - Fix display of rack elevation labels
* [#20290](https://github.com/netbox-community/netbox/issues/20290) - Fix migration error when upgrading to NetBox v4.4 from releases earlier than v4.3
* [#20471](https://github.com/netbox-community/netbox/issues/20471) - Saving an unmodified VLAN group should not generate a change record
* [#20475](https://github.com/netbox-community/netbox/issues/20475) - Collapse singleton VLAN IDs in VLAN group display
* [#20494](https://github.com/netbox-community/netbox/issues/20494) - Correct OpenAPI schema definition for `IntegerRangeSerializer`
* [#20496](https://github.com/netbox-community/netbox/issues/20496) - REST API should always honor `MAX_PAGE_SIZE` value
* [#20497](https://github.com/netbox-community/netbox/issues/20497) - Fix filtering of VLAN groups by VLAN ID range in GraphQL API
* [#20507](https://github.com/netbox-community/netbox/issues/20507) - Fix support for fetching ASN contacts via GraphQL API
* [#20523](https://github.com/netbox-community/netbox/issues/20523) - Hide password change form for users authenticated via SSO
* [#20542](https://github.com/netbox-community/netbox/issues/20542) - Fix the creation of MAC addresses using the "quick add" form

---

## v4.4.2 (2025-09-30)

### Enhancements

* [#17010](https://github.com/netbox-community/netbox/issues/17010) - Show admin navigation menu items only for staff & superusers
* [#19590](https://github.com/netbox-community/netbox/issues/19590) - Add columns for device site & location to device component tables
* [#19765](https://github.com/netbox-community/netbox/issues/19765) - Linkify assigned object types under saved filter view
* [#20308](https://github.com/netbox-community/netbox/issues/20308) - Add a hotkey (`/`) for the global search field
* [#20332](https://github.com/netbox-community/netbox/issues/20332) - Add a "none" option to object tag filters
* [#20380](https://github.com/netbox-community/netbox/issues/20380) - Introduce the `SENTRY_CONFIG` configuration parameter
* [#20412](https://github.com/netbox-community/netbox/issues/20412) - Linkify cluster type on virtual machine detail view
* [#20438](https://github.com/netbox-community/netbox/issues/20438) - Add `facility` field to bulk edit forms for sites and locations

### Bug Fixes

* [#18878](https://github.com/netbox-community/netbox/issues/18878) - Automatically assign a designated primary MAC address upon creation of a new interface
* [#20243](https://github.com/netbox-community/netbox/issues/20243) - Prevent scheduled system jobs from re-running multiple times
* [#20253](https://github.com/netbox-community/netbox/issues/20253) - Fix support for filtering object contact assignments in GraphQL API
* [#20365](https://github.com/netbox-community/netbox/issues/20365) - Address various inaccuracies in generated OpenAPI schema
* [#20375](https://github.com/netbox-community/netbox/issues/20375) - Preserve filter parameters when performing bulk operations
* [#20390](https://github.com/netbox-community/netbox/issues/20390) - Fix styling of page size selection dropdown
* [#20392](https://github.com/netbox-community/netbox/issues/20392) - Clean up ordering of interface type options
* [#20398](https://github.com/netbox-community/netbox/issues/20398) - Fix misleading error reporting for min/max custom field values
* [#20419](https://github.com/netbox-community/netbox/issues/20419) - Correct action buttons for child object views
* [#20425](https://github.com/netbox-community/netbox/issues/20425) - Fix Markdown preview functionality within "quick add" modal
* [#20441](https://github.com/netbox-community/netbox/issues/20441) - Fix display of the "groups" column in contact assignments table 

---

## v4.4.1 (2025-09-16)

### Enhancements

* [#15492](https://github.com/netbox-community/netbox/issues/15492) - Enable cloning of permissions
* [#16381](https://github.com/netbox-community/netbox/issues/16381) - Display script result timestamps in system timezone
* [#19262](https://github.com/netbox-community/netbox/issues/19262) - No longer restrict FHRP group assignment by assigned IP address
* [#19408](https://github.com/netbox-community/netbox/issues/19408) - Support export templates for circuit terminations and virtual circuit terminations
* [#19428](https://github.com/netbox-community/netbox/issues/19428) - Add an optional U height field to the devices table
* [#19547](https://github.com/netbox-community/netbox/issues/19547) - Add individual "sync" buttons in data sources table
* [#19865](https://github.com/netbox-community/netbox/issues/19865) - Reorganize cable type groupings
* [#20222](https://github.com/netbox-community/netbox/issues/20222) - Enable the `HttpOnly` flag for CSRF cookie
* [#20237](https://github.com/netbox-community/netbox/issues/20237) - Include VPN tunnel groups in global search results
* [#20241](https://github.com/netbox-community/netbox/issues/20241) - Record A & B terminations in cable changelog data
* [#20277](https://github.com/netbox-community/netbox/issues/20277) - Add support for attribute assignment to `deserialize_object()` utility
* [#20321](https://github.com/netbox-community/netbox/issues/20321) - Add physical media types for transceiver interfaces
* [#20347](https://github.com/netbox-community/netbox/issues/20347) - Add Wi-Fi Alliance aliases to 802.11 interface types

### Bug Fixes

* [#19729](https://github.com/netbox-community/netbox/issues/19729) - Restore `kind` filter for interfaces in GraphQL API
* [#19744](https://github.com/netbox-community/netbox/issues/19744) - Plugins list should be orderable by "active" column
* [#19851](https://github.com/netbox-community/netbox/issues/19851) - Fix `ValueError` complaining of missing `scope` when bulk importing wireless LANs
* [#19896](https://github.com/netbox-community/netbox/issues/19896) - Min/max values for decimal custom fields should accept decimal values
* [#20197](https://github.com/netbox-community/netbox/issues/20197) - Correct validation for virtual chassis parent interface
* [#20215](https://github.com/netbox-community/netbox/issues/20215) - All GraphQL filters for config contexts should be optional
* [#20217](https://github.com/netbox-community/netbox/issues/20217) - Remove "0 VLANs available" row at end of VLAN range table
* [#20221](https://github.com/netbox-community/netbox/issues/20221) - JSON fields should not coerce empty dictionaries to null
* [#20227](https://github.com/netbox-community/netbox/issues/20227) - Ensure consistent padding of Markdown content
* [#20234](https://github.com/netbox-community/netbox/issues/20234) - Fix "add" button link for prerequisite object warning in UI
* [#20236](https://github.com/netbox-community/netbox/issues/20236) - Strip invalid characters from uploaded image file names
* [#20238](https://github.com/netbox-community/netbox/issues/20238) - Fix support for outside IP assignment during bulk import of tunnel terminations
* [#20242](https://github.com/netbox-community/netbox/issues/20242) - Avoid `AttributeError` exception on background jobs with no request ID
* [#20252](https://github.com/netbox-community/netbox/issues/20252) - Remove generic AddObject from ObjectChildrenView to prevent duplicate "add" buttons
* [#20264](https://github.com/netbox-community/netbox/issues/20264) - Fix rendering of default icon in plugins list
* [#20272](https://github.com/netbox-community/netbox/issues/20272) - ConfigContexts assigned to ancestor locations should apply to device/VM
* [#20282](https://github.com/netbox-community/netbox/issues/20282) - Fix styling of prerequisite objects warning
* [#20298](https://github.com/netbox-community/netbox/issues/20298) - Display a placeholder when an image thumbnail fails to load
* [#20327](https://github.com/netbox-community/netbox/issues/20327) - Avoid calling `distinct()` on device/VM queryset when fetching config context data

---

## v4.4.0 (2025-09-02)

### New Features

#### Background Jobs for Bulk Operations ([#19589](https://github.com/netbox-community/netbox/issues/19589), [#19891](https://github.com/netbox-community/netbox/issues/19891))

Most bulk operations, such as the import, modification, or deletion of objects can now be executed as a background job. This frees the user to continue working in NetBox while the bulk operation is processed. Once completed, the user will be notified of the job's result.

#### Logging Mechanism for Background Jobs ([#19816](https://github.com/netbox-community/netbox/issues/19816))

A dedicated logging mechanism has been implemented for background jobs. Jobs can now easily record log messages by calling e.g. `self.logger.info("Log message")` under the `run()` method. These messages are displayed along with the job's resulting data. Supported log levels include `DEBUG`, `INFO`, `WARNING`, and `ERROR`.

#### Changelog Comments ([#19713](https://github.com/netbox-community/netbox/issues/19713))

When creating, editing, or deleting objects in NetBox, users now have the option of providing a short message explaining the change. This message will be recorded on the resulting changelog records for all affected objects.

#### Config Context Data Validation ([#19377](https://github.com/netbox-community/netbox/issues/19377))

A new ConfigContextProfile model has been introduced to support JSON schema validation for config context data. If a validation schema has been defined for a profile, all config contexts assigned to it will have their data validated against the schema whenever a change is made. (The assignment of a config context to a profile is optional.)

### Enhancements

* [#17413](https://github.com/netbox-community/netbox/issues/17413) - Platforms belonging to different manufacturers may now have identical names
* [#18204](https://github.com/netbox-community/netbox/issues/18204) - Improved layout of the image attachments view & tables
* [#18528](https://github.com/netbox-community/netbox/issues/18528) - Introduced the `HOSTNAME` configuration parameter to override the system hostname reported by NetBox
* [#18984](https://github.com/netbox-community/netbox/issues/18984) - Added a `status` field for rack reservations
* [#18990](https://github.com/netbox-community/netbox/issues/18990) - Image attachments now include an optional description field
* [#19134](https://github.com/netbox-community/netbox/issues/19134) - Interface transmit power now accepts negative values
* [#19231](https://github.com/netbox-community/netbox/issues/19231) - Bulk renaming support has been implemented in the UI for most object types
* [#19591](https://github.com/netbox-community/netbox/issues/19591) - Thumbnails for all images attached to an object are now displayed under a dedicated tab
* [#19722](https://github.com/netbox-community/netbox/issues/19722) - The REST API endpoint for object types has been extended to include additional details
* [#19739](https://github.com/netbox-community/netbox/issues/19739) - Introduced a user preference for CSV delimiter
* [#19740](https://github.com/netbox-community/netbox/issues/19740) - Enable nesting of platforms within a hierarchy for improved organization
* [#19773](https://github.com/netbox-community/netbox/issues/19773) - Extend the system UI view with additional information
* [#19893](https://github.com/netbox-community/netbox/issues/19893) - The `/api/status/` REST API endpoint now includes the system hostname
* [#19920](https://github.com/netbox-community/netbox/issues/19920) - Contacts can now be assigned to ASNs
* [#19945](https://github.com/netbox-community/netbox/issues/19945) - Introduce a new custom script variable to represent decimal values
* [#19965](https://github.com/netbox-community/netbox/issues/19965) - Add REST & GraphQL API request counters to the Prometheus metrics exporter
* [#20029](https://github.com/netbox-community/netbox/issues/20029) - Include complete representation of object type in webhook payload data

### Plugins

* [#18006](https://github.com/netbox-community/netbox/issues/18006) - A Javascript is now triggered when UI is toggled between light and dark mode
* [#19735](https://github.com/netbox-community/netbox/issues/19735) - Custom individual and bulk operations can now be registered under individual views using `ObjectAction`
* [#20003](https://github.com/netbox-community/netbox/issues/20003) - Enable registration of callbacks to provide supplementary webhook payload data
* [#20115](https://github.com/netbox-community/netbox/issues/20115) - Support the use of ArrayColumn for plugin tables
* [#20129](https://github.com/netbox-community/netbox/issues/20129) - Enable plugins to register custom model features

### Deprecations

* [#19738](https://github.com/netbox-community/netbox/issues/19738) - The direct assignment of VLANs to sites is now discouraged in favor of VLAN groups

### Other Changes

* [#18349](https://github.com/netbox-community/netbox/issues/18349) - The housekeeping script has been replaced with a system job
* [#18588](https://github.com/netbox-community/netbox/issues/18588) - The "Service" model has been renamed to "Application Service" for clarity (UI change only)
* [#19829](https://github.com/netbox-community/netbox/issues/19829) - The REST API endpoint for object types is now available under `/api/core/`
* [#19924](https://github.com/netbox-community/netbox/issues/19924) - ObjectTypes are now tracked as concrete objects in the database (alongside ContentTypes)
* [#19973](https://github.com/netbox-community/netbox/issues/19973) - Miscellaneous improvements to the `nbshell` management command

### REST API Changes

* All object types which support change logging now support the inclusion of a `changelog_message` for write operations. If provided, this message will be attached to the changelog record resulting from the change (if successful).
* The `/api/status/` endpoint now includes the system hostname.
* The `/api/extras/object-types/` endpoint is now available at `/api/core/object-types/`. (The original endpoint will be removed in NetBox v4.5.)
* The `/api/core/object-types/` endpoint has been expanded to include the following read-only fields:
    * `app_name`
    * `model_name`
    * `model_name_plural`
    * `is_plugin_model`
    * `rest_api_endpoint`
    * `description`
* Introduced the `/api/extras/config-context-profiles/` endpoint
* core.Job
    * Added the read-only `log_entries` array field
* dcim.Interface
    * The `tx_power` field now accepts negative values
* dcim.RackReservation
    * Added the `status` choice field
* dcim.Platform
    * Add an optional `parent` foreign key field to support nesting
* extras.ConfigContext
    * Added the optional `profile` foreign key field
* extras.ImageAttachment
    * Added an optional `description` field
