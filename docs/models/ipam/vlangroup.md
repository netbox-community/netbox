# VLAN Groups

VLAN groups can be used to organize VLANs within NetBox. Each VLAN group can be scoped to a particular region, site group, site, location, rack, cluster group, or cluster. Member VLANs will be available for assignment to devices and/or virtual machines within the specified scope.

Groups can also be used to enforce uniqueness: Each VLAN within a group must have a unique ID and name. VLANs which are not assigned to a group may have overlapping names and IDs (including VLANs which belong to a common site). For example, you can create two VLANs with ID 123, but they cannot both be assigned to the same group.
