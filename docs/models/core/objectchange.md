# Object Changes

An object change is a record of a single create, update, or delete operation against an object whose model supports [change logging](../../features/change-logging.md). Object changes form a complete audit trail: each one captures the user that initiated the change, the request that caused it, the action performed, and a JSON snapshot of the object before and after.

For component objects (e.g. an interface on a device), an object change can also reference a related parent object so that the change appears in the parent's changelog as well as the component's own.

## Fields

### Time

The date and time at which the change was recorded.

### User & User Name

The [user](../users/user.md) who initiated the change. The user's username is also stored as a static string (`user_name`) so that change records remain readable even after the user account is deleted.

### Request ID

A UUID identifying the request that produced the change. All changes resulting from a single request share the same request ID, which makes it easy to correlate related modifications. The same value is returned on REST API responses via the `X-Request-ID` header.

### Action

The type of operation performed: `create`, `update`, or `delete`.

### Changed Object

A generic foreign key (`changed_object_type` + `changed_object_id`) identifying the object that was modified.

### Related Object

An optional generic foreign key referencing a related object (e.g. the parent device for a changed interface). When set, the change is also surfaced in the related object's changelog.

### Object Representation

A static text representation of the changed object, captured at the time of the change. Preserved so that the change record is meaningful even after the underlying object is deleted.

### Message

An optional free-form message attached to the change. May be supplied via the UI (in eligible forms) or via the [REST API](../../integrations/rest-api.md#changelog-messages) using the `changelog_message` field.

### Pre-Change Data & Post-Change Data

JSON snapshots of the object's serialized state immediately before and immediately after the change. For `create` actions, only post-change data is recorded; for `delete` actions, only pre-change data. The diff displayed in the UI is computed from these snapshots.
