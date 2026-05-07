# Rack Groups

Racks can optionally be assigned to rack groups to reflect their physical placement. Rack groups provide a secondary means of categorization alongside [locations](./location.md), which is particularly useful for datacenter operators who need to group racks by row, aisle, or similar physical arrangement while keeping them assigned to the same location, such as a cage or room. Rack groups are flat and do not form a hierarchy.

Rack groups can also be used to scope [VLAN groups](../ipam/vlangroup.md), which can help model L2 domains spanning rows or pairs of racks.

## Fields

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)
