# Branches

!!! danger "Deprecated Feature"
    This feature has been deprecated in NetBox v4.2 and will be removed in a future release. Please consider using the [netbox-branching plugin](https://github.com/netboxlabs/netbox-branching), which provides much more robust functionality.

A branch is a collection of related [staged changes](./stagedchange.md) that have been prepared for merging into the active database. A branch can be merged by executing its `commit()` method. Deleting a branch will delete all its related changes.

## Fields

### Name

The branch's name.

### User

The user to which the branch belongs (optional).
