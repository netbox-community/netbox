# Change Logging

Every time an object in NetBox is created, updated, or deleted, a serialized copy of that object is saved to the database, along with meta data including the current time and the user associated with the change. These records form a running changelog both for each individual object as well as NetBox as a whole (Organization > Changelog).

A serialized representation is included for each object in JSON format. This is similar to how objects are conveyed within the REST API, but does not include any nested representations. For instance, the `tenant` field of a site will record only the tenant's ID, not a representation of the tenant.

When a request is made, a random request ID is generated and attached to any change records resulting from the request. For example, editing multiple objects in bulk will create a change record for each object, and each of those objects will be assigned the same request ID. This makes it easy to identify all the change records associated with a particular request.

Change records are exposed in the API via the read-only endpoint `/api/extras/object-changes/`. They may also be exported in CSV format.
