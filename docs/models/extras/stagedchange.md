# Staged Changes

A staged change represents the creation of a new object or the modification or deletion of an existing object to be performed at some future point. Each change must be assigned to a [branch](./branch.md).

Changes can be applied individually via the `apply()` method, however it is recommended to apply changes in bulk using the parent branch's `commit()` method.

## Fields

!!! warning
    Staged changes are not typically created or manipulated directly, but rather effected through the use of the [`checkout()`](../../plugins/development/staged-changes.md) context manager.

### Branch

The [branch](./branch.md) to which this change belongs.

### Action

The type of action this change represents: `create`, `update`, or `delete`.

### Object

A generic foreign key referencing the existing object to which this change applies.

### Data

JSON representation of the changes being made to the object (not applicable for deletions).
