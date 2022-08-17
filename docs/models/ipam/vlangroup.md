# VLAN Groups

VLAN groups can be used to organize [VLANs](./vlan.md) within NetBox. Each VLAN group can be scoped to a particular [region](../dcim/region.md), [site group](../dcim/sitegroup.md), [site](../dcim/sitegroup.md), [location](../dcim/location.md), [rack](../dcim/rack.md), [cluster group](../virtualization/clustergroup.md), or [cluster](../virtualization/cluster.md). Member VLANs will be available for assignment to devices and/or virtual machines within the specified scope.

Groups can also be used to enforce uniqueness: Each VLAN within a group must have a unique ID and name. VLANs which are not assigned to a group may have overlapping names and IDs (including VLANs which belong to a common site). For example, two VLANs with ID 123 may be created, but they cannot both be assigned to the same group.

## Fields

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

### Minimum & Maximum VLAN IDs

A minimum and maximum child VLAN ID must be set for each group. (These default to 1 and 4094 respectively.) VLANs created within a group must have a VID that falls between these values (inclusive).

### Scope

The domain covered by a VLAN group, defined as one of the supported object types. This conveys the context in which a VLAN group applies.
