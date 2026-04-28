# NetBox v4.6

## v4.6.0-beta2 (2026-04-28)

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
