# VLAN Groups

VLAN groups can be used to organize VLANs within NetBox. Each group may optionally be assigned to a specific site, but a group cannot belong to multiple sites.

Groups can also be used to enforce uniqueness: Each VLAN within a group must have a unique ID and name. VLANs which are not assigned to a group may have overlapping names and IDs (including VLANs which belong to a common site). For example, you can create two VLANs with ID 123, but they cannot both be assigned to the same group.
