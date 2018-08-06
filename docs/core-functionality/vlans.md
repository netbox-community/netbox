# VLANs

A VLAN represents an isolated layer two domain, identified by a name and a numeric ID (1-4094) as defined in [IEEE 802.1Q](https://en.wikipedia.org/wiki/IEEE_802.1Q). Each VLAN may be assigned to a site and/or VLAN group.

Each VLAN must be assigned one of the following operational statuses:

* Active
* Reserved
* Deprecated

Each VLAN may also be assigned a functional role. Prefixes and VLANs share the same set of customizable roles.

## VLAN Groups

VLAN groups can be used to organize VLANs within NetBox. Groups can also be used to enforce uniqueness: Each VLAN within a group must have a unique ID and name. VLANs which are not assigned to a group may have overlapping names and IDs (including VLANs which belong to a common site). For example, you can create two VLANs with ID 123, but they cannot both be assigned to the same group.
