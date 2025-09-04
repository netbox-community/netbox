# NetBox v4.3

## v4.3.7 (2025-08-26)

### Enhancements

* [#18147](https://github.com/netbox-community/netbox/issues/18147) - Add device & VM interface counts under related objects for VRFs
* [#19990](https://github.com/netbox-community/netbox/issues/19990) - Button to add a missing prerequisite now includes a return URL
* [#20122](https://github.com/netbox-community/netbox/issues/20122) - Improve color contrast of highlighted data under changelog diff view
* [#20131](https://github.com/netbox-community/netbox/issues/20131) - Add object selector for interface to the MAC address edit form

### Bug Fixes

* [#18916](https://github.com/netbox-community/netbox/issues/18916) - Fix dynamic dropdown selection styling for required fields when no selection is made
* [#19645](https://github.com/netbox-community/netbox/issues/19645) - Fix interface selection when adding a cable for a virtual chassis master
* [#19669](https://github.com/netbox-community/netbox/issues/19669) - Restore token authentication support for fetching media assets
* [#19970](https://github.com/netbox-community/netbox/issues/19970) - Device role child device counts should be cumulative
* [#20012](https://github.com/netbox-community/netbox/issues/20012) - Fix support for `empty` filter lookup on custom fields
* [#20043](https://github.com/netbox-community/netbox/issues/20043) - Fix page styling when rack elevations are embedded
* [#20098](https://github.com/netbox-community/netbox/issues/20098) - Fix `AttributeError` exception when assigning tags during bulk import
* [#20120](https://github.com/netbox-community/netbox/issues/20120) - Fix REST API serialization of jobs under `/api/core/background-tasks/`
* [#20157](https://github.com/netbox-community/netbox/issues/20157) - Fix `IntegrityError` exception when a duplicate notification is triggered
* [#20164](https://github.com/netbox-community/netbox/issues/20164) - Fix `ValueError` exception when attempting to add power outlets to devices in bulk

---

## v4.3.6 (2025-08-12)

### Enhancements

* [#17222](https://github.com/netbox-community/netbox/issues/17222) - Made unread notifications more visible with improved styling and positioning
* [#18843](https://github.com/netbox-community/netbox/issues/18843) - Include color name when exporting cables
* [#18873](https://github.com/netbox-community/netbox/issues/18873) - Add a request timeout parameter to the RSS feed dashboard widget
* [#19622](https://github.com/netbox-community/netbox/issues/19622) - Allow sharing GraphQL queries as links
* [#19728](https://github.com/netbox-community/netbox/issues/19728) - Added C18 power port type for audio devices
* [#19968](https://github.com/netbox-community/netbox/issues/19968) - Improve object type selection form field when editing permissions
* [#19977](https://github.com/netbox-community/netbox/issues/19977) - Improve performance when filtering device components by site, location, or rack

### Bug Fixes

* [#19321](https://github.com/netbox-community/netbox/issues/19321) - Reduce redundant database queries when bulk importing devices
* [#19379](https://github.com/netbox-community/netbox/issues/19379) - Support singular VLAN IDs in list when editing a VLAN group
* [#19812](https://github.com/netbox-community/netbox/issues/19812) - Implement `contains` GraphQL filter for IPAM prefixes and IP ranges
* [#19917](https://github.com/netbox-community/netbox/issues/19917) - Ensure deterministic ordering of duplicate MAC addresses
* [#19996](https://github.com/netbox-community/netbox/issues/19996) - Correct dynamic query parameters for IP Address field in Add/Edit Service form
* [#19998](https://github.com/netbox-community/netbox/issues/19998) - Fix missing changelog records for deleted tags
* [#19999](https://github.com/netbox-community/netbox/issues/19999) - Corrected excessive whitespace in script list dashboard widget
* [#20001](https://github.com/netbox-community/netbox/issues/20001) - `is_api_request()` should not evaluate a request's content type
* [#20009](https://github.com/netbox-community/netbox/issues/20009) - Ensure search parameter is escaped for export links under object list views
* [#20017](https://github.com/netbox-community/netbox/issues/20017) - Fix highlighting of changed lines in changelog data
* [#20023](https://github.com/netbox-community/netbox/issues/20023) - Add GiST index on prefixes table to vastly improve bulk deletion time
* [#20030](https://github.com/netbox-community/netbox/issues/20030) - Fix height of object list action buttons & others
* [#20033](https://github.com/netbox-community/netbox/issues/20033) - Fix `TypeError` exception when bulk deleting bookmarks
* [#20056](https://github.com/netbox-community/netbox/issues/20056) - Fixed missing RF role options in device type schema validation

---

## v4.3.5 (2025-07-29)

### Enhancements
* [#18797](https://github.com/netbox-community/netbox/issues/18797) - Added jinja2.StrictUndefined option for config template rendering to catch undefined variables
* [#18936](https://github.com/netbox-community/netbox/issues/18936) - Cable imports now accept color names (e.g. "red", "blue") in addition to hex color codes
* [#19840](https://github.com/netbox-community/netbox/issues/19840) - Cable imports now support specifying site information for better organization
* [#19902](https://github.com/netbox-community/netbox/issues/19902) - Device names in rack elevation SVG exports are automatically truncated to prevent overflow beyond rack unit boundaries
* [#19903](https://github.com/netbox-community/netbox/issues/19903) - String field filters now support `regex` and `iregex` lookups for advanced pattern matching
* [#19910](https://github.com/netbox-community/netbox/issues/19910) - Internet-dependent links are no longer visible when running in air-gapped environments

### Bug Fixes
* [#18900](https://github.com/netbox-community/netbox/issues/18900) - REST API paginator now raises proper exceptions when attempting to paginate unordered querysets
* [#19916](https://github.com/netbox-community/netbox/issues/19916) - Rack elevation image/label dropdown functionality restored
* [#19934](https://github.com/netbox-community/netbox/issues/19934) - Added missing description field to tenant bulk edit form
* [#19956](https://github.com/netbox-community/netbox/issues/19956) - Prevent duplicate deletion records in changelog from cascading deletions

!!! note "Plugin Developer Advisory"
    The fix for bug [#18900](https://github.com/netbox-community/netbox/issues/18900) now raises explicit exceptions when API endpoints attempt to paginate unordered querysets. Plugin maintainers should review their API viewsets to ensure proper queryset ordering is applied before pagination, either by using `.order_by()` on querysets or by setting `ordering` in model Meta classes. Previously silent pagination issues in plugin code will now raise `QuerySetNotOrdered` exceptions and may require updates to maintain compatibility.

---

## v4.3.4 (2025-07-15)

### Enhancements

* [#18811](https://github.com/netbox-community/netbox/issues/18811) - Match expanded form IPv6 addresses in global search
* [#19550](https://github.com/netbox-community/netbox/issues/19550) - Enable lazy loading for rack elevations
* [#19571](https://github.com/netbox-community/netbox/issues/19571) - Add a default module type profile for expansion cards
* [#19793](https://github.com/netbox-community/netbox/issues/19793) - Support custom dynamic navigation menu links
* [#19828](https://github.com/netbox-community/netbox/issues/19828) - Expose L2VPN termination in interface GraphQL response

### Bug Fixes

* [#19413](https://github.com/netbox-community/netbox/issues/19413) - Custom fields should be grouped in filter forms
* [#19633](https://github.com/netbox-community/netbox/issues/19633) - Introduce InvalidCondition exception and log all evaluations of invalid event rule conditions
* [#19800](https://github.com/netbox-community/netbox/issues/19800) - Module type bulk import should support profile assignment
* [#19806](https://github.com/netbox-community/netbox/issues/19806) - Introduce JobFailed exception to allow marking background jobs as failed
* [#19827](https://github.com/netbox-community/netbox/issues/19827) - Enforce uniqueness for device role names & slugs
* [#19839](https://github.com/netbox-community/netbox/issues/19839) - Enable export of parent assignment for recursively nested objects
* [#19876](https://github.com/netbox-community/netbox/issues/19876) - Remove Markdown rendering from CustomFieldChoiceSet description field

---

## v4.3.3 (2025-06-26)

### Enhancements

* [#17183](https://github.com/netbox-community/netbox/issues/17183) - Enable associating tags with object types during bulk import
* [#17719](https://github.com/netbox-community/netbox/issues/17719) - Introduce a user preference for table row striping
* [#19492](https://github.com/netbox-community/netbox/issues/19492) - Add a UI button to download the output of an executed custom script
* [#19499](https://github.com/netbox-community/netbox/issues/19499) - Support qualifying interfaces by parent device when bulk importing wireless links

### Bug Fixes

* [#19529](https://github.com/netbox-community/netbox/issues/19529) - Fix support for running custom scripts via the `runscript` management command
* [#19555](https://github.com/netbox-community/netbox/issues/19555) - Fix support for `schedule_at` when invoking a custom script via the REST API
* [#19617](https://github.com/netbox-community/netbox/issues/19617) - Ensure consistent styling of "connect" buttons in UI
* [#19640](https://github.com/netbox-community/netbox/issues/19640) - Restore ability to filter FHRP group assignments by device/VM in GraphQL API
* [#19644](https://github.com/netbox-community/netbox/issues/19644) - Atomic transactions should always employ database routing
* [#19659](https://github.com/netbox-community/netbox/issues/19659) - Populate initial device/VM selection for "add a service" button
* [#19665](https://github.com/netbox-community/netbox/issues/19665) - Correct field reference in wireless link model validation
* [#19667](https://github.com/netbox-community/netbox/issues/19667) - Fix `TypeError` exception when creating a new module profile type with no schema
* [#19673](https://github.com/netbox-community/netbox/issues/19673) - Ignore custom field references when compiling table prefetches
* [#19677](https://github.com/netbox-community/netbox/issues/19677) - Fix exception when passing null value to `present_in_vrf` filter
* [#19680](https://github.com/netbox-community/netbox/issues/19680) - Correct chronological ordering of change records resulting from device deletions
* [#19687](https://github.com/netbox-community/netbox/issues/19687) - Cellular interface types should be considered non-connectable
* [#19702](https://github.com/netbox-community/netbox/issues/19702) - Fix `DoesNotExist` exception when deleting a notification group with an associated event rule
* [#19745](https://github.com/netbox-community/netbox/issues/19745) - Fix bulk import of services with IP addresses assigned to FHRP groups

---

## v4.3.2 (2025-06-05)

### Enhancements

* [#19200](https://github.com/netbox-community/netbox/issues/19200) - Display assigned virtual chassis (if any) on device view
* [#19461](https://github.com/netbox-community/netbox/issues/19461) - Add color backgrounds for virtual circuit types
* [#19605](https://github.com/netbox-community/netbox/issues/19605) - Enable filtering IP addresses by family in GraphQL API
* [#19627](https://github.com/netbox-community/netbox/issues/19627) - Introduce object change migrators

### Bug Fixes

* [#19415](https://github.com/netbox-community/netbox/issues/19415) - Increase maximum supported distance for circuits and wireless links
* [#19475](https://github.com/netbox-community/netbox/issues/19475) - VLANs belonging to the same location as a VM's cluster should be eligible for assignment to interfaces on that VM
* [#19486](https://github.com/netbox-community/netbox/issues/19486) - Fix connection card rendering for console server ports
* [#19487](https://github.com/netbox-community/netbox/issues/19487) - Fix `FieldError` exception when ordering circuit or tunnel terminations by the terminating object
* [#19490](https://github.com/netbox-community/netbox/issues/19490) - Fix inclusion support for config templates populated via a data source
* [#19496](https://github.com/netbox-community/netbox/issues/19496) - Fix `AttributeError` exception when rendering a config template with no output
* [#19510](https://github.com/netbox-community/netbox/issues/19510) - Restore GraphQL API filtering for assigned IP addresses
* [#19520](https://github.com/netbox-community/netbox/issues/19520) - Restore ability to alter prefix scope via the REST API
* [#19587](https://github.com/netbox-community/netbox/issues/19587) - The `occupied` filter should include interfaces terminating a wireless link
* [#19599](https://github.com/netbox-community/netbox/issues/19599) - Fix `AttributeError` exception when sorting change history under user view
* [#19610](https://github.com/netbox-community/netbox/issues/19610) - Fix `FieldError` exception when sorting tunnel terminations by tenant
* [#19623](https://github.com/netbox-community/netbox/issues/19623) - Display description under provider account view

---

## v4.3.1 (2025-05-13)

### Enhancements

* [#17073](https://github.com/netbox-community/netbox/issues/17073) - Enable global search for tags
* [#18419](https://github.com/netbox-community/netbox/issues/18419) - Enable specifying a queue name when calling `Job.enqueue()`
* [#19416](https://github.com/netbox-community/netbox/issues/19416) - Add the 1000BASE-SX interface type
* [#19434](https://github.com/netbox-community/netbox/issues/19434) - Add pre-populated interface speed choices for 2.5 and 5 Gbps

### Bug Fixes

* [#17107](https://github.com/netbox-community/netbox/issues/17107) - Fix cosmetic issue in cable traces ending at a provider network
* [#19309](https://github.com/netbox-community/netbox/issues/19309) - Improve REST API query performance for prefixes and IP addresses
* [#19361](https://github.com/netbox-community/netbox/issues/19361) - Fix incorrect GraphQL object types
* [#19375](https://github.com/netbox-community/netbox/issues/19375) - Fix table configuration after applying a saved table config
* [#19376](https://github.com/netbox-community/netbox/issues/19376) - Fix `FieldDoesNotExist` exception when global search results include a contact
* [#19380](https://github.com/netbox-community/netbox/issues/19380) - Fix column selections for child object tables
* [#19381](https://github.com/netbox-community/netbox/issues/19381) - Fix syncing of custom scripts from a remote data source
* [#19396](https://github.com/netbox-community/netbox/issues/19396) - Enable nullifying VLAN `qinq_role` via the REST API
* [#19397](https://github.com/netbox-community/netbox/issues/19397) - Correct enum type for IPRangeFilter in GraphQL API
* [#19432](https://github.com/netbox-community/netbox/issues/19432) - Update minimum required PostgreSQL version referenced by server error page
* [#19440](https://github.com/netbox-community/netbox/issues/19440) - Ensure data migrations use the correct database connection
* [#19444](https://github.com/netbox-community/netbox/issues/19444) - Fix change logging for contact group assignments
* [#19463](https://github.com/netbox-community/netbox/issues/19463) - Hide button dropdown for tables which do not support saved configs
* [#19464](https://github.com/netbox-community/netbox/issues/19464) - Fix bulk editing of inventory items from device view
* [#19465](https://github.com/netbox-community/netbox/issues/19465) - Fix ability to clear assigned prefix scope in UI
* [#19472](https://github.com/netbox-community/netbox/issues/19472) - Fix device column rendering in virtual device contexts table

---

## v4.3.0 (2025-05-01)

### Breaking Changes

* The GraphQL API Now uses an advanced syntax for filtering, to enable e.g. logical AND/OR filtering and custom field lookups.
* PostgreSQL 13 is no longer supported. NetBox v4.3 requires PostgreSQL 14.0 or later.
* The `ALLOW_TOKEN_RETRIEVAL` configuration parameter now defaults to False.
* The `device` and `virtual_machine` foreign keys on the Service model have been replaced with a generic `parent` relationship to support the assignment of services to FHRP groups as well.
* The `group` foreign key on the Contact model has been replaced with a many-to-many `groups` field.
* `django-storages` is now a required dependency. (It will be installed automatically on upgrade.)
* PluginTemplateExtension no longer supports registration via the singular `model` attribute (use `models` instead).
* The legacy staged changes functionality has been removed.

### New Features

#### Module Type Profiles & Custom Attributes ([#19002](https://github.com/netbox-community/netbox/issues/19002))

The new [module type profile](../models/dcim/moduletypeprofile.md) model enables users to declare custom profiles for module types, with the ability to define custom attributes for each profile according to its functional role. For example, a CPU module type might declare architecture and clock speed attributes; a hard disk profile might declare attributes for type and speed.

Attributes can be declared on each profile using [JSON schema](https://json-schema.org/), which allows for attributes to be declared as strings (text), integers, decimals, booleans, or choice fields. Profile attributes render as individual form fields when modifying a module type. Several profiles have been included by default to serve as examples, however these may be modified or removed.

#### Reusable Table Configurations ([#14591](https://github.com/netbox-community/netbox/issues/14591))

After modifying the displayed columns and/or ordering for a specific object table in the user interface, users now have the option to save that configuration so that it can be reused in the future. Similar to saved filters, table configs can be shared with other users to easily replicate table layouts crafted to serve specific use cases.

#### Option to Treat IP Ranges as Fully Populated ([#9763](https://github.com/netbox-community/netbox/issues/9763))

A new `mark_populated` boolean field has been added to the IPRange model. If set to true, NetBox will consider the IP range to be fully populated, and will not permit the creation of individual IP addresses within the range. For example, you might defer the management of an IP range to an external DHCP server, and wish for NetBox to treat the range as a opaque monolithic block for planning and allocation purposes.

#### Hierarchical Device Roles ([#18245](https://github.com/netbox-community/netbox/issues/18245))

Device roles can now be arranged hierarchically, with one role optionally serving as a parent to one or more child roles. For example, you might wish to create a generic "Server" role for devices with "Application Server" and "Database Server" roles beneath it. A device could then be assigned to any of these three roles.

#### Periodic Synchronization of Data Sources ([#18287](https://github.com/netbox-community/netbox/issues/18287))

Data sources can now be configured to synchronize automatically at a specified interval, as indicated by the new `sync_interval` field. No additional system configuration is necessary to support this functionality; background jobs will be scheduled automatically by the RQ worker process.

#### Proxy Routing ([#18627](https://github.com/netbox-community/netbox/issues/18627))

User can now declare one or more proxy routers via the `PROXY_ROUTERS` configuration parameter to control the use of specific proxy servers for various outbound connections. For example, it is now possible to configure NetBox to use different proxies based on the type of outbound traffic or its destination.

### Enhancements

* [#7598](https://github.com/netbox-community/netbox/issues/7598) - Adopt advanced query filtering in GraphQL API to support filtering by custom fields
* [#8423](https://github.com/netbox-community/netbox/issues/8423) - Enable assigning services to FHRP groups
* [#15842](https://github.com/netbox-community/netbox/issues/15842) - Introduce the `LOGIN_FORM_HIDDEN` configuration parameter
* [#16224](https://github.com/netbox-community/netbox/issues/16224) - Implement pagination support for the GraphQL API
* [#17170](https://github.com/netbox-community/netbox/issues/17170) - Enable the assignment of a contact to multiple contact groups
* [#17443](https://github.com/netbox-community/netbox/issues/17443) - Add a `file_name` field to the export template model
* [#17602](https://github.com/netbox-community/netbox/issues/17602) - Add a `comments` field to all nested group models (Region, SiteGroup, Location, ContactGroup, TenantGroup, and WirelessLANGroup)
* [#17608](https://github.com/netbox-community/netbox/issues/17608) - Add a `status` field to the L2VPN model
* [#17653](https://github.com/netbox-community/netbox/issues/17653) - Enable declaring Jinja environment parameters on export templates (similar to config templates)
* [#17793](https://github.com/netbox-community/netbox/issues/17793) - Introduce a REST API endpoint for tagged objects (`/api/extras/tagged-objects/`)
* [#17841](https://github.com/netbox-community/netbox/issues/17841) - Add a `weight` field to the Tag model to influence ordering
* [#18296](https://github.com/netbox-community/netbox/issues/18296) - Add a `tenant` field to the VLAN group model
* [#18352](https://github.com/netbox-community/netbox/issues/18352) - Add a `status` field to the power outlet model
* [#18417](https://github.com/netbox-community/netbox/issues/18417) - Add an `outer_height` field to the rack & rack type models
* [#18535](https://github.com/netbox-community/netbox/issues/18535) - The presence of incompatible plugins will no longer prevent NetBox from starting
* [#18780](https://github.com/netbox-community/netbox/issues/18780) - Introduce `DATABASES` and `DATABASE_ROUTERS` configuration parameters to enable defining connections to external databases (e.g. for plugins)
* [#18783](https://github.com/netbox-community/netbox/issues/18783) - Enable filtering all applicable models by tag ID
* [#18785](https://github.com/netbox-community/netbox/issues/18785) - Enable custom choices for rack, device, and module airflow
* [#18896](https://github.com/netbox-community/netbox/issues/18896) - Enable the use of remote storage for custom scripts

### Plugins

* [#16630](https://github.com/netbox-community/netbox/issues/16630) - Plugins can now inject content within the HTML `<head>` block via the new `plugin_head()` method on PluginTemplateExtension
* [#17424](https://github.com/netbox-community/netbox/issues/17424) - Extend ViewTab with a `visible` argument to control tab rendering
* [#17857](https://github.com/netbox-community/netbox/issues/17857) - Added a `release_track` attribute to PluginConfig
* [#18305](https://github.com/netbox-community/netbox/issues/18305) - Introduce plugin support for ContactsMixin
* [#19073](https://github.com/netbox-community/netbox/issues/19073) - Allow installed plugins to be omitted from the plugins list

### Other Changes

* [#18071](https://github.com/netbox-community/netbox/issues/18071) - Removed legacy staged changed functionality in favor of the [netbox-branching](https://github.com/netboxlabs/netbox-branching) plugin
* [#18072](https://github.com/netbox-community/netbox/issues/18072) - Drop support for the singular `model` attribute on PluginTemplateExtension (use `models` instead)
* [#18191](https://github.com/netbox-community/netbox/issues/18191) - Remove redundant PostgreSQL indexes
* [#18236](https://github.com/netbox-community/netbox/issues/18236) - Upgrade the HTMX library to v2.0
* [#18540](https://github.com/netbox-community/netbox/issues/18540) - Operational plugins are now recorded in the application registry
* [#18623](https://github.com/netbox-community/netbox/issues/18623) - Upgrade the Tabler CSS theme to v1.2
* [#18743](https://github.com/netbox-community/netbox/issues/18743) - Upgrade Django to v5.2
* [#18751](https://github.com/netbox-community/netbox/issues/18751) - Change the default value for `ALLOW_TOKEN_RETRIEVAL` to False
* [#18808](https://github.com/netbox-community/netbox/issues/18808) - Squashed migration dependencies have been altered to rectify an issue with Django's `sqlmigrate` management command
* [#18820](https://github.com/netbox-community/netbox/issues/18820) - PostgreSQL 13 is no longer supported
* [#19004](https://github.com/netbox-community/netbox/issues/19004) - The use of inventory items has been deprecated in favor of modules. Inventory items and roles may be removed in a future NetBox release.

### REST API Changes

* Added the following endpoints:
    * `/api/extras/table-configs/`
    * `/api/extras/tagged-objects/`
    * `/api/dcim/module-type-profiles/`
* core.DataSource
    * Added the optional `sync_interval` field
* dcim.DeviceRole
    * Added the optional `parent` recursive foreign key field to effect hierarchical ordering
    * Added a `comments` field
* dcim.Location
    * Added a `comments` field
* dcim.ModuleType
    * Added the optional `profile` foreign key to the new ModuleTypeProfile model
* dcim.PowerOutlet
    * Added a `status` field
* dcim.Rack
    * Added the optional `outer_height` field
* dcim.RackType
    * Added the optional `outer_height` field
* dcim.Region
    * Added a `comments` field
* dcim.SiteGroup
    * Added a `comments` field
* extras.ConfigTemplate
    * Added optional fields `mime_type`, `file_name`, `file_extension` and `as_attachment`
* extras.ExportTemplate
    * Added optional fields `file_name` and `environment_params` (JSON)
* extras.Tag
    * Added a `weight` field
* ipam.IPRange
    * Added a `mark_populaed` boolean field
* ipam.L2VPN
    * Added a `status` field
* ipam.Service
    * Removed the `device` and `virtual_machine` foreign key fields
    * Added the `parent_object_type`, `parent_object_id`, and (read-only) `parent` fields
* ipam.VLANGroup
    * Added the optional `tenant` foreign key field
* tenancy.Contact
    * Removed the `group` foreign key field
    * Added the `groups` many-to-many field
* tenancy.ContactGroup
    * Added a `comments` field
* tenancy.TenantGroup
    * Added a `comments` field
* wireless.WirelessLANGroup
    * Added a `comments` field
