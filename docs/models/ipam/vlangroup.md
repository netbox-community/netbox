# VLAN Groups

VLAN groups can be used to organize [VLANs](./vlan.md) within NetBox. Each VLAN group can be scoped to a particular [region](../dcim/region.md), [site group](../dcim/sitegroup.md), [site](../dcim/sitegroup.md), [location](../dcim/location.md), [rack](../dcim/rack.md), [cluster group](../virtualization/clustergroup.md), or [cluster](../virtualization/cluster.md). Member VLANs will be available for assignment to devices and/or virtual machines within the specified scope.

Groups can also be used to enforce uniqueness: Each VLAN within a group must have a unique ID and name. VLANs which are not assigned to a group may have overlapping names and IDs (including VLANs which belong to a common site). For example, two VLANs with ID 123 may be created, but they cannot both be assigned to the same group.

## Fields

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

### VLAN ID Ranges

The set of VLAN IDs which are encompassed by the group. By default, this will be the entire range of valid IEEE 802.1Q VLAN IDs (1 to 4094, inclusive). VLANs created within a group must have a VID that falls within one of these ranges. Ranges may not overlap.

Internally, each range is stored in PostgreSQL as a canonical half-open `[start, end)` interval. The `start` value is the first VID included in the range; the `end` value sits one above the last VID included.

The REST API and UI both present ranges using inclusive bounds, so most users never see the half-open form. Users working with the stored value directly, such as through psql, raw SQL, Django ORM access in Custom Scripts or plugins, or third-party tools, should expect this canonical representation.

For the range covering VLANs 100 through 200:

* UI input: `100-200`
* REST API range item: `[100, 200]`
* Database row: `[100, 201)`

### Total VLAN IDs

A read-only integer indicating the total count of VLAN IDs available within the group, calculated from the configured VLAN ID Ranges. For example, a group with ranges `100-199` and `300-399` would have a total of 200 VLAN IDs. This value is automatically computed and updated whenever the VLAN ID ranges are modified.

### Scope

The domain covered by a VLAN group, defined as one of the supported object types. This conveys the context in which a VLAN group applies.
