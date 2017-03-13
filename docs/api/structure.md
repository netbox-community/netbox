# URL Hierarchy

NetBox's entire REST API is housed under the API root, `/api/`. The API's URL structure is divided at the root level by application: circuits, DCIM, extras, IPAM, secrets, and tenancy. Within each application, each model has its own path. For example:

* /api/circuits/providers/
* /api/circuits/circuits/
* /api/dcim/sites/
* /api/dcim/racks/
* /api/dcim/devices/

Each model generally has two URLs associated with it: a list URL and a detail URL. The list URL is used to request a list of multiple objects or to create a new object. The detail URL is used to retrieve, update, or delete an existing object.

* /api/dcim/devices/ - List devices or create a new device
* /api/dcim/devices/123/ - Retrieve, update, or delete the device with ID 123

Lists of objects can be filtered using a set of query parameters. For example, to find all interfaces belonging to the device with ID 123:

```
GET /api/dcim/interfaces/?device_id=123
```

# Serializers

The NetBox API employs three types of serializers to represent model data:

* Base serializer
* Nested serializer
* Writable serializer

The base serializer is used to represent the default view of a model. This includes all database table fields which comprise the model, and may include additional metadata. A base serializer includes relationships to parent objects, but **does not** include child objects. For example, the `VLANSerializer` includes a nested representation its parent VLANGroup (if any), but does not include any assigned Prefixes.

Related objects (e.g. `ForeignKey` fields) are represented using a nested serializer. A nested serializer provides a minimal representation of an object, including only its URL and enough information to construct its name.

When a base serializer includes one or more nested serializers, the hierarchical structure precludes it from being used for write operations. Thus, a flat representation of an object may be provided using a writable serializer. This serializer includes only raw database values and is not typically used for retrieval, except as part of the response to the creation or updating of an object.
