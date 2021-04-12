# NetBox v2.10

## v2.10.9 (FUTURE)

### Enhancements

* [#5526](https://github.com/netbox-community/netbox/issues/5526) - Add MAC address search field to VM interfaces list
* [#5756](https://github.com/netbox-community/netbox/issues/5756) - Omit child devices from non-racked devices list under rack view
* [#5840](https://github.com/netbox-community/netbox/issues/5840) - Add column to cable termination objects to display cable color
* [#6054](https://github.com/netbox-community/netbox/issues/6054) - Display NAPALM-enabled device tabs only when relevant
* [#6083](https://github.com/netbox-community/netbox/issues/6083) - Support disabling TLS certificate validation for Redis

### Bug Fixes

* [#5805](https://github.com/netbox-community/netbox/issues/5805) - Fix missing custom field filters for cables, rack reservations
* [#6070](https://github.com/netbox-community/netbox/issues/6070) - Add missing `count_ipaddresses` attribute to VMInterface serializer
* [#6073](https://github.com/netbox-community/netbox/issues/6073) - Permit users to manage their own REST API tokens without needing explicit permission
* [#6081](https://github.com/netbox-community/netbox/issues/6081) - Fix interface connections REST API endpoint
* [#6082](https://github.com/netbox-community/netbox/issues/6082) - Support colons in webhook header values
* [#6108](https://github.com/netbox-community/netbox/issues/6108) - Do not infer tenant assignment from parent objects for prefixes, IP addresses
* [#6117](https://github.com/netbox-community/netbox/issues/6117) - Handle exception when attempting to assign an MPTT-enabled model as its own parent
* [#6131](https://github.com/netbox-community/netbox/issues/6131) - Correct handling of boolean fields when cloning objects

---

## v2.10.8 (2021-03-26)

### Bug Fixes

* [#6060](https://github.com/netbox-community/netbox/issues/6060) - Fix exception on cable trace in UI (regression from #5650)

---

## v2.10.7 (2021-03-25)

### Enhancements

* [#5641](https://github.com/netbox-community/netbox/issues/5641) - Allow filtering device components by label
* [#5723](https://github.com/netbox-community/netbox/issues/5723) - Allow customization of the geographic mapping service via `MAPS_URL` config parameter
* [#5736](https://github.com/netbox-community/netbox/issues/5736) - Allow changing site assignment when bulk editing devices
* [#5953](https://github.com/netbox-community/netbox/issues/5953) - Support Markdown rendering for custom script descriptions
* [#6040](https://github.com/netbox-community/netbox/issues/6040) - Add UI search fields for asset tag for devices and racks

### Bug Fixes

* [#5595](https://github.com/netbox-community/netbox/issues/5595) - Restore ability to delete an uploaded device type image
* [#5650](https://github.com/netbox-community/netbox/issues/5650) - Denote when the total length of a cable trace may exceed the indicated value
* [#5962](https://github.com/netbox-community/netbox/issues/5962) - Ensure consistent display of change log action labels
* [#5966](https://github.com/netbox-community/netbox/issues/5966) - Skip Markdown reference link when tabbing through form fields
* [#5977](https://github.com/netbox-community/netbox/issues/5977) - Correct validation of `RELEASE_CHECK_URL` config parameter
* [#6006](https://github.com/netbox-community/netbox/issues/6006) - Fix VLAN group/site association for bulk prefix import
* [#6010](https://github.com/netbox-community/netbox/issues/6010) - Eliminate duplicate virtual chassis search results
* [#6012](https://github.com/netbox-community/netbox/issues/6012) - Pre-populate attributes when creating an available child prefix via the UI
* [#6023](https://github.com/netbox-community/netbox/issues/6023) - Fix display of bottom banner with uBlock Origin enabled

---

## v2.10.6 (2021-03-09)

### Enhancements

* [#5592](https://github.com/netbox-community/netbox/issues/5592) - Add IP addresses count to VRF view
* [#5630](https://github.com/netbox-community/netbox/issues/5630) - Add QSFP+ (64GFC) FibreChannel Interface option
* [#5884](https://github.com/netbox-community/netbox/issues/5884) - Enable custom links for device components
* [#5914](https://github.com/netbox-community/netbox/issues/5914) - Add edit/delete buttons for IP addresses on interface view
* [#5942](https://github.com/netbox-community/netbox/issues/5942) - Add button to add a new IP address on interface view

### Bug Fixes

* [#5703](https://github.com/netbox-community/netbox/issues/5703) - Fix VRF and Tenant field population when adding IP addresses from prefix
* [#5819](https://github.com/netbox-community/netbox/issues/5819) - Enable ordering of virtual machines by primary IP address
* [#5872](https://github.com/netbox-community/netbox/issues/5872) - Ordering of devices by primary IP should respect `PREFER_IPV4` configuration parameter
* [#5922](https://github.com/netbox-community/netbox/issues/5922) - Fix options for filtering object permissions in admin UI
* [#5935](https://github.com/netbox-community/netbox/issues/5935) - Fix filtering prefixes list by multiple prefix values
* [#5948](https://github.com/netbox-community/netbox/issues/5948) - Invalidate cached queries when running `renaturalize`

---

## v2.10.5 (2021-02-24)

### Bug Fixes

* [#5315](https://github.com/netbox-community/netbox/issues/5315) - Fix site unassignment from VLAN when using "None" option
* [#5626](https://github.com/netbox-community/netbox/issues/5626) - Fix REST API representation for circuit terminations connected to non-interface endpoints
* [#5716](https://github.com/netbox-community/netbox/issues/5716) - Fix filtering rack reservations by custom field
* [#5718](https://github.com/netbox-community/netbox/issues/5718) - Fix bulk editing of services when no port(s) are defined
* [#5735](https://github.com/netbox-community/netbox/issues/5735) - Ensure consistent treatment of duplicate IP addresses
* [#5738](https://github.com/netbox-community/netbox/issues/5738) - Fix redirect to device components view after disconnecting a cable
* [#5753](https://github.com/netbox-community/netbox/issues/5753) - Fix Redis Sentinel password application for caching
* [#5786](https://github.com/netbox-community/netbox/issues/5786) - Allow setting null tenant group on tenant via REST API
* [#5841](https://github.com/netbox-community/netbox/issues/5841) - Disallow the creation of available prefixes/IP addresses in violation of assigned permission constraints

---

## v2.10.4 (2021-01-26)

### Enhancements

* [#5542](https://github.com/netbox-community/netbox/issues/5542) - Show cable trace lengths in both meters and feet
* [#5570](https://github.com/netbox-community/netbox/issues/5570) - Add "management only" filter widget for interfaces list
* [#5586](https://github.com/netbox-community/netbox/issues/5586) - Allow filtering virtual chassis by name and master
* [#5612](https://github.com/netbox-community/netbox/issues/5612) - Add GG45 and TERA port types, and CAT7a and CAT8 cable types
* [#5678](https://github.com/netbox-community/netbox/issues/5678) - Show available type choices for all device component import forms

### Bug Fixes

* [#5232](https://github.com/netbox-community/netbox/issues/5232) - Correct swagger definition for ip_prefixes_available-ips_create API
* [#5574](https://github.com/netbox-community/netbox/issues/5574) - Restrict the creation of device bay templates on non-parent device types
* [#5584](https://github.com/netbox-community/netbox/issues/5584) - Restore power utilization panel under device view
* [#5597](https://github.com/netbox-community/netbox/issues/5597) - Fix ordering devices by primary IP address
* [#5603](https://github.com/netbox-community/netbox/issues/5603) - Fix display of white cables in trace view
* [#5639](https://github.com/netbox-community/netbox/issues/5639) - Fix filtering connection lists by device name
* [#5640](https://github.com/netbox-community/netbox/issues/5640) - Fix permissions assessment when adding VM interfaces in bulk
* [#5648](https://github.com/netbox-community/netbox/issues/5648) - Include VC member interfaces on interfaces tab count when viewing VC master
* [#5665](https://github.com/netbox-community/netbox/issues/5665) - Validate rack group is assigned to same site when creating a rack
* [#5683](https://github.com/netbox-community/netbox/issues/5683) - Correct rack elevation displayed when viewing a reservation

---

## v2.10.3 (2021-01-05)

### Bug Fixes

* [#5049](https://github.com/netbox-community/netbox/issues/5049) - Add check for LLDP neighbor chassis name to lldp_neighbors
* [#5301](https://github.com/netbox-community/netbox/issues/5301) - Fix misleading error when racking a device with invalid parameters
* [#5311](https://github.com/netbox-community/netbox/issues/5311) - Update child objects when a rack group is moved to a new site
* [#5518](https://github.com/netbox-community/netbox/issues/5518) - Fix persistent vertical scrollbar
* [#5533](https://github.com/netbox-community/netbox/issues/5533) - Fix bulk editing of objects with required custom fields
* [#5540](https://github.com/netbox-community/netbox/issues/5540) - Fix exception when viewing a provider with one or more tags assigned
* [#5543](https://github.com/netbox-community/netbox/issues/5543) - Fix rendering of config contexts with cluster assignment for devices
* [#5546](https://github.com/netbox-community/netbox/issues/5546) - Add custom field bulk edit support for cables, power panels, rack reservations, and virtual chassis
* [#5547](https://github.com/netbox-community/netbox/issues/5547) - Add custom field bulk import support for cables, power panels, rack reservations, and virtual chassis
* [#5551](https://github.com/netbox-community/netbox/issues/5551) - Restore missing import button on services list
* [#5557](https://github.com/netbox-community/netbox/issues/5557) - Fix VRF route target assignment via REST API
* [#5558](https://github.com/netbox-community/netbox/issues/5558) - Fix regex validation support for custom URL fields
* [#5563](https://github.com/netbox-community/netbox/issues/5563) - Fix power feed cable trace link
* [#5564](https://github.com/netbox-community/netbox/issues/5564) - Raise validation error if a power port template's `allocated_draw` exceeds its `maximum_draw`
* [#5569](https://github.com/netbox-community/netbox/issues/5569) - Ensure consistent labeling of interface `mgmt_only` field
* [#5573](https://github.com/netbox-community/netbox/issues/5573) - Report inconsistent values when migrating custom field data

---

## v2.10.2 (2020-12-21)

### Enhancements

* [#5489](https://github.com/netbox-community/netbox/issues/5489) - Add filters for type and width to racks list
* [#5496](https://github.com/netbox-community/netbox/issues/5496) - Add form field to filter rack reservation by user

### Bug Fixes

* [#5254](https://github.com/netbox-community/netbox/issues/5254) - Require plugin authors to set zip_safe=False
* [#5468](https://github.com/netbox-community/netbox/issues/5468) - Fix unlocking secrets from device/VM view
* [#5473](https://github.com/netbox-community/netbox/issues/5473) - Fix alignment of rack names in elevations list
* [#5478](https://github.com/netbox-community/netbox/issues/5478) - Fix display of route target description
* [#5484](https://github.com/netbox-community/netbox/issues/5484) - Fix "tagged" indication in VLAN members list
* [#5486](https://github.com/netbox-community/netbox/issues/5486) - Optimize retrieval of config context data for device/VM REST API views
* [#5487](https://github.com/netbox-community/netbox/issues/5487) - Support filtering rack type/width with multiple values
* [#5488](https://github.com/netbox-community/netbox/issues/5488) - Fix caching error when viewing cable trace after toggling cable status
* [#5498](https://github.com/netbox-community/netbox/issues/5498) - Fix filtering rack reservations by username
* [#5499](https://github.com/netbox-community/netbox/issues/5499) - Fix filtering of displayed device/VM interfaces by regex
* [#5507](https://github.com/netbox-community/netbox/issues/5507) - Fix custom field data assignment via UI for IP addresses, secrets
* [#5510](https://github.com/netbox-community/netbox/issues/5510) - Fix filtering by boolean custom fields

---

## v2.10.1 (2020-12-15)

### Bug Fixes

* [#5444](https://github.com/netbox-community/netbox/issues/5444) - Don't force overwriting of boolean fields when bulk editing interfaces
* [#5450](https://github.com/netbox-community/netbox/issues/5450) - API serializer foreign count fields do not have a default value
* [#5453](https://github.com/netbox-community/netbox/issues/5453) - Correct change log representation when creating a cable
* [#5458](https://github.com/netbox-community/netbox/issues/5458) - Creating a component template throws an exception
* [#5461](https://github.com/netbox-community/netbox/issues/5461) - Rack Elevations throw reverse match exception
* [#5463](https://github.com/netbox-community/netbox/issues/5463) - Back-to-back Circuit Termination throws AttributeError exception
* [#5465](https://github.com/netbox-community/netbox/issues/5465) - Correct return URL when disconnecting a cable from a device
* [#5466](https://github.com/netbox-community/netbox/issues/5466) - Fix validation for required custom fields
* [#5470](https://github.com/netbox-community/netbox/issues/5470) - Fix exception when making `OPTIONS` request for a REST API list endpoint

---

## v2.10.0 (2020-12-14)

**NOTE:** This release completely removes support for embedded graphs.

**NOTE:** The Django templating language (DTL) is no longer supported for export templates. Ensure that all export templates use Jinja2 before upgrading.

### New Features

#### Route Targets ([#259](https://github.com/netbox-community/netbox/issues/259))

This release introduces support for modeling L3VPN route targets, which can be used to control the redistribution of advertised prefixes among VRFs. Each VRF may be assigned one or more route targets in the import and/or export direction. Like VRFs, route targets may be assigned to tenants and support tag assignment.

#### REST API Bulk Deletion ([#3436](https://github.com/netbox-community/netbox/issues/3436))

The REST API now supports the bulk deletion of objects of the same type in a single request. Send a `DELETE` HTTP request to the list to the model's list endpoint (e.g. `/api/dcim/sites/`) with a list of JSON objects specifying the numeric ID of each object to be deleted. For example, to delete sites with IDs 10, 11, and 12, issue the following request:

```no-highlight
curl -s -X DELETE \
-H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
http://netbox/api/dcim/sites/ \
--data '[{"id": 10}, {"id": 11}, {"id": 12}]'
```

#### REST API Bulk Update ([#4882](https://github.com/netbox-community/netbox/issues/4882))

Similar to bulk deletion, the REST API also now supports bulk updates. Send a `PUT` or `PATCH` HTTP request to the list to the model's list endpoint (e.g. `/api/dcim/sites/`) with a list of JSON objects specifying the numeric ID of each object and the attribute(s) to be updated. For example, to set a description for sites with IDs 10 and 11, issue the following request:

```no-highlight
curl -s -X PATCH \
-H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
http://netbox/api/dcim/sites/ \
--data '[{"id": 10, "description": "Foo"}, {"id": 11, "description": "Bar"}]'
```

#### Reimplementation of Custom Fields ([#4878](https://github.com/netbox-community/netbox/issues/4878))

NetBox v2.10 introduces a completely overhauled approach to custom fields. Whereas previous versions used CustomFieldValue instances to store values, custom field data is now stored directly on each model instance as JSON data and may be accessed using the `cf` property:

```python
>>> site = Site.objects.first()
>>> site.cf
{'site_code': 'US-RAL01'}
>>> site.cf['foo'] = 'ABC'
>>> site.full_clean()
>>> site.save()
>>> site = Site.objects.first()
>>> site.cf
{'foo': 'ABC', 'site_code': 'US-RAL01'}
```

Additionally, custom selection field choices are now defined on the CustomField model within the admin UI, which greatly simplifies working with choice values.

#### Improved Cable Trace Performance ([#4900](https://github.com/netbox-community/netbox/issues/4900))

All end-to-end cable paths are now cached using the new CablePath backend model. This allows NetBox to now immediately return the complete path originating from any endpoint directly from the database, rather than having to trace each cable recursively. It also resolves some systemic validation issues present in the original implementation.

**Note:** As part of this change, cable traces will no longer traverse circuits: A circuit termination will be considered the origin or destination of an end-to-end path.

### Enhancements

* [#609](https://github.com/netbox-community/netbox/issues/609) - Add min/max value and regex validation for custom fields
* [#1503](https://github.com/netbox-community/netbox/issues/1503) - Allow assigment of secrets to virtual machines
* [#1692](https://github.com/netbox-community/netbox/issues/1692) - Allow assigment of inventory items to parent items in web UI
* [#2179](https://github.com/netbox-community/netbox/issues/2179) - Support the use of multiple port numbers when defining a service
* [#4897](https://github.com/netbox-community/netbox/issues/4897) - Allow filtering by content type identified as `<app>.<model>` string
* [#4918](https://github.com/netbox-community/netbox/issues/4918) - Add a REST API endpoint (`/api/status/`) which returns NetBox's current operational status
* [#4956](https://github.com/netbox-community/netbox/issues/4956) - Include inventory items on primary device view
* [#4967](https://github.com/netbox-community/netbox/issues/4967) - Support tenant assignment for aggregates
* [#5003](https://github.com/netbox-community/netbox/issues/5003) - CSV import now accepts slug values for choice fields
* [#5146](https://github.com/netbox-community/netbox/issues/5146) - Add custom field support for cables, power panels, rack reservations, and virtual chassis
* [#5154](https://github.com/netbox-community/netbox/issues/5154) - The web interface now consumes the entire browser window
* [#5190](https://github.com/netbox-community/netbox/issues/5190) - Add a REST API endpoint for retrieving content types (`/api/extras/content-types/`)
* [#5274](https://github.com/netbox-community/netbox/issues/5274) - Add REST API support for custom fields
* [#5399](https://github.com/netbox-community/netbox/issues/5399) - Show options for cable endpoint types during bulk import
* [#5411](https://github.com/netbox-community/netbox/issues/5411) - Include cable tags in trace view

### Other Changes

* [#1846](https://github.com/netbox-community/netbox/issues/1846) - Enable MPTT for InventoryItem hierarchy
* [#2755](https://github.com/netbox-community/netbox/issues/2755) - Switched from Font Awesome/Glyphicons to Material Design icons
* [#4349](https://github.com/netbox-community/netbox/issues/4349) - Dropped support for embedded graphs
* [#4360](https://github.com/netbox-community/netbox/issues/4360) - Dropped support for the Django template language from export templates
* [#4711](https://github.com/netbox-community/netbox/issues/4711) - Renamed Webhook `obj_type` to `content_types`
* [#4941](https://github.com/netbox-community/netbox/issues/4941) - `commit` argument is now required argument in a custom script's `run()` method
* [#5011](https://github.com/netbox-community/netbox/issues/5011) - Standardized name field lengths across all models
* [#5139](https://github.com/netbox-community/netbox/issues/5139) - Omit utilization statistics from RIR list
* [#5225](https://github.com/netbox-community/netbox/issues/5225) - Circuit termination port speed is now an optional field

### REST API Changes

* Added support for `PUT`, `PATCH`, and `DELETE` operations on list endpoints (bulk update and delete)
* Added the `/extras/content-types/` endpoint for Django ContentTypes
* Added the `/extras/custom-fields/` endpoint for custom fields
* Removed the `/extras/_custom_field_choices/` endpoint (replaced by new custom fields endpoint)
* Added the `/status/` endpoint to convey NetBox's current status
* circuits.CircuitTermination:
  * Added the `/trace/` endpoint
  * Replaced `connection_status` with `connected_endpoint_reachable` (boolean)
  * Added `cable_peer` and `cable_peer_type`
  * `port_speed` may now be null
* dcim.Cable: Added `custom_fields`
* dcim.ConsolePort:
  * Replaced `connection_status` with `connected_endpoint_reachable` (boolean)
  * Added `cable_peer` and `cable_peer_type`
  * Removed `connection_status` from nested serializer
* dcim.ConsoleServerPort:
  * Replaced `connection_status` with `connected_endpoint_reachable` (boolean)
  * Added `cable_peer` and `cable_peer_type`
  * Removed `connection_status` from nested serializer
* dcim.FrontPort:
  * Replaced the `/trace/` endpoint with `/paths/`, which returns a list of cable paths
  * Added `cable_peer` and `cable_peer_type`
* dcim.Interface:
  * Replaced `connection_status` with `connected_endpoint_reachable` (boolean)
  * Added `cable_peer` and `cable_peer_type`
  * Removed `connection_status` from nested serializer
* dcim.InventoryItem: The `_depth` field has been added to reflect MPTT positioning
* dcim.PowerFeed:
  * Added the `/trace/` endpoint
  * Added fields `connected_endpoint`, `connected_endpoint_type`, `connected_endpoint_reachable`, `cable_peer`, and `cable_peer_type`
* dcim.PowerOutlet:
  * Replaced `connection_status` with `connected_endpoint_reachable` (boolean)
  * Added `cable_peer` and `cable_peer_type`
  * Removed `connection_status` from nested serializer
* dcim.PowerPanel: Added `custom_fields`
* dcim.PowerPort
  * Replaced `connection_status` with `connected_endpoint_reachable` (boolean)
  * Added `cable_peer` and `cable_peer_type`
  * Removed `connection_status` from nested serializer
* dcim.RackReservation: Added `custom_fields`
* dcim.RearPort:
  * Replaced the `/trace/` endpoint with `/paths/`, which returns a list of cable paths
  * Added `cable_peer` and `cable_peer_type`
* dcim.VirtualChassis: Added `custom_fields`
* extras.ExportTemplate: The `template_language` field has been removed
* extras.Graph: This API endpoint has been removed (see #4349)
* extras.ImageAttachment: Filtering by `content_type` now takes a string in the form `<app>.<model>`
* extras.ObjectChange: Filtering by `changed_object_type` now takes a string in the form `<app>.<model>`
* ipam.Aggregate: Added `tenant` field
* ipam.RouteTarget: New endpoint
* ipam.Service: Renamed `port` to `ports`; now holds a list of one or more port numbers
* ipam.VRF: Added `import_targets` and `export_targets` fields
* secrets.Secret: Removed `device` field; replaced with `assigned_object` generic foreign key. This may represent either a device or a virtual machine. Assign an object by setting `assigned_object_type` and `assigned_object_id`.
