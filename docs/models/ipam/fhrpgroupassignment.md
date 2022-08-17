# FHRP Group Assignments

Member device and VM interfaces can be assigned to [FHRP groups](./fhrpgroup.md) to indicate their participation in maintaining a common virtual IP address (VIP). For instance, three interfaces, each belonging to a different router, may each be assigned to the same FHRP group to serve a shared VIP. Each of these assignments would typically receive a different priority.

Interfaces are assigned to FHRP groups under the interface detail view.

## Fields

### Group

The [FHRP group](./fhrpgroup.md) being assigned.

### Interface

The device or VM interface to which the group is being assigned.

### Priority

A value between 0 and 255 indicating the interface's priority for being elected as the master/primary node in the group.
