# Change Logging

Every time an object in NetBox is created, updated, or deleted, a serialized copy of that object is saved to the database, along with meta data including the current time and the user associated with the change. These records form a persistent record of changes both for each individual object as well as NetBox as a whole. The global change log can be viewed by navigating to Other > Change Log.

A serialized representation of the instance being modified is included in JSON format. This is similar to how objects are conveyed within the REST API, but does not include any nested representations. For instance, the `tenant` field of a site will record only the tenant's ID, not a representation of the tenant.

When a request is made, a UUID is generated and attached to any change records resulting from that request. For example, editing three objects in bulk will create a separate change record for each  (three in total), and each of those objects will be associated with the same UUID. This makes it easy to identify all the change records resulting from a particular request.

Change records are exposed in the API via the read-only endpoint `/api/extras/object-changes/`. They may also be exported via the web UI in CSV format.
