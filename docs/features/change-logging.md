# Change Logging

Every time an object in NetBox is created, updated, or deleted, a serialized copy of that object taken both before and after the change is saved to the database, along with metadata including the current time and the user associated with the change. These records form a persistent record of changes both for each individual object as well as NetBox as a whole. The global change log can be viewed by navigating to Other > Change Log.

A serialized representation of the instance being modified is included in JSON format. This is similar to how objects are conveyed within the REST API, but does not include any nested representations. For instance, the `tenant` field of a site will record only the tenant's ID, not a representation of the tenant.

When a request is made, a UUID is generated and attached to any change records resulting from that request. For example, editing three objects in bulk will create a separate change record for each  (three in total), and each of those objects will be associated with the same UUID. This makes it easy to identify all the change records resulting from a particular request.

Change records are exposed in the API via the read-only endpoint `/api/extras/object-changes/`. They may also be exported via the web UI in CSV format.

## User Messages

When creating, modifying, or deleting an object in NetBox, a user has the option of recording an arbitrary message (up to 200 characters) that will appear in the change record. This can be helpful to capture additional context, such as the reason for a change or a reference to an external ticket.

When editing an object via the web UI, the "Changelog message" field appears at the bottom of the form. This field is optional. The changelog message field is available in object create forms, object edit forms, delete confirmation dialogs, and bulk operations.

For information on including changelog messages when making changes via the REST API, see [Changelog Messages](../integrations/rest-api.md#changelog-messages).

## Correlating Changes by Request

Every request made to NetBox is assigned a random unique ID that can be used to correlate change records. For example, if you change the status of three sites using the UI's bulk edit feature, you will see three new change records (one for each site) all referencing the same request ID. This shows that all three changes were made as part of the same request.
