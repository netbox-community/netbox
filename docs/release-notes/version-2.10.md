# NetBox v2.10

## v2.10-beta3 (FUTURE)

### Enhancements

* [#5411](https://github.com/netbox-community/netbox/issues/5411) - Include cable tags in trace view

### Bug Fixes

* [#5417](https://github.com/netbox-community/netbox/issues/5417) - Fix exception when viewing a device installed within a device bay

---

## v2.10-beta2 (2020-12-03)

### Enhancements

* [#5274](https://github.com/netbox-community/netbox/issues/5274) - Add REST API support for custom fields
* [#5399](https://github.com/netbox-community/netbox/issues/5399) - Show options for cable endpoint types during bulk import

### Bug Fixes

* [#5176](https://github.com/netbox-community/netbox/issues/5176) - Enforce content type restrictions when creating objects via the REST API
* [#5358](https://github.com/netbox-community/netbox/issues/5358) - Fix user table configuration for VM interfaces
* [#5374](https://github.com/netbox-community/netbox/issues/5374) - Fix exception thrown when tracing mid-point
* [#5376](https://github.com/netbox-community/netbox/issues/5376) - Correct invalid custom field filter logic values
* [#5395](https://github.com/netbox-community/netbox/issues/5395) - Fix cable tracing for rear ports with no corresponding front port

### Other Changes

* [#4711](https://github.com/netbox-community/netbox/issues/4711) - Renamed Webhook `obj_type` to `content_types`

---

## v2.10-beta1 (2020-11-17)

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

### Other Changes

* [#1846](https://github.com/netbox-community/netbox/issues/1846) - Enable MPTT for InventoryItem hierarchy
* [#2755](https://github.com/netbox-community/netbox/issues/2755) - Switched from Font Awesome/Glyphicons to Material Design icons
* [#4349](https://github.com/netbox-community/netbox/issues/4349) - Dropped support for embedded graphs
* [#4360](https://github.com/netbox-community/netbox/issues/4360) - Dropped support for the Django template language from export templates
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
