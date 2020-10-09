# NetBox v2.10

## v2.10-beta1 (FUTURE)

**NOTE:** This release completely removes support for embedded graphs.

### New Features

#### Route Targets ([#259](https://github.com/netbox-community/netbox/issues/259))

This release introduces support for model L3VPN route targets, which can be used to control the redistribution of routing information among VRFs. Each VRF may be assigned one or more route targets in the import or export direction (or both). Like VRFs, route targets may be assigned to tenants and may have tags applied to them.

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

#### Improved Cable Trace Performance ([#4900](https://github.com/netbox-community/netbox/issues/4900))

All end-to-end cable paths are now cached using the new CablePath model. This allows NetBox to now immediately return the complete path originating from any endpoint directly from the database, rather than having to trace each cable recursively. It also resolves some systemic validation issues with the original implementation.

**Note:** As part of this change, cable traces will no longer traverse circuits: A circuit termination will be considered the origin or destination of an end-to-end path.

### Enhancements

* [#1503](https://github.com/netbox-community/netbox/issues/1503) - Allow assigment of secrets to virtual machines
* [#1692](https://github.com/netbox-community/netbox/issues/1692) - Allow assigment of inventory items to parent items in web UI
* [#2179](https://github.com/netbox-community/netbox/issues/2179) - Support the assignment of multiple port numbers for services
* [#4897](https://github.com/netbox-community/netbox/issues/4897) - Allow filtering by content type identified as `<app>.<model>` string
* [#4956](https://github.com/netbox-community/netbox/issues/4956) - Include inventory items on primary device view
* [#5003](https://github.com/netbox-community/netbox/issues/5003) - CSV import now accepts slug values for choice fields
* [#5146](https://github.com/netbox-community/netbox/issues/5146) - Add custom fields support for cables, power panels, rack reservations, and virtual chassis
* [#5190](https://github.com/netbox-community/netbox/issues/5190) - Add a REST API endpoint for content types

### Other Changes

* [#1846](https://github.com/netbox-community/netbox/issues/1846) - Enable MPTT for InventoryItem hierarchy
* [#4349](https://github.com/netbox-community/netbox/issues/4349) - Dropped support for embedded graphs
* [#4360](https://github.com/netbox-community/netbox/issues/4360) - Remove support for the Django template language from export templates
* [#4878](https://github.com/netbox-community/netbox/issues/4878) - Custom field data is now stored directly on each object
* [#4941](https://github.com/netbox-community/netbox/issues/4941) - `commit` argument is now required argument in a custom script's `run()` method
* [#5225](https://github.com/netbox-community/netbox/issues/5225) - Circuit termination port speed is now an optional field

### REST API Changes

* Added support for `PUT`, `PATCH`, and `DELETE` operations on list endpoints (bulk update and delete)
* Added `/extras/content-types/` endpoint for Django ContentTypes
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
* ipam.RouteTarget: New endpoint
* ipam.Service: Renamed `port` to `ports`; now holds a list of one or more port numbers
* ipam.VRF: Added `import_targets` and `export_targets` fields
* secrets.Secret: Removed `device` field; replaced with `assigned_object` generic foreign key. This may represent either a device or a virtual machine. Assign an object by setting `assigned_object_type` and `assigned_object_id`.
