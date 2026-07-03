# NetBox v4.6

## v4.6.4 (2026-06-30)

### Enhancements

* [#21710](https://github.com/netbox-community/netbox/issues/21710) - Render JSON schema `enum` options as a dropdown selection in module and device profile attribute forms
* [#22174](https://github.com/netbox-community/netbox/issues/22174) - Include the `dns_name` of primary & out-of-band IP addresses in event payloads
* [#22279](https://github.com/netbox-community/netbox/issues/22279) - Add a 1C8P:8C1P breakout cable profile
* [#22548](https://github.com/netbox-community/netbox/issues/22548) - Improve the styling of action buttons in the navigation sidebar

### Performance Improvements

* [#22169](https://github.com/netbox-community/netbox/issues/22169) - Improve performance of the image attachments view when using S3 storage
* [#22442](https://github.com/netbox-community/netbox/issues/22442) - Avoid repeated serializer instantiation in `GFKSerializerField`
* [#22526](https://github.com/netbox-community/netbox/issues/22526) - Chunk bulk updates to custom field data to better handle a large number of records

### Bug Fixes

* [#21310](https://github.com/netbox-community/netbox/issues/21310) - Fix LDAP group lookup failure when a returned row contains a null value
* [#22439](https://github.com/netbox-community/netbox/issues/22439) - Enforce object-level permissions on custom links rendered via the `custom_links` template tag
* [#22440](https://github.com/netbox-community/netbox/issues/22440) - Remove errant `changelog` relation from GraphQL schema
* [#22480](https://github.com/netbox-community/netbox/issues/22480) - Restore inline browser display of device front/rear images instead of forcing a download
* [#22489](https://github.com/netbox-community/netbox/issues/22489) - Update the cached virtual chassis name on member devices in the search index when a virtual chassis is renamed
* [#22501](https://github.com/netbox-community/netbox/issues/22501) - Return JSON rather than an HTML error page for GraphQL API exceptions
* [#22507](https://github.com/netbox-community/netbox/issues/22507) - Also check `is_active` in the superuser bypass for `restrict()` and `IsSuperuser`
* [#22543](https://github.com/netbox-community/netbox/issues/22543) - Prevent deletion of an existing custom script's file when re-uploading a same-named script via the REST API
* [#22561](https://github.com/netbox-community/netbox/issues/22561) - Fix `AttributeError` when importing IP addresses with `is_primary`/`is_oob` set but no device assigned

### Accessibility

* [#22527](https://github.com/netbox-community/netbox/issues/22527) - Announce quick search results to screen readers
* [#22528](https://github.com/netbox-community/netbox/issues/22528) - Make the Results/Filters tabs keyboard-operable
* [#22529](https://github.com/netbox-community/netbox/issues/22529) - Allow the left sidebar accordion to be toggled with the spacebar
* [#22530](https://github.com/netbox-community/netbox/issues/22530) - Remove hidden `<select>` inputs from the accessibility tree
* [#22531](https://github.com/netbox-community/netbox/issues/22531) - Associate a label with the "Saved Filter" combobox for screen readers
* [#22532](https://github.com/netbox-community/netbox/issues/22532) - Provide an accessible name for the empty checkbox column header cell in object tables

---

## v4.6.3 (2026-06-16)

### Enhancements

* [#17598](https://github.com/netbox-community/netbox/issues/17598) - Add bulk creation support for VLANs
* [#21666](https://github.com/netbox-community/netbox/issues/21666) - Add MU connector type for fiber ports and cables
* [#22361](https://github.com/netbox-community/netbox/issues/22361) - Introduce an `ArrayAttr` UI panel attribute for rendering array field values
* [#22457](https://github.com/netbox-community/netbox/issues/22457) - Use `hmac.compare_digest()` for constant-time authentication of API tokens

### Performance Improvements

* [#21870](https://github.com/netbox-community/netbox/issues/21870) - Optimize prefix availability calculations
* [#22375](https://github.com/netbox-community/netbox/issues/22375) - Improve efficiency of filtering VLANs by interface

### Bug Fixes

* [#21338](https://github.com/netbox-community/netbox/issues/21338) - Include connected endpoint data in interface webhooks generated during cable creation
* [#21895](https://github.com/netbox-community/netbox/issues/21895) - Restore pagination controls for job log entries (previously limited to 50 rows)
* [#22210](https://github.com/netbox-community/netbox/issues/22210) - Respect saved filters when rendering IPAM child availability views in additional tabs
* [#22237](https://github.com/netbox-community/netbox/issues/22237) - Fix server error when opening the standalone "Add Table Configuration" page
* [#22245](https://github.com/netbox-community/netbox/issues/22245) - Include the `id` field in the OpenAPI request schemas for bulk PATCH/PUT endpoints
* [#22251](https://github.com/netbox-community/netbox/issues/22251) - Re-parent child module bays when a multi-bay module is moved to a new bay
* [#22273](https://github.com/netbox-community/netbox/issues/22273) - Fix migration failure when a service has several thousand ports defined
* [#22303](https://github.com/netbox-community/netbox/issues/22303) - Add the missing `fields` parameter to the OpenAPI schema
* [#22324](https://github.com/netbox-community/netbox/issues/22324) - Fix GraphQL filtering of custom field choice set extra choices
* [#22340](https://github.com/netbox-community/netbox/issues/22340) - Display a token's allowed IPs as comma-separated strings rather than `IPNetwork` objects
* [#22346](https://github.com/netbox-community/netbox/issues/22346) - Render SSO/SAML authentication failures as a login page message instead of an HTTP 500 error
* [#22357](https://github.com/netbox-community/netbox/issues/22357) - Remove the unused `local_context_data` field from `dcim.Module` (which no longer inherits from `ConfigContextModel`)
* [#22376](https://github.com/netbox-community/netbox/issues/22376) - Fix `AssertionError` in event rule script jobs when a device type has an image attached
* [#22388](https://github.com/netbox-community/netbox/issues/22388) - Pin redis-py to 7.x to avoid a startup failure on older Redis releases
* [#22397](https://github.com/netbox-community/netbox/issues/22397) - Fix `AttributeError` exception when an unauthenticated user attempts to export devices
* [#22399](https://github.com/netbox-community/netbox/issues/22399) - Enforce object permissions on the related object when serving static media
* [#22427](https://github.com/netbox-community/netbox/issues/22427) - Validate `JSONFilter.path` to prevent ORM operator injection over JSONField contents in the GraphQL API
* [#22429](https://github.com/netbox-community/netbox/issues/22429) - Enforce `ObjectPermission` constraints on `grant_token` in the REST API
* [#22431](https://github.com/netbox-community/netbox/issues/22431) - Use a cryptographically secure random number generator when generating API tokens
* [#22444](https://github.com/netbox-community/netbox/issues/22444) - Fix `KeyError` exception on the power feed detail view when the locale is not English
* [#22448](https://github.com/netbox-community/netbox/issues/22448) - Ensure all object representations are escaped under `handle_protectederror()`
* [#22454](https://github.com/netbox-community/netbox/issues/22454) - Fix serialization of decimal custom field values to avoid spurious changelog entries
* [#22466](https://github.com/netbox-community/netbox/issues/22466) - Fix test failure against SSL-enabled PosgtreSQL

### Deprecations

* [#22392](https://github.com/netbox-community/netbox/issues/22392) - Deprecate support for Redis 5.x (to be removed in v4.7)

---

## v4.6.2 (2026-06-02)

### Enhancements

* [#17127](https://github.com/netbox-community/netbox/issues/17127) - Add a user preference for selecting metric or imperial units of measurement
* [#19336](https://github.com/netbox-community/netbox/issues/19336) - Convert the filtering of tabbed list views from JavaScript to HTMX
* [#19460](https://github.com/netbox-community/netbox/issues/19460) - Support additional template variables for greater flexibility when constructing map URLs
* [#20804](https://github.com/netbox-community/netbox/issues/20804) - Support bulk renaming of the `label` field on device components
* [#21261](https://github.com/netbox-community/netbox/issues/21261) - Allow setting `quick_add` on an `ObjectVar` in custom scripts
* [#21952](https://github.com/netbox-community/netbox/issues/21952) - Improve robustness of the RQ worker liveness check
* [#22109](https://github.com/netbox-community/netbox/issues/22109) - Include child dependency counts in the module type REST API representation
* [#22212](https://github.com/netbox-community/netbox/issues/22212) - Make designated environment parameters available within Jinja2 templates via the new `env()` filter
* [#22239](https://github.com/netbox-community/netbox/issues/22239) - Rename the "Save" button on the table configuration form to "Apply" for clarity
* [#22255](https://github.com/netbox-community/netbox/issues/22255) - Allow plugins to register custom serializer resolvers for `get_serializer_for_model()`

### Bug Fixes

* [#21091](https://github.com/netbox-community/netbox/issues/21091) - Declare proper request & response schema types for the device/VM config rendering API endpoints
* [#22158](https://github.com/netbox-community/netbox/issues/22158) - Cache empty config revision state to avoid per-request queries polluting database connections
* [#22163](https://github.com/netbox-community/netbox/issues/22163) - Fix `ValueError` raised by CircuitTerminationForm when a termination type is set but the target object is blank
* [#22180](https://github.com/netbox-community/netbox/issues/22180) - Ensure custom scripts added via a remote data source are validated
* [#22187](https://github.com/netbox-community/netbox/issues/22187) - Fix erroneous cable path retracing when using a cable profile
* [#22219](https://github.com/netbox-community/netbox/issues/22219) - Add missing required form field indicator to InlineFields rows
* [#22228](https://github.com/netbox-community/netbox/issues/22228) - Validate `vid_ranges` bounds metadata in `VLANGroup.save()` to avoid miscounts and a crash on singleton ranges
* [#22232](https://github.com/netbox-community/netbox/issues/22232) - Prevent duplicate scheduled background jobs from being created
* [#22233](https://github.com/netbox-community/netbox/issues/22233) - Fix `site_id` filter on the cables REST API returning no results when both endpoints are circuit terminations
* [#22247](https://github.com/netbox-community/netbox/issues/22247) - Display the verbose name instead of the internal model name for the related object type on the custom field detail page
* [#22270](https://github.com/netbox-community/netbox/issues/22270) - Avoid recording a spurious UPDATE change record after DELETE for objects with reverse SET_NULL relations
* [#22282](https://github.com/netbox-community/netbox/issues/22282) - Fix `fetch()` on S3Backend to reliably resolve object keys
* [#22283](https://github.com/netbox-community/netbox/issues/22283) - Restrict the Job queryset in ScriptResultView to authorized objects
* [#22286](https://github.com/netbox-community/netbox/issues/22286) - Mark the `name` and `description` fields on the GraphQL ConfigContextProfileFilter as optional
* [#22287](https://github.com/netbox-community/netbox/issues/22287) - Fix GraphQL `EventRuleFilter.action_object_type` being typed as a string lookup against a ContentType foreign key
* [#22301](https://github.com/netbox-community/netbox/issues/22301) - Avoid name conflict when multiple plugins introduce taggable models of the same name
* [#22307](https://github.com/netbox-community/netbox/issues/22307) - Fix inconsistent enforcement of `grant_token` permissions between the UI and REST API
* [#22325](https://github.com/netbox-community/netbox/issues/22325) - Fix `AttributeError` when creating a custom field choice set with base choices
* [#22328](https://github.com/netbox-community/netbox/issues/22328) - Avoid out-of-memory crash in DynamicMultipleChoiceField with large choice sets

---

## v4.6.1 (2026-05-19)

### Enhancements

* [#16851](https://github.com/netbox-community/netbox/issues/16851) - Correct errant and missing ARIA labels throughout the UI
* [#20776](https://github.com/netbox-community/netbox/issues/20776) - Add changelog message support for bulk rename operations
* [#20808](https://github.com/netbox-community/netbox/issues/20808) - Display the names of installed devices when selecting a rack position
* [#21938](https://github.com/netbox-community/netbox/issues/21938) - Display geographic hierarchy for circuit terminations assigned to sites, locations, or regions
* [#21993](https://github.com/netbox-community/netbox/issues/21993) - Allow IP ranges comprising a single IP address
* [#22057](https://github.com/netbox-community/netbox/issues/22057) - Add filter support for notifications and subscriptions to GraphQL API
* [#22192](https://github.com/netbox-community/netbox/issues/22192) - Introduce `HTTP_CLIENT_IP_HEADERS` configuration parameter to customize HTTP headers used to determine client IP address

### Performance Improvements

* [#22060](https://github.com/netbox-community/netbox/issues/22060) - Implement GraphQL query depth limiting (via `GRAPHQL_MAX_QUERY_DEPTH`) to guard against excessively complex queries
* [#22061](https://github.com/netbox-community/netbox/issues/22061) - Add prefetch hints to various GraphQL type mixins to improve query efficiency
* [#22102](https://github.com/netbox-community/netbox/issues/22102) - Add GIN index on CablePath to optimize filtering of cable paths by node
* [#22104](https://github.com/netbox-community/netbox/issues/22104) - Avoid retracing cable paths during cable deletion
* [#22146](https://github.com/netbox-community/netbox/issues/22146) - Avoid renumbering MPTT trees when creating module bays

### Bug Fixes

* [#21934](https://github.com/netbox-community/netbox/issues/21934) - Fix striped table rows overriding conditional row color highlighting for virtual/LAG interfaces
* [#22055](https://github.com/netbox-community/netbox/issues/22055) - Fix API exceptions being silently consumed by middleware without reporting to Sentry
* [#22079](https://github.com/netbox-community/netbox/issues/22079) - Fix security vulnerability allowing arbitrary code execution via ExportTemplate `environment_params` (CVE-2026-29514)
* [#22081](https://github.com/netbox-community/netbox/issues/22081) - REST API should return plaintext for new v2 tokens upon creation
* [#22183](https://github.com/netbox-community/netbox/issues/22183) - Fix spurious changelog entries for `interface_b` generated when saving an unchanged wireless link
* [#22190](https://github.com/netbox-community/netbox/issues/22190) - Restore tenant and tenant group column options for circuits group table configuration
* [#22198](https://github.com/netbox-community/netbox/issues/22198) - Restrict export template queryset to authorized objects in REST API and list views
* [#22202](https://github.com/netbox-community/netbox/issues/22202) - Fix crash in system housekeeping job when no stable releases are available
* [#22206](https://github.com/netbox-community/netbox/issues/22206) - Fix `TypeError` exception raised by table config validation when `ordering` attribute is null
* [#22207](https://github.com/netbox-community/netbox/issues/22207) - Fix missing explicit `object_type` field annotation on TableConfigType GraphQL type
* [#22208](https://github.com/netbox-community/netbox/issues/22208) - Add missing `user_id` FK filter on job filterset
* [#22209](https://github.com/netbox-community/netbox/issues/22209) - Add missing `cable_id` FK filter on cable termination filterset
* [#22227](https://github.com/netbox-community/netbox/issues/22227) - Fix display of IP address detail view when multiple NAT assignments exist
* [#22236](https://github.com/netbox-community/netbox/issues/22236) - Fix support for user changelog message when saving table configurations via the REST API

### Deprecations

* [#22128](https://github.com/netbox-community/netbox/issues/22128) - Deprecate support for v1 API tokens (to be removed in v5.0)
* [#22141](https://github.com/netbox-community/netbox/issues/22141) - Deprecate support for PostgreSQL 14 (to be removed in v4.7)

---

## v4.6.0 (2026-05-05)

### New Features

#### Virtual Machine Types ([#5795](https://github.com/netbox-community/netbox/issues/5795))

A new VirtualMachineType model has been introduced to enable categorization of virtual machines by instance type, analogous to how DeviceType categorizes physical hardware. VM types can be defined once and reused across many virtual machines.

#### Cable Bundles ([#20151](https://github.com/netbox-community/netbox/issues/20151))

A new CableBundle model allows individual cables to be grouped together to represent physical cable runs that are managed as a unit; e.g. a bundle of 48 CAT6 cables between two patch panels. (Please note that this feature is _not_ suitable for modeling individual fiber strands within a single cable.)

#### Rack Groups ([#20961](https://github.com/netbox-community/netbox/issues/20961))

A flat RackGroup model has been reintroduced to provide a lightweight secondary axis of rack organization (e.g. by row or aisle) that is independent of the location hierarchy. Racks carry an optional foreign key to a RackGroup, and RackGroup can also serve as a scope for VLANGroup assignments.

#### ETag Support for REST API ([#21356](https://github.com/netbox-community/netbox/issues/21356))

The REST API now returns an `ETag` header on responses for individual objects, derived from the object's last-updated timestamp. Clients can supply an `If-Match` header on PUT/PATCH requests to guard against conflicting concurrent updates; if the object has been modified since the ETag was issued, the server returns a 412 (Precondition Failed) response.

#### Cursor-based Pagination for REST API ([#21363](https://github.com/netbox-community/netbox/issues/21363))

A new `start` query parameter has been introduced as an efficient alternative to the existing `offset` parameter for paginating large result sets. Rather than scanning the table up to a relative offset, the `start` parameter filters for objects with a primary key equal to or greater than the given value, enabling constant-time pagination regardless of result set size.

### Enhancements

* [#12024](https://github.com/netbox-community/netbox/issues/12024) - Permit virtual machines to be assigned to devices without a cluster
* [#14329](https://github.com/netbox-community/netbox/issues/14329) - Improve diff highlighting for custom field data in change logs
* [#15513](https://github.com/netbox-community/netbox/issues/15513) - Add bulk creation support for IP prefixes
* [#17654](https://github.com/netbox-community/netbox/issues/17654) - Support role assignment for ASNs
* [#19025](https://github.com/netbox-community/netbox/issues/19025) - Support optional schema validation for JSON custom fields
* [#19034](https://github.com/netbox-community/netbox/issues/19034) - Annotate total reserved unit count on rack reservations
* [#19138](https://github.com/netbox-community/netbox/issues/19138) - Include NAT addresses for primary & out-of-band IP addresses in REST API
* [#19648](https://github.com/netbox-community/netbox/issues/19648) - Add a color custom field type
* [#19796](https://github.com/netbox-community/netbox/issues/19796) - Support `{module}` position inheritance for nested module bays
* [#19953](https://github.com/netbox-community/netbox/issues/19953) - Enable debugging support for ConfigTemplate rendering
* [#20123](https://github.com/netbox-community/netbox/issues/20123) - Introduce options to control adoption/replication of device components via REST API (replicates UI behavior)
* [#20152](https://github.com/netbox-community/netbox/issues/20152) - Support for marking module and device bays as disabled
* [#20162](https://github.com/netbox-community/netbox/issues/20162) - Provide an option to execute as a background job when adding components to devices in bulk
* [#20163](https://github.com/netbox-community/netbox/issues/20163) - Add changelog message support for bulk device component creation
* [#20698](https://github.com/netbox-community/netbox/issues/20698) - Add read-only `total_vlan_ids` attribute on VLAN group representation in REST & GraphQL APIs
* [#20916](https://github.com/netbox-community/netbox/issues/20916) - Include stack trace for unhandled exceptions in job logs
* [#21157](https://github.com/netbox-community/netbox/issues/21157) - Include all public model classes in export template context
* [#21409](https://github.com/netbox-community/netbox/issues/21409) - Introduce `CHANGELOG_RETAIN_CREATE_LAST_UPDATE` configuration parameter to retain creation & most recent update record in change log for each object
* [#21575](https://github.com/netbox-community/netbox/issues/21575) - Introduce `{vc_position}` template variable for device component template name/label
* [#21662](https://github.com/netbox-community/netbox/issues/21662) - Increase `rf_channel_frequency` precision to 3 decimal places
* [#21702](https://github.com/netbox-community/netbox/issues/21702) - Include a serialized representation of the HTTP request in each webhook
* [#21720](https://github.com/netbox-community/netbox/issues/21720) - Align HTTP basic auth regex of `EnhancedURLValidator` with Django's `URLValidator`
* [#21751](https://github.com/netbox-community/netbox/issues/21751) - Disable notifications for scripts running in the background
* [#21770](https://github.com/netbox-community/netbox/issues/21770) - Enable specifying columns to include/exclude on embedded tables
* [#21771](https://github.com/netbox-community/netbox/issues/21771) - Add support for partial tag assignment (`add_tags`) and removal (`remove_tags`) via REST API
* [#21780](https://github.com/netbox-community/netbox/issues/21780) - Add changelog message support to bulk creation of IP addresses
* [#21865](https://github.com/netbox-community/netbox/issues/21865) - Allow setting empty `INTERNAL_IPS` to enable debug toolbar for all clients
* [#21924](https://github.com/netbox-community/netbox/issues/21924) - Improve styling and consistency of floating bulk action controls
* [#22062](https://github.com/netbox-community/netbox/issues/22062) - Display API token ID & plaintext one time immediately upon creation

### Performance Improvements

* [#21455](https://github.com/netbox-community/netbox/issues/21455) - Ensure PostgreSQL indexes exist to support the default ordering of each model
* [#21688](https://github.com/netbox-community/netbox/issues/21688) - Reduce per-position ORM lookups when tracing cable paths
* [#21788](https://github.com/netbox-community/netbox/issues/21788) - Optimize bulk object export to avoid timeout errors on large querysets

### Plugins

* [#20924](https://github.com/netbox-community/netbox/issues/20924) - Introduce support for declarative layouts and reusable UI components
* [#21357](https://github.com/netbox-community/netbox/issues/21357) - Provide an API for plugins to register custom model actions (for permission assignment)

### Deprecations

* [#21284](https://github.com/netbox-community/netbox/issues/21284) - Deprecate the `username` and `request_id` fields in event data
* [#21304](https://github.com/netbox-community/netbox/issues/21304) - Deprecate the `housekeeping` management command
* [#21331](https://github.com/netbox-community/netbox/issues/21331) - Deprecate NetBox's custom `querystring` template tag
* [#21881](https://github.com/netbox-community/netbox/issues/21881) - Deprecate legacy Sentry configuration parameters
* [#21884](https://github.com/netbox-community/netbox/issues/21884) - Deprecate the obsolete `DEFAULT_ACTION_PERMISSIONS` mapping
* [#21887](https://github.com/netbox-community/netbox/issues/21887) - Deprecate support for legacy view actions
* [#21890](https://github.com/netbox-community/netbox/issues/21890) - Deprecate `models` key in application registry
* [#21936](https://github.com/netbox-community/netbox/issues/21936) - Deprecate the `LOGIN_REQUIRED` configuration parameter
* [#22046](https://github.com/netbox-community/netbox/issues/22046) - Deprecate OptionalLimitOffsetPagination 
* [#22047](https://github.com/netbox-community/netbox/issues/22047) - Deprecate ExpandableIPAddressField 
* [#22048](https://github.com/netbox-community/netbox/issues/22048) - Deprecate the `expand_ipaddress_pattern()` utility function

### Other Changes

* [#20984](https://github.com/netbox-community/netbox/issues/20984) - Upgrade to Django 6.0
* [#21635](https://github.com/netbox-community/netbox/issues/21635) - Migrate documentation site from mkdocs to Zensical

### REST API Changes

* New features:
    * `ETag` response header and `If-Match` request header support for all individual object endpoints
    * `start` query parameter for cursor-based pagination on all list endpoints
    * `add_tags` and `remove_tags` write-only fields on all taggable model serializers
* New endpoints:
    * `GET/POST /api/dcim/cable-bundles/`
    * `GET/PUT/PATCH/DELETE /api/dcim/cable-bundles/<id>/`
    * `GET/POST /api/dcim/rack-groups/`
    * `GET/PUT/PATCH/DELETE /api/dcim/rack-groups/<id>/`
    * `GET/POST /api/virtualization/virtual-machine-types/`
    * `GET/PUT/PATCH/DELETE /api/virtualization/virtual-machine-types/<id>/`
* `dcim.Cable`
    * Add optional foreign key field `bundle`
* `dcim.Device`
    * The `primary_ip`, `primary_ip4`, `primary_ip6`, and `oob_ip` nested representations now include `nat_inside` and `nat_outside`
* `dcim.DeviceBay`
    * Add boolean field `enabled`
    * Add read-only boolean field `_occupied`
* `dcim.DeviceBayTemplate`
    * Add boolean field `enabled`
* `dcim.Module`
    * Add write-only boolean fields `replicate_components` and `adopt_components`
* `dcim.ModuleBay`
    * Add boolean field `enabled`
    * Add read-only boolean field `_occupied`
* `dcim.ModuleBayTemplate`
    * Add boolean field `enabled`
* `dcim.Rack`
    * Add optional foreign key field `group`
* `dcim.RackReservation`
    * Add read-only integer field `unit_count`
* `extras.CustomField`
    * Add JSON field `validation_schema`
* `ipam.ASN`
    * Add optional foreign key field `role`
* `ipam.Role`
    * Annotate count of assigned ASNs (`asn_count`)
* `ipam.VLANGroup`
    * Add read-only field `total_vlan_ids`
* `virtualization.VirtualMachine`
    * Add optional foreign key field `virtual_machine_type`
    * The `primary_ip`, `primary_ip4`, and `primary_ip6` nested representations now include `nat_inside` and `nat_outside`
    * The `cluster` field is now optional (nullable)
