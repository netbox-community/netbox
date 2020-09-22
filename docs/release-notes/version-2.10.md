# NetBox v2.10

## v2.10-beta1 (FUTURE)

**NOTE:** This release completely removes support for embedded graphs.

### New Features

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

### Enhancements

* [#1503](https://github.com/netbox-community/netbox/issues/1503) - Allow assigment of secrets to virtual machines
* [#1692](https://github.com/netbox-community/netbox/issues/1692) - Allow assigment of inventory items to parent items in web UI
* [#2179](https://github.com/netbox-community/netbox/issues/2179) - Support the assignment of multiple port numbers for services
* [#4956](https://github.com/netbox-community/netbox/issues/4956) - Include inventory items on primary device view
* [#5003](https://github.com/netbox-community/netbox/issues/5003) - CSV import now accepts slug values for choice fields
* [#5146](https://github.com/netbox-community/netbox/issues/5146) - Add custom fields support for cables, power panels, rack reservations, and virtual chassis

### Other Changes

* [#1846](https://github.com/netbox-community/netbox/issues/1846) - Enable MPTT for InventoryItem hierarchy
* [#4349](https://github.com/netbox-community/netbox/issues/4349) - Dropped support for embedded graphs
* [#4360](https://github.com/netbox-community/netbox/issues/4360) - Remove support for the Django template language from export templates
* [#4878](https://github.com/netbox-community/netbox/issues/4878) - Custom field data is now stored directly on each object
* [#4941](https://github.com/netbox-community/netbox/issues/4941) - `commit` argument is now required argument in a custom script's `run()` method

### REST API Changes

* Added support for `PUT`, `PATCH`, and `DELETE` operations on list endpoints
* dcim.Cable: Added `custom_fields`
* dcim.InventoryItem: The `_depth` field has been added to reflect MPTT positioning
* dcim.PowerPanel: Added `custom_fields`
* dcim.RackReservation: Added `custom_fields`
* dcim.VirtualChassis: Added `custom_fields`
* extras.ExportTemplate: The `template_language` field has been removed
* extras.Graph: This API endpoint has been removed (see #4349)
* ipam.Service: Renamed `port` to `ports`; now holds a list of one or more port numbers
* secrets.Secret: Removed `device` field; replaced with `assigned_object` generic foreign key. This may represent either a device or a virtual machine. Assign an object by setting `assigned_object_type` and `assigned_object_id`.
