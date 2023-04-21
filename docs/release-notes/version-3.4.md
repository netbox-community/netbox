# NetBox v3.4

## v3.4.9 (FUTURE)

### Enhancements

* [#12205](https://github.com/netbox-community/netbox/issues/12205) - Sanitize rendered custom links to mitigate malicious links
* [#12226](https://github.com/netbox-community/netbox/issues/12226) - Enable setting user name & email values via remote authenticate headers

### Bug Fixes

* [#11383](https://github.com/netbox-community/netbox/issues/11383) - Fix ordering of global search results by object type
* [#12238](https://github.com/netbox-community/netbox/issues/12238) - Improve error message for API token IP prefix validation failures
* [#12255](https://github.com/netbox-community/netbox/issues/12255) - Restore the ability to move inventory items among devices
* [#12270](https://github.com/netbox-community/netbox/issues/12270) - Fix pre-population of list values when creating a saved filter
* [#12296](https://github.com/netbox-community/netbox/issues/12296) - Fix "mark connected" form field for bulk editing front & rear ports

---

## v3.4.8 (2023-04-12)

### Enhancements

* [#10414](https://github.com/netbox-community/netbox/issues/10414) - Enable general purpose image attachments for device types
* [#10600](https://github.com/netbox-community/netbox/issues/10600) - Allow custom object fields to reference a user or group
* [#11015](https://github.com/netbox-community/netbox/issues/11015) - Remove unit from commit rate column header in circuits table
* [#11431](https://github.com/netbox-community/netbox/issues/11431) - Disallow changing custom field type after creation
* [#11453](https://github.com/netbox-community/netbox/issues/11453) - Display a warning banner when `DEBUG` is enabled
* [#12007](https://github.com/netbox-community/netbox/issues/12007) - Enable filtering of VM Interfaces by assigned VLAN
* [#12095](https://github.com/netbox-community/netbox/issues/12095) - Specify UTF-8 encoding for default export template MIME type
* [#12207](https://github.com/netbox-community/netbox/issues/12207) - Introduce the `grant_token` permission for controlling the creation of API tokens on behalf of other users

### Bug Fixes

* [#10221](https://github.com/netbox-community/netbox/issues/10221) - Validate generic foreign key relations assigned via REST API requests
* [#11432](https://github.com/netbox-community/netbox/issues/11432) - Prevent existing components & component templates from being reassigned to different devices/device types via the REST API
* [#11454](https://github.com/netbox-community/netbox/issues/11454) - Raise validation error if generic foreign key assignment does not specify both object type and ID
* [#11746](https://github.com/netbox-community/netbox/issues/11746) - Fix cleanup of object data when deleting a custom field
* [#12011](https://github.com/netbox-community/netbox/issues/12011) - Fix KeyError exception when attempting to add module bays in bulk
* [#12040](https://github.com/netbox-community/netbox/issues/12040) - Display relevant UI tab upon bulk import validation failure
* [#12074](https://github.com/netbox-community/netbox/issues/12074) - Fix the automatic assignment of racks to devices via the REST API
* [#12084](https://github.com/netbox-community/netbox/issues/12084) - Fix exception when attempting to create a saved filter for applied filters
* [#12087](https://github.com/netbox-community/netbox/issues/12087) - Fix bulk editing of many-to-many relationships
* [#12117](https://github.com/netbox-community/netbox/issues/12117) - Hide clone button for objects with no clonable attributes
* [#12118](https://github.com/netbox-community/netbox/issues/12118) - Fix instantiation of nested inventory item templates when creating a device
* [#12184](https://github.com/netbox-community/netbox/issues/12184) - Fix filtered bulk deletion for various models
* [#12190](https://github.com/netbox-community/netbox/issues/12190) - Fix form layout for plugin textarea fields
* [#12227](https://github.com/netbox-community/netbox/issues/12227) - Fix tenant assignment on bulk import of L2VPNs

---

## v3.4.7 (2023-03-28)

### Enhancements

* [#11645](https://github.com/netbox-community/netbox/issues/11645) - Automatically set the scheduled time when executing reports/scripts at a recurring interval
* [#11833](https://github.com/netbox-community/netbox/issues/11833) - Add fieldset support for custom script forms
* [#11973](https://github.com/netbox-community/netbox/issues/11833) - Use SSID for representing wireless links, if set
* [#11977](https://github.com/netbox-community/netbox/issues/11977) - Support designating multiple backends via `REMOTE_AUTH_BACKEND` config parameter
* [#11990](https://github.com/netbox-community/netbox/issues/11990) - Improve error reporting for duplicate CSV column headings
* [#11991](https://github.com/netbox-community/netbox/issues/11991) - Enable VDC assignment during bulk import/edit of interfaces

### Bug Fixes

* [#11914](https://github.com/netbox-community/netbox/issues/11914) - Include parameters when exporting saved filters
* [#11933](https://github.com/netbox-community/netbox/issues/11933) - Fix cloning of saved filters
* [#11984](https://github.com/netbox-community/netbox/issues/11984) - Remove erroneous 802.3az PoE type
* [#11979](https://github.com/netbox-community/netbox/issues/11979) - Correct URL for tags in route targets list
* [#12008](https://github.com/netbox-community/netbox/issues/12008) - Enable cloning of export templates
* [#12029](https://github.com/netbox-community/netbox/issues/12029) - Restore missing description field on virtual chassis form
* [#12038](https://github.com/netbox-community/netbox/issues/12038) - Correct display of zero values for virtual chassis member priority
* [#12048](https://github.com/netbox-community/netbox/issues/12048) - Enable cloning of tags
* [#12058](https://github.com/netbox-community/netbox/issues/12058) - Enable cloning of config contexts

---

## v3.4.6 (2023-03-13)

### Enhancements

* [#10058](https://github.com/netbox-community/netbox/issues/10058) - Enable searching for devices/VMs by primary IP address
* [#11011](https://github.com/netbox-community/netbox/issues/11011) - Add ability to toggle visibility of virtual interfaces under device view
* [#11294](https://github.com/netbox-community/netbox/issues/11294) - Enable live preview of Markdown content
* [#11807](https://github.com/netbox-community/netbox/issues/11807) - Restore default page size when navigating between views
* [#11817](https://github.com/netbox-community/netbox/issues/11817) - Add `connected_endpoints` field to GraphQL API for cabled objects
* [#11851](https://github.com/netbox-community/netbox/issues/11851) - Include IP version in GraphQL API representations of aggregates, prefixes, and IP addresses
* [#11862](https://github.com/netbox-community/netbox/issues/11862) - Add Cisco StackWise 1T interface type
* [#11871](https://github.com/netbox-community/netbox/issues/11871) - Add IEEE 802.3az PoE type for interfaces
* [#11929](https://github.com/netbox-community/netbox/issues/11929) - Strip whitespace from CSV headers prior to validation

### Bug Fixes

* [#11470](https://github.com/netbox-community/netbox/issues/11470) - Avoid raising exception when filtering IPs by an invalid address
* [#11565](https://github.com/netbox-community/netbox/issues/11565) - Apply custom field defaults to IP address created during FHRP group creation
* [#11631](https://github.com/netbox-community/netbox/issues/11631) - Fix filtering changelog & journal entries by multiple content type IDs
* [#11758](https://github.com/netbox-community/netbox/issues/11758) - Support non-URL-safe characters in plugin menu titles
* [#11796](https://github.com/netbox-community/netbox/issues/11796) - When importing devices, restrict rack by location only if the location field is specified
* [#11819](https://github.com/netbox-community/netbox/issues/11819) - Fix filtering of cable terminations by object type
* [#11850](https://github.com/netbox-community/netbox/issues/11850) - Fix loading of CSV files containing a byte order mark
* [#11903](https://github.com/netbox-community/netbox/issues/11903) - Fix escaping of return URL values for action buttons in tables
* [#11927](https://github.com/netbox-community/netbox/issues/11927) - Correct loading of plugin resources with custom paths

---

## v3.4.5 (2023-02-21)

### Enhancements

* [#11110](https://github.com/netbox-community/netbox/issues/11110) - Add `start_address` and `end_address` filters for IP ranges
* [#11592](https://github.com/netbox-community/netbox/issues/11592) - Introduce `FILE_UPLOAD_MAX_MEMORY_SIZE` configuration parameter
* [#11685](https://github.com/netbox-community/netbox/issues/11685) - Match on containing prefixes and aggregates when querying for IP addresses using global search
* [#11787](https://github.com/netbox-community/netbox/issues/11787) - Upgrade script will automatically rebuild missing search cache

### Bug Fixes

* [#11032](https://github.com/netbox-community/netbox/issues/11032) - Fix false custom validation errors during component creation
* [#11226](https://github.com/netbox-community/netbox/issues/11226) - Ensure scripts and reports within submodules are automatically reloaded
* [#11459](https://github.com/netbox-community/netbox/issues/11459) - Enable evaluating null values in custom validation rules
* [#11473](https://github.com/netbox-community/netbox/issues/11473) - GraphQL requests specifying an invalid filter should return an empty queryset
* [#11582](https://github.com/netbox-community/netbox/issues/11582) - Ensure form validation errors are displayed when adding virtual chassis members
* [#11601](https://github.com/netbox-community/netbox/issues/11601) - Fix partial matching of start/end addresses for IP range search
* [#11683](https://github.com/netbox-community/netbox/issues/11683) - Fix CSV header attribute detection when auto-detecting import format
* [#11711](https://github.com/netbox-community/netbox/issues/11711) - Fix CSV import for multiple-object custom fields
* [#11723](https://github.com/netbox-community/netbox/issues/11723) - Circuit terminations should link to their associated circuits (rather than site or provider network)
* [#11775](https://github.com/netbox-community/netbox/issues/11775) - Skip checking for old search cache records when creating a new object
* [#11786](https://github.com/netbox-community/netbox/issues/11786) - List only applicable object types in form widget when filtering custom fields

---

## v3.4.4 (2023-02-02)

### Enhancements

* [#10762](https://github.com/netbox-community/netbox/issues/10762) - Permit selection custom fields to have only one choice
* [#11152](https://github.com/netbox-community/netbox/issues/11152) - Introduce AbortScript exception to elegantly abort scripts
* [#11554](https://github.com/netbox-community/netbox/issues/11554) - Add module types count to manufacturers list
* [#11585](https://github.com/netbox-community/netbox/issues/11585) - Add IP address filters for services
* [#11598](https://github.com/netbox-community/netbox/issues/11598) - Add buttons to easily switch between rack list and elevations views

### Bug Fixes

* [#11267](https://github.com/netbox-community/netbox/issues/11267) - Avoid catching ImportErrors when loading plugin resources
* [#11487](https://github.com/netbox-community/netbox/issues/11487) - Remove "set null" option from non-writable custom fields during bulk edit
* [#11491](https://github.com/netbox-community/netbox/issues/11491) - Show edit/delete buttons in user tokens table
* [#11528](https://github.com/netbox-community/netbox/issues/11528) - Permit import of devices using uploaded file
* [#11555](https://github.com/netbox-community/netbox/issues/11555) - Avoid inadvertent interpretation of search query as regular expression under global search (previously [#11516](https://github.com/netbox-community/netbox/issues/11516))
* [#11562](https://github.com/netbox-community/netbox/issues/11562) - Correct ordering of virtual chassis interfaces with duplicate names
* [#11574](https://github.com/netbox-community/netbox/issues/11574) - Fix exception when attempting to schedule reports/scripts
* [#11620](https://github.com/netbox-community/netbox/issues/11620) - Correct available filter choices for interface PoE type
* [#11635](https://github.com/netbox-community/netbox/issues/11635) - Pre-populate assigned VRF when following "first available IP" link from prefix view
* [#11650](https://github.com/netbox-community/netbox/issues/11650) - Display error message when attempting to create device component with duplicate name

---

## v3.4.3 (2023-01-20)

### Enhancements

* [#9996](https://github.com/netbox-community/netbox/issues/9996) - Introduce `CA_CERT_PATH` parameter to define SSL CA path for Redis servers
* [#10486](https://github.com/netbox-community/netbox/issues/10486) - Add a cable edit button for connected components in component lists
* [#11118](https://github.com/netbox-community/netbox/issues/11118) - Add L2VPN filters for VLANs and interfaces
* [#11150](https://github.com/netbox-community/netbox/issues/11150) - Add primary IPv4/v6 address filters for devices
* [#11227](https://github.com/netbox-community/netbox/issues/11227) - Add 800GE interface types
* [#11228](https://github.com/netbox-community/netbox/issues/11228) - List both devices & VMs under device role view
* [#11245](https://github.com/netbox-community/netbox/issues/11245) - Enable export templates for journal entries
* [#11371](https://github.com/netbox-community/netbox/issues/11371) - Introduce additional 100M Ethernet interface types

### Bug Fixes

* [#10201](https://github.com/netbox-community/netbox/issues/10201) - Fix AssertionError exception when removing some terminations from an existing cable
* [#11210](https://github.com/netbox-community/netbox/issues/11210) - Fix ValueError exception when attempting to bulk import cables attached to occupied terminations
* [#11340](https://github.com/netbox-community/netbox/issues/11340) - Avoid flagging cable termination changes erroneously
* [#11379](https://github.com/netbox-community/netbox/issues/11379) - Fix TypeError exception when bulk editing custom date fields
* [#11384](https://github.com/netbox-community/netbox/issues/11384) - Correct current time display on script & report forms
* [#11402](https://github.com/netbox-community/netbox/issues/11402) - Avoid LookupError exception when running scripts with commit disabled
* [#11403](https://github.com/netbox-community/netbox/issues/11403) - Fix exception when scheduling a job in the past
* [#11416](https://github.com/netbox-community/netbox/issues/11416) - Avoid AttributeError exception when deleting a cabled circuit termination
* [#11433](https://github.com/netbox-community/netbox/issues/11433) - Avoid AttributeError exception when generating API schema for views with custom schema
* [#11438](https://github.com/netbox-community/netbox/issues/11438) - Fix deletion of scheduled job using non-default queues
* [#11444](https://github.com/netbox-community/netbox/issues/11444) - Adding/removing a device from a device bay should record a pre-change snapshot on the device bay
* [#11467](https://github.com/netbox-community/netbox/issues/11467) - Correct count on interfaces tab when viewing a VC master device
* [#11483](https://github.com/netbox-community/netbox/issues/11483) - Apply configured formatting to custom date fields
* [#11488](https://github.com/netbox-community/netbox/issues/11488) - Add missing `description` fields to several REST API serializers
* [#11497](https://github.com/netbox-community/netbox/issues/11497) - Enforce `run_script` permission when executing scripts via REST API
* ~[#11516](https://github.com/netbox-community/netbox/issues/11516) - Prevent text highlight utility from interpreting match as regex~
* [#11522](https://github.com/netbox-community/netbox/issues/11522) - Correct tag links under contact & tenant list views
* [#11537](https://github.com/netbox-community/netbox/issues/11537) - Remove obsolete "Connection" column from power feeds table
* [#11544](https://github.com/netbox-community/netbox/issues/11544) - Catch ValidationError exception when filtering by invalid MAC address

---

## v3.4.2 (2023-01-03)

### Enhancements

* [#9285](https://github.com/netbox-community/netbox/issues/9285) - Enable specifying assigned component during bulk import of inventory items
* [#10700](https://github.com/netbox-community/netbox/issues/10700) - Match device name when using modules quick search
* [#11121](https://github.com/netbox-community/netbox/issues/11121) - Add VM resource totals to cluster view
* [#11156](https://github.com/netbox-community/netbox/issues/11156) - Enable selecting assigned component when editing inventory item in UI
* [#11223](https://github.com/netbox-community/netbox/issues/11223) - `reindex` management command should accept app label without model name
* [#11244](https://github.com/netbox-community/netbox/issues/11244) - Add controls for saved filters to rack elevations list
* [#11248](https://github.com/netbox-community/netbox/issues/11248) - Fix database migration when plugin with search indexer is enabled
* [#11259](https://github.com/netbox-community/netbox/issues/11259) - Add support for Redis username configuration

### Bug Fixes

* [#11280](https://github.com/netbox-community/netbox/issues/11280) - Fix errant newlines when exporting interfaces with multiple IP addresses assigned
* [#11290](https://github.com/netbox-community/netbox/issues/11290) - Correct reporting of scheduled job duration
* [#11232](https://github.com/netbox-community/netbox/issues/11232) - Enable partial & regular expression matching for non-string types in global search
* [#11342](https://github.com/netbox-community/netbox/issues/11342) - Correct cable trace URL under "connection" tab for device components
* [#11345](https://github.com/netbox-community/netbox/issues/11345) - Fix form validation for bulk import of modules

---

## v3.4.1 (2022-12-16)

### Enhancements

* [#9971](https://github.com/netbox-community/netbox/issues/9971) - Enable ordering of nested group models by name
* [#11214](https://github.com/netbox-community/netbox/issues/11214) - Introduce the `DEFAULT_LANGUAGE` configuration parameter

### Bug Fixes

* [#11175](https://github.com/netbox-community/netbox/issues/11175) - Fix cloning of fields containing special characters
* [#11178](https://github.com/netbox-community/netbox/issues/11178) - Pressing enter in quick search box should not trigger bulk operations
* [#11184](https://github.com/netbox-community/netbox/issues/11184) - Correct visualization of cable path which splits across multiple circuit terminations
* [#11185](https://github.com/netbox-community/netbox/issues/11185) - Fix TemplateSyntaxError when viewing custom script results
* [#11189](https://github.com/netbox-community/netbox/issues/11189) - Fix localization of dates & numbers
* [#11205](https://github.com/netbox-community/netbox/issues/11205) - Correct cloning behavior for recursively-nested models
* [#11206](https://github.com/netbox-community/netbox/issues/11206) - Avoid clearing assigned groups if `REMOTE_AUTH_DEFAULT_GROUPS` is invalid

---

## v3.4.0 (2022-12-14)

!!! warning "PostgreSQL 11 Required"
    NetBox v3.4 requires PostgreSQL 11 or later.

### Breaking Changes

* Device and virtual machine names are no longer case-sensitive. Attempting to create e.g. "device1" and "DEVICE1" within the same site will raise a validation error.
* The `asn`, `noc_contact`, `admin_contact`, and `portal_url` fields have been removed from the provider model. Please replicate any data remaining in these fields to the ASN and contact models introduced in NetBox v3.1 prior to upgrading.
* The `content_type` fields on the CustomLink and ExportTemplate models have been renamed to `content_types` and now support the assignment of multiple content types per object.
* Within the Python API, the `cf` property on an object with custom fields now returns deserialized values. For example, a custom field referencing an object will return the object instance rather than its numeric ID. To access the raw serialized values, reference the object's `custom_field_data` attribute instead.
* The `NetBoxModelCSVForm` class has been renamed to `NetBoxModelImportForm`. Backward compatability with the previous name has been retained for this release, but will be dropped in NetBox v3.5.

### New Features

#### New Global Search ([#10560](https://github.com/netbox-community/netbox/issues/10560))

NetBox's global search functionality has been completely overhauled and replaced by a new cache-based lookup. This new implementation provides a much faster, more intelligent search capability. Results are returned in order of precedence regardless of object type, and matching field values are highlighted in the results. Additionally, custom field values are now included in global search results (where enabled). Plugins can also register their own models with the new global search engine.

#### Virtual Device Contexts ([#7854](https://github.com/netbox-community/netbox/issues/7854))

A new model representing virtual device contexts (VDCs) has been added. VDCs are logical partitions of resources within a device that can be managed independently. A VDC is created within a device and may have device interfaces assigned to it. An interface can be allocated to any number of VDCs on its device.

#### Saved Filters ([#9623](https://github.com/netbox-community/netbox/issues/9623))

Object lists can be filtered by a variety of different fields and characteristics. Applied filters can now be saved for reuse. For example, the query string

```
?status=active&region_id=12&tenant=acme
```

can be saved and applied to future queries as

```
?filter=my-custom-filter
```

Saved filters can be kept private, or shared among NetBox users. They can be applied to both UI and REST API searches.

#### JSON/YAML Bulk Imports ([#4347](https://github.com/netbox-community/netbox/issues/4347))

NetBox's bulk import feature, which was previously limited to CSV-formatted data for most types of objects, has been extended to accept data formatted in JSON or YAML as well. This enables users to directly import objects from a variety of sources without needing to first convert data to CSV. NetBox will attempt to automatically determine the format of import data if not specified by the user.

#### Update Existing Objects via Bulk Import ([#7961](https://github.com/netbox-community/netbox/issues/7961))

NetBox's CSV-based bulk import functionality has been extended to support also modifying existing objects. When an `id` column is present in the import form, it will be used to infer the object to be modified, rather than a new object being created. All fields (columns) are optional when modifying existing objects.

#### Scheduled Reports & Scripts ([#8366](https://github.com/netbox-community/netbox/issues/8366))

Reports and custom scripts can now be scheduled for execution at a desired future time. Background scheduling is handled entirely by the existing RQ workers; there is no need to configure additional tasks to support scheduled jobs. When creating a scheduled job, the user may optionally specify an interval at which the job will run repeatedly (e.g. every 24 hours).

#### API for Staged Changes ([#10851](https://github.com/netbox-community/netbox/issues/10851))

This release introduces a new programmatic API that enables plugins and custom scripts to prepare changes in NetBox without actually committing them to the active database. To stage changes, create and activate a branch using the `checkout()` context manager. Any changes made within this context will be captured, recorded, and rolled back for future use. Once ready, a branch can be applied to the active database by calling `merge()`. 

!!! danger "Experimental Feature"
    This feature is still under active development and considered experimental in nature. Its use in production is strongly discouraged at this time.

### Enhancements

* [#815](https://github.com/netbox-community/netbox/issues/815) - Enable specifying terminations when bulk importing circuits
* [#6003](https://github.com/netbox-community/netbox/issues/6003) - Enable the inclusion of custom field values in global search
* [#7376](https://github.com/netbox-community/netbox/issues/7376) - Enable the assignment of tags during CSV import
* [#8245](https://github.com/netbox-community/netbox/issues/8245) - Enable GraphQL filtering of related objects
* [#8274](https://github.com/netbox-community/netbox/issues/8274) - Enable associating a custom link with multiple object types
* [#8485](https://github.com/netbox-community/netbox/issues/8485) - Enable journaling for all organizational models
* [#8853](https://github.com/netbox-community/netbox/issues/8853) - Introduce the `ALLOW_TOKEN_RETRIEVAL` config parameter to restrict the display of API tokens
* [#9249](https://github.com/netbox-community/netbox/issues/9249) - Device and virtual machine names are no longer case-sensitive
* [#9478](https://github.com/netbox-community/netbox/issues/9478) - Add `link_peers` field to GraphQL types for cabled objects
* [#9654](https://github.com/netbox-community/netbox/issues/9654) - Add `weight` field to racks, device types, and module types
* [#9817](https://github.com/netbox-community/netbox/issues/9817) - Add `assigned_object` field to GraphQL type for IP addresses and L2VPN terminations
* [#9832](https://github.com/netbox-community/netbox/issues/9832) - Add `mounting_depth` field to rack model
* [#9892](https://github.com/netbox-community/netbox/issues/9892) - Add optional `name` field for FHRP groups
* [#10348](https://github.com/netbox-community/netbox/issues/10348) - Add decimal custom field type
* [#10371](https://github.com/netbox-community/netbox/issues/10371) - Add `status` field for modules
* [#10545](https://github.com/netbox-community/netbox/issues/10545) - Standardize the use of `description` and `comments` fields on all primary models
* [#10556](https://github.com/netbox-community/netbox/issues/10556) - Include a `display` field in all GraphQL object types
* [#10595](https://github.com/netbox-community/netbox/issues/10595) - Add GraphQL relationships for additional generic foreign key fields
* [#10675](https://github.com/netbox-community/netbox/issues/10675) - Add `max_weight` field to track maximum load capacity for racks
* [#10698](https://github.com/netbox-community/netbox/issues/10698) - Omit app label from content type in table columns
* [#10710](https://github.com/netbox-community/netbox/issues/10710) - Add `status` field to WirelessLAN
* [#10761](https://github.com/netbox-community/netbox/issues/10761) - Enable associating an export template with multiple object types
* [#10945](https://github.com/netbox-community/netbox/issues/10945) - Enable recurring execution of scheduled reports & scripts
* [#11022](https://github.com/netbox-community/netbox/issues/11022) - Introduce `QUEUE_MAPPINGS` configuration parameter to allow customization of background task prioritization

### Bug Fixes (from v3.4-beta1)

* [#10946](https://github.com/netbox-community/netbox/issues/10946) - Fix AttributeError exception when viewing a device with a primary IP and no platform assigned
* [#10948](https://github.com/netbox-community/netbox/issues/10948) - Linkify primary IPs for VDCs
* [#10950](https://github.com/netbox-community/netbox/issues/10950) - Fix validation of VDC primary IPs
* [#10957](https://github.com/netbox-community/netbox/issues/10957) - Add missing VDCs column to interface tables
* [#10973](https://github.com/netbox-community/netbox/issues/10973) - Fix device links in VDC table
* [#10980](https://github.com/netbox-community/netbox/issues/10980) - Fix view tabs for plugin objects
* [#10982](https://github.com/netbox-community/netbox/issues/10982) - Catch `NoReverseMatch` exception when rendering tabs with no registered URL
* [#10984](https://github.com/netbox-community/netbox/issues/10984) - Fix navigation menu expansion for plugin menus comprising multiple words
* [#11000](https://github.com/netbox-community/netbox/issues/11000) - Improve validation of YAML-formatted import data
* [#11046](https://github.com/netbox-community/netbox/issues/11046) - Fix exception when caching very large field values for search
* [#11154](https://github.com/netbox-community/netbox/issues/11154) - Index VM interface MAC address and MTU for global search
* [#11171](https://github.com/netbox-community/netbox/issues/11171) - Fix querying of related objects under GraphQL API

### Plugins API

* [#4751](https://github.com/netbox-community/netbox/issues/4751) - Enable embedding custom content on core list views via `list_buttons()` method
* [#8927](https://github.com/netbox-community/netbox/issues/8927) - Enable inclusion of plugin models in global search via `SearchIndex`
* [#9071](https://github.com/netbox-community/netbox/issues/9071) - Enable plugins to register top-level navigation menus using PluginMenu
* [#9072](https://github.com/netbox-community/netbox/issues/9072) - Enable registration of tabbed plugin views for core NetBox models
* [#9880](https://github.com/netbox-community/netbox/issues/9880) - Enable plugins to install and register other Django apps via `django_apps` attribute
* [#9887](https://github.com/netbox-community/netbox/issues/9887) - Inspect `docs_url` property to determine link to model documentation
* [#10314](https://github.com/netbox-community/netbox/issues/10314) - Move `clone()` method from NetBoxModel to CloningMixin
* [#10543](https://github.com/netbox-community/netbox/issues/10543) - Introduce `get_plugin_config()` utility function
* [#10739](https://github.com/netbox-community/netbox/issues/10739) - Introduce `get_queryset()` method on generic views

### Other Changes

* [#9045](https://github.com/netbox-community/netbox/issues/9045) - Remove legacy ASN field from provider model
* [#9046](https://github.com/netbox-community/netbox/issues/9046) - Remove legacy contact fields from provider model
* [#10052](https://github.com/netbox-community/netbox/issues/10052) - The `cf` attribute on objects now returns deserialized custom field data
* [#10358](https://github.com/netbox-community/netbox/issues/10358) - Raise minimum required PostgreSQL version from 10 to 11
* [#10694](https://github.com/netbox-community/netbox/issues/10694) - Emit the `post_save` signal when creating device components in bulk
* [#10697](https://github.com/netbox-community/netbox/issues/10697) - Move application registry into core app
* [#10699](https://github.com/netbox-community/netbox/issues/10699) - Remove unused custom `import_object()` function
* [#10781](https://github.com/netbox-community/netbox/issues/10781) - Add support for Python v3.11
* [#10816](https://github.com/netbox-community/netbox/issues/10816) - Pass the current request as context when instantiating a FilterSet within UI views
* [#10820](https://github.com/netbox-community/netbox/issues/10820) - Switch timezone library from pytz to zoneinfo
* [#10821](https://github.com/netbox-community/netbox/issues/10821) - Enable data localization

### REST API Changes

* Added the `/api/dcim/virtual-device-contexts/` endpoint
* circuits.provider
    * Removed the `asn`, `noc_contact`, `admin_contact`, and `portal_url` fields
    * Added a `description` field
* dcim.Cable
    * Added `description` and `comments` fields
* dcim.Device
    * Added a `description` field
* dcim.DeviceType
    * Added `description`, `weight`, and `weight_unit` fields
* dcim.Module
    * Added a `description` field
* dcim.Interface
    * Added the `vdcs` field
* dcim.Module
    * Added a required `status` field
* dcim.ModuleType
    * Added `description`, `weight`, and `weight_unit` fields
* dcim.PowerFeed
    * Added a `description` field
* dcim.PowerPanel
    * Added `description` and `comments` fields
* dcim.Rack
    * Added `description`, `mounting_depth`, `weight`, `max_weight`, and `weight_unit` fields
* dcim.RackReservation
    * Added a `comments` field
* dcim.VirtualChassis
    * Added `description` and `comments` fields
* extras.CustomField
    * Added a `search_weight` field
* extras.CustomLink
    * Renamed `content_type` field to `content_types`
* extras.ExportTemplate
    * Renamed `content_type` field to `content_types`
* extras.JobResult
    * Added `interval`, `scheduled`, and `started` fields
* ipam.Aggregate
    * Added a `comments` field
* ipam.ASN
    * Added a `comments` field
* ipam.FHRPGroup
    * Added `name` and `comments` fields
* ipam.IPAddress
    * Added a `comments` field
* ipam.IPRange
    * Added a `comments` field
* ipam.L2VPN
    * Added a `comments` field
* ipam.Prefix
    * Added a `comments` field
* ipam.RouteTarget
    * Added a `comments` field
* ipam.Service
    * Added a `comments` field
* ipam.ServiceTemplate
    * Added a `comments` field
* ipam.VLAN
    * Added a `comments` field
* ipam.VRF
    * Added a `comments` field
* tenancy.Contact
    * Added a `description` field
* virtualization.Cluster
    * Added a `description` field
* virtualization.VirtualMachine
    * Added a `description` field
* wireless.WirelessLAN
    * Added a required `status` choice field
    * Added a `comments` field
* wireless.WirelessLink
    * Added a `comments` field

### GraphQL API Changes

* All object types now include a `display` field
* All cabled object types now include a `link_peers` field
* Add a `contacts` relationship for all relevant models
* dcim.Cable
    * Add A/B terminations fields
* dcim.CableTermination
    * Add `termination` field
* dcim.InventoryItem
    * Add `component` field
* dcim.InventoryItemTemplate
    * Add `component` field
* dcim.Rack
    * Add `mounting_depth` field
* ipam.FHRPGroupAssignment
    * Add `interface` field
* ipam.IPAddress
    * Add `assigned_object` field
* ipam.L2VPNTermination
    * Add `assigned_object` field
* ipam.VLANGroupType
    * Add `scope` field
